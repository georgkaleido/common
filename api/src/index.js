const logger = require("kaleido-api/logger");
require("dotenv").config()

if(process.env.NODE_ENV == "development") {
  const mockery = require("mockery")
  mockery.enable({
    warnOnUnregistered: false
  })
  mockery.registerSubstitute("kaleido-api/core", "./mock/core_mock")
}

const https = require('https');
const http = require('http');
const fs = require('fs');
const express = require('express');
const fileUpload = require('express-fileupload');
const bodyParser = require("body-parser");
const cors = require('cors');
const Validation = require("./validation")
const validUrl = require('valid-url');
const createHttpTerminator = require('http-terminator').createHttpTerminator;

const TokenAuth = require('./token_auth');
const KeyAuth = require('./key_auth');
const Db = require("kaleido-api/db");
const MockCredits = require('./mock_credits');
const RemoteCredits = require('./remote_credits');
const Design = require('./design');
const sendError = require('./send_error');
const shutdown = require("kaleido-api/shutdown");
const Core = require("kaleido-api/core");
const RequestId = require("kaleido-api/request_id");
const download = require("kaleido-api/download");
const ratelimit = require("kaleido-api/rate_limit");

const namedColors = require('color-name');
const hexRgb = require('hex-rgb');
const remoteIp = require("kaleido-api/remote_ip");
const ipRangeCheck = require("ip-range-check");
const { Improve, applyImproveRateLimit} = require("./improve");

const apiPort = process.env.API_PORT || 9443
const useSSL = toBoolean(process.env.API_SSL || true) 
                && process.env.API_SSL_KEY 
                && process.env.API_SSL_CRT
const maxFileSize = 12*1024*1024;


function toBoolean(value) {
  if (null !== value) {
    let t = typeof value;
    if ("undefined" !== typeof value) {
      if ("string" !== t) return !!value;
      value = value.toLowerCase().trim();
      return "true" === value || "yes" === value || "1" === value;
    }
  }
  return false;
}

function startServer() {
  const app = express()
  app.disable('x-powered-by');
  app.use(withRequestId);
  app.use(fileUpload());
  app.use(bodyParser.urlencoded({extended: false, limit: maxFileSize}));
  app.use(bodyParser.json({limit: maxFileSize}));
  app.use(logParams);

  app.get('/', (req, res) => {
    res.type('txt');
    res.send("Welcome to the remove.bg API. Find the docs at remove.bg/api!")
  });

  app.get('/robots.txt', cors(), (req, res) => {
    res.type('txt');
    res.send("User-agent: *\nDisallow: /\n");
  });

  function getHealthStatus() {
    var status = "ok";
    if(!core.isConnected()) status = "no-amqp-connection";
    if(!credits.hasRecentlyFetched()) status = "no-recent-fetch";
    if(shutdown.isInProgress()) status = "shutting-down";
    return status;
  }

  function healthCheck(res, ...goodStates) {
    var status = getHealthStatus();
    if(!goodStates.includes(status)) {
      res.status(500);
    }
    res.type('txt');
    res.send(`health:${status}`)
    logger.info(`[${res.locals.requestId}]   API Health: ${status}`)
  }

  app.get('/health', (req, res) => healthCheck(res, "ok"));
  app.get('/health/readiness', (req, res) => healthCheck(res, "ok"));
  app.get('/health/liveness', (req, res) => healthCheck(res, "ok", "shutting-down"));

  app.options('/v1.0/removebg', cors());
  app.post('/v1.0/removebg', cors(), authenticated, authScope("removebg:process"), (req, res) => {
    var wrapperFormat = (req.headers["accept"] == "application/json" ? "json" : "binary");
    prepare(req, res, wrapperFormat);
  });

  app.options('/v1.0/removebg.json', cors());
  app.post('/v1.0/removebg.json', cors(), authenticated, authScope("removebg:process"), (req, res) => {
    logger.info("[${res.locals.requestId}]   DEPRECATED: Endpoint /v1.0/removebg.json");
    prepare(req, res, "json");
  })

  app.options('/v1.0/apps/:name', cors());
  app.get('/v1.0/apps/:name', cors(), (req, res) => {
    logger.info(`[${res.locals.requestId}]   App: ${req.params.name} / Version: ${req.query.v}`);
    
    // All OK:            res.json({"status": "ok"});
    // Optional update:   res.json({"status": "warning", "message": "Thanks for testing remove.bg for Adobe Photoshop. Feedback? team@remove.bg"});
    // Required update:   res.json({"status": "error", "message": "This plugin is no longer supported. Please update at www.remove.bg/photoshop"});

    switch(req.params.name) {
      case "photoshop":
        // req.query.v == "1.0.0"
        // req.query.v == "1.0.1"
        if (req.query.v.split('.')[0]=="1") { // send warning nudge to all users of CEP plugin
          res.json({"status": "warning", "message": "<b>⚠️ This plugin is outdated</b><br>Learn how to upgrade to the new version in the FAQ section. www.remove.bg/photoshop"});
        } else {
          res.json({"status": "ok"});
        }
        break;
      case "desktop":
        // req.query.v == "1.0.0"
        res.json({"status": "ok"});
        break;
      case "android":
        if(req.query.v == "0.1.0") {
          res.json({"status": "error", "message": "This app is no longer supported. Please update via the Google Play Store."});
        }
        else if(req.query.v == "0.2.0") {
          res.json({"status": "warning", "message": "You are using an outdated app version. Please update via the Google Play Store."});
        }
        else {
          res.json({"status": "ok"});
        }
        break;
      default:
        res.json({"status": "error", "message": "Unknown app (if this is an unexpected error, please contact team@remove.bg)"});
    }

    res.end();
  });

  if(process.env["SKIP_DB"] != "1") {
    app.options('/v1.0/account', cors());
    app.get('/v1.0/account', cors(), authenticated, authScope("user:read"), (req, res) => {
      var user_id = res.locals.user_id;
      var user = res.locals.user;
      var balance = {
        subscription: user.mcredits_monthly,
        payg: user.mcredits,
        enterprise: (user.enterprise ? user.mcredits_enterprise : 0),
      };
      balance.total = balance.subscription + balance.payg + balance.enterprise;

      res.json(
        {
          "data": {
            "attributes": {
              credits: {
                subscription: (balance.subscription / 1000),
                payg: (balance.payg / 1000),
                enterprise: (balance.enterprise / 1000),
                total: (balance.total / 1000),
              },
              api: {
                free_calls: user.free_api_calls,
                sizes: "all",
              },
            }
          }
        }
      );
      res.end();
    });

    app.options('/v1.0/designs', cors());
    app.get('/v1.0/designs', cors(), authenticated, authScope("user:read"), (req, res) => {
      applyRateLimit(res, 1000000).then(() => Design.index(db, req, res));
    });

    app.options('/v1.0/designs/:id', cors());
    app.get('/v1.0/designs/:id', cors(), authenticated, authScope("user:read"), (req, res) => {
      applyRateLimit(res, 1000000).then(() => Design.show(db, req, res));
    });
  }

  if(process.env["SKIP_IP"] != "1") {
    app.options('/v1.0/improve', cors());
    app.post('/v1.0/improve', cors(), authenticated, authScope("removebg:process"), (req, res) => {
      applyImproveRateLimit(res).then(() => Improve.process(req, res))
    })
  }

  app.use(errorHandler);

  const serverType = useSSL ? "HTTPS" : "HTTP"
  const serverOptions = useSSL ? {
    key: fs.readFileSync(process.env.API_SSL_KEY),
    cert: fs.readFileSync(process.env.API_SSL_CRT),
    passphrase: process.env.API_SSL_PASS,
  } : {}

  const server = useSSL ? 
    https.createServer(serverOptions, app) :
    http.createServer(serverOptions, app)
  
  server.listen(apiPort, () => logger.info(`remove bg API listening on ${serverType} port ${apiPort}!`));

  var httpTerminator = createHttpTerminator({
    server,
    gracefulTerminationTimeout: 10000
  });

  // Google Cloud HTTPS Load Balancer requires a keep-alive timeout of 600+ seconds
  // See here: https://cloud.google.com/load-balancing/docs/https#timeouts_and_retries
  // And here: https://cloud.google.com/load-balancing/docs/https/https-logging-monitoring#statusdetail_http_failure_messages
  server.keepAliveTimeout = 620*1000;
  // We also need to set headersTimeout > keepAliveTimeout
  // to fix this issue: https://github.com/nodejs/node/issues/27363
  server.headersTimeout = server.keepAliveTimeout + 1000;

  shutdown.before((callback) => {
    logger.info("Closing server...")
    httpTerminator.terminate().then(() => {
      logger.info("Server closed. Waiting a few more seconds to proceed shutdown to allow for persistence...")
      setTimeout(callback, 8000);
    });
  });
}

function prepare(req, res, wrapperFormat) {
  var user_id = res.locals.user_id;
  var user = res.locals.user;
  var size = getSize(req, user);
  checkBalance(user_id, size, req, res, (auth) => {
    var image_url = req.body.image_url;
    var image_file = req.files ? req.files.image_file : null;
    var image_file_b64 = req.body.image_file_b64;

    if(image_url && image_file || image_file && image_file_b64 || image_file_b64 && image_url) {
      return sendError(res, 400, "Multiple image sources given: Please provide either the image_url, image_file or image_file_b64 parameter.", { code: "multiple_sources" });
    }

    if(!image_url && !image_file && !image_file_b64) {
      return sendError(res, 400, "No image given", { code: "missing_source", detail: "Please provide the source image in the image_url, image_file or image_file_b64 parameter." });
    }

    if(image_url) {
      if(!validUrl.isWebUri(image_url)) {
        return sendError(res, 400, "Invalid image_url: Please provide a valid URL.", { code: "invalid_image_url" });
      }
    }

    var channels = getChannels(req);
    var type = getType(req);
    var typeLevel = getTypeLevel(req);
    var crop = getCrop(req);
    
    var format = getFormat(req);
    if(!format) {
      return sendError(res, 400, "Invalid format parameter given", { code: "invalid_format" });
    }
    
    var megapixels = 0.25;
    switch(size) {
      case "full":
        if(format == "zip" || format == "jpg") {
          megapixels = 25;
        }
        else {
          megapixels = 10;
        }
        break;
      case "hd": // legacy (before 06/2019)
        megapixels = 4;
        break;
      case "medium": // legacy (before 06/2019)
        megapixels = 1.5;
        break;
    }
    
    var roi = getRoi(req);
    if(roi == null) {
      return sendError(res, 400, "Invalid roi parameter given", { code: "invalid_roi" });
    }

    var semitransparency = getSemitransparency(req);
    if(semitransparency == null) {
      return sendError(res, 400, "Invalid semitransparency parameter given", { code: "invalid_semitransparency" });
    }
    
    var cropMargin = getCropMargin(req);
    if(cropMargin == null) {
      return sendError(res, 400, "Invalid crop_margin parameter given", { code: "invalid_crop_margin" });
    }

    var scale = getScale(req);
    if(scale == null) {
      return sendError(res, 400, "Invalid scale parameter given", { code: "invalid_scale" });
    }

    var position = getPosition(req);
    if(position == null) {
      return sendError(res, 400, "Invalid position parameter given", { code: "invalid_position" });
    }

    var bgColor = getBgColor(req);
    if(!bgColor) {
      return sendError(res, 400, "Invalid bg_color parameter given", { code: "invalid_bg_color" });
    }
    var bgColorVisible = bgColor[3] > 0;
    
    var bgImageUrl = req.body.bg_image_url;
    if(bgImageUrl && !validUrl.isWebUri(bgImageUrl)) {
      return sendError(res, 400, "Invalid bg_image_url: Please provide a valid URL.", { code: "invalid_bg_image_url" });
    }

    var bgImageFile = req.files ? req.files.bg_image_file : null;
    if(bgColorVisible && bgImageUrl || bgImageUrl && bgImageFile || bgImageFile && bgColorVisible) {
      return sendError(res, 400, "Multiple background sources given: Please provide either the bg_color, the bg_image_url or the bg_image_file parameter.", { code: "multiple_bg_sources" });
    }

    var addShadow = getAddShadow(req);

    var afterAllFetched = (originalData, backgroundData) => {
      validate(originalData, backgroundData, res, wrapperFormat, megapixels, type, channels, format, bgColor, roi, semitransparency, crop, cropMargin, scale, position, addShadow, auth, typeLevel);
    }

    var afterOriginalFetched = (originalData) => {
      if(bgImageUrl) {
        const profiler = logger.startTimer();
        download(bgImageUrl, maxFileSize, res.locals.requestId, (data) => {
          profiler.done({message: `[${res.locals.requestId}]   download-background-image`});
          afterAllFetched(originalData, data);
        }, (error) => {
          profiler.done({message: `[${res.locals.requestId}]   download-background-image`});
          logger.info(`[${res.locals.requestId}]   Fetch URL error: `, error);
          return sendError(res, 400, `Failed to download background image from given image_url: ${error}`, { code: "failed_bg_download" });
        });
      }
      else if(bgImageFile) {
        afterAllFetched(originalData, bgImageFile.data);
      }
      else {
        afterAllFetched(originalData, null);
      }
    };

    if(image_url) {
      const profiler = logger.startTimer();
      download(image_url, maxFileSize, res.locals.requestId, (data) => {
        profiler.done({message: `[${res.locals.requestId}]   download-image`});
        afterOriginalFetched(data);
      }, (error) => {
        profiler.done({message: `[${res.locals.requestId}]   download-image`});
        logger.info(`[${res.locals.requestId}]   Fetch URL error: `, error);
        return sendError(res, 400, `Failed to download image from given image_url: ${error}`, { code: "failed_image_download" });
      });
      return
    }

    if(image_file_b64) {
      image_file_b64 = image_file_b64.replace(/^data:image\/(png|jpeg);base64,/, '');
      afterOriginalFetched(Buffer.from(image_file_b64, "base64"));
      return
    }

    if(image_file) {
      afterOriginalFetched(image_file.data);
      return
    }
  });
}



function validate(data, backgroundData, res, wrapperFormat, megapixels, type, channels, format, bgColor, roi, semitransparency, crop, cropMargin, scale, position, addShadow, auth, typeLevel) {
  var dataValid = Validation.validateImageData(data);
  if(!dataValid.valid) {
    return sendError(res, 400, dataValid.message, { code: dataValid.code, detail: dataValid.detail });
  }

  res.locals.inputImageWidth = dataValid.width;
  res.locals.inputImageHeight = dataValid.height;

  if(backgroundData) {
    var bgDataValid = Validation.validateImageData(backgroundData);
    if(!bgDataValid.valid) {
      return sendError(res, 400, bgDataValid.message, { code: bgDataValid.code, detail: bgDataValid.detail });
    }
  }

  for(var point of roi) {
    if(point.x_relative) {
      point.x = Math.round(point.x / 100 * (dataValid.width - 1));
      point.x_relative = false;
    }
    else if(point.x > dataValid.width-1) {
      return sendError(res, 400, "ROI exceeds image bounds", { code: "roi_exceeds_bounds", detail: "The given roi parameter defines a region that exceeds the image bounds" });
    }
    if(point.y_relative) {
      point.y = Math.round(point.y / 100 * (dataValid.height - 1));
      point.y_relative = false;
    }
    else if(point.y > dataValid.height-1) {
      return sendError(res, 400, "ROI exceeds image bounds", { code: "roi_exceeds_bounds", detail: "The given roi parameter defines a region that exceeds the image bounds" });
    }
  }

  if(roi[0].x == roi[1].x || roi[0].y == roi[1].y) {
    return sendError(res, 400, "ROI region is empty", { code: "roi_region_empty", detail: "The given roi parameter defines an empty region" });
  }

  if(!core.isConnected()) {
    return sendError(res, 500, "Internal messaging connection error");
  }

  applyRateLimit(res, dataValid.width * dataValid.height).then(() => {
    logger.info(`[${res.locals.requestId}]   Input image: ${dataValid.width} x ${dataValid.height} / format ${dataValid.ext} / size ${data.length} bytes`)
    if(backgroundData) {
      logger.info(`[${res.locals.requestId}]   Background image: ${bgDataValid.width} x ${bgDataValid.height} / format ${bgDataValid.ext} / size ${backgroundData.length} bytes`)
    }

    var user = res.locals.user;
    if(user && user.enterprise) {
      var pixels = dataValid.width * dataValid.height;
      logger.info(`[${res.locals.requestId}]   Enterprise user ${res.locals.user_id}, input resolution ${pixels} px`)
    }
    
    processImage(data, backgroundData, res, wrapperFormat, megapixels, type, channels, format, bgColor, roi, semitransparency, crop, cropMargin, scale, position, addShadow, auth, typeLevel);
  }).catch(() => {
    // no-op
  });
}

function processImage(data, backgroundData, res, wrapperFormat, megapixels, type, channels, format, bgColor, roi, semitransparency, crop, cropMargin, scale, position, addShadow, auth, typeLevel) {
  var msg = {
    version: "1.0",
    command: "removebg",
    data: Buffer.from(data, 'binary'),
    megapixels: megapixels,
    channels: channels,
    format: format,
    bg_color: bgColor,
    bg_image: backgroundData,
    type: type,
    crop: crop,
    crop_margin: cropMargin,
    roi: [roi[0].x, roi[0].y, roi[1].x, roi[1].y],
    semitransparency: semitransparency,
    shadow: addShadow,
  }

  if(backgroundData) {
    msg.bg_image = Buffer.from(backgroundData, 'binary');
  }

  if(scale && scale != "original") {
    msg.scale = scale;
  }

  if(position && position != "original") {
    msg.position = position;
  }

  core.process(
    res.locals.requestId,
    msg,
    (result) => {
      try {
        if(result.status == "ok") {
          res.set('X-Width', result.width);
          res.set('X-Height', result.height);

          res.set('X-Max-Width', result.maxwidth);
          res.set('X-Max-Height', result.maxheight);

          if(typeLevel !== null) {
            res.set('X-Type', mapType(result.type, typeLevel));
          }

          if(result.type == 'car' && addShadow) {
            logger.info(`[${res.locals.requestId}]   Car shadow for ${res.locals.user_id}, shadow user agent: ${res.locals.user_agent}`);
          }
          
          var resolution = result.width_uncropped * result.height_uncropped;

          var data = Buffer.from(result.data, "binary");
          
          var chargeInfo = auth.charge(resolution);
          res.set('X-Credits-Charged', chargeInfo.credits_charged);

          var squarepx = result.width > 0 && result.height > 0 ? Math.round(Math.sqrt(result.width * result.height)) : 0;
          logger.info(`[${res.locals.requestId}]   Credits charged ${chargeInfo.credits_charged} / type ${result.type} / size ${result.width}x${result.height} (${squarepx} px^2)`)

          processedImageLog = [
            `[${res.locals.requestId}]`,
            "img-processed",
            res.locals.remoteIp,
            res.locals.user_id,
            res.locals.user_agent,
            res.locals.inputImageWidth,
            res.locals.inputImageHeight,
            result.width,
            result.height,
          ].join(",")
      
          logger.info(processedImageLog)

          if(wrapperFormat == "binary") {
            res.type(result.format.toString());
            res.end(data, "binary");
          }
          else {
            res.json({
              data: {
                result_b64: data.toString("base64")
              }
            })
            res.end()
          }
        }
        else {
          var error = "";
          if(result.description) {
            error = result.description.toString('utf8');
          }
          var details = { code: error };
          var httpCode = 400;
          switch(error) {
            case "unknown_foreground":
              error = "Could not identify foreground in image. For details and recommendations see https://www.remove.bg/supported-images.";
              break;
            case "unknown_error":
              httpCode = 500;
              error = "An unknown error happened. Sorry – please try again later.";
              break;
            case 'failed_to_read_image':
              error = 'There was an error reading the image.'
              break;
          }
          sendError(res, httpCode, error, details);
        }
      }
      catch(err) {
        logger.error("Failed to process image result: ", err);
        try {
          sendError(res, 500, "Internal response processing failed");
        }
        catch(err) {
          logger.error(`Failed to return HTTP status 500: ${err}`)
        }
      }
    }
  )
}

function mapType(type, typeLevel) {
  if(typeLevel == "latest") {
    return type;
  }

  var level1Mapping = {
    "car_interior": "car",
    "car_part": "car",
    "graphics": "other",
    "transportation": "other",
  }

  if(typeLevel == "1") { return (type in level1Mapping) ? level1Mapping[type] : type }
}

function errorHandler(err, req, res, next) {
  sendError(res, err.status || 500, err.message, err.details || {});
}

function withRequestId(req, res, next) {
  res.locals.requestId = RequestId.generate();

  var ip = remoteIp(req);
  res.locals.remoteIp = ip;
  logger.info(`[${res.locals.requestId}] Started ${req.method} ${req.path} for ${ip}`);

  var user_agent = req.headers['x-user-agent'] || req.headers['user-agent'];
  res.locals.user_agent = user_agent;
  logger.info(`[${res.locals.requestId}]   User Agent: ${user_agent}`);

  var started = new Date();
  res.on('finish', function() {
    var finished = new Date();
    logger.info(`[${res.locals.requestId}] Completed ${this.statusCode} in ${finished-started}ms`);
  })
  return next();
}

function logParams(req, res, next) {
  var params = [];
  if(req.body) {
    for(var paramName of Object.keys(req.body)) {
      var value = req.body[paramName];
      if(paramName == "image_url" && typeof(value) == "string" && value.length > 0) {
        params.push(`"${paramName}"="${value.substr(0, 7)}..." (${value.length} chars)`);
      }
      else {
        var limit = 100;
        if(typeof(value) == "string" && value.length > limit) {
          params.push(`"${paramName}"="${value.substr(0, limit)}..." (${value.length} chars)`);
        }
        else {
          params.push(`"${paramName}"="${value}"`);
        }
      }
    }
  }
  if(req.files) {
    for(var paramName of Object.keys(req.files)) {
      var value = req.files[paramName];
      params.push(`"${paramName}"=(${(value && value.data ? value.data.length : "null")} bytes)`);
    }
  }
  if(params.length > 0) {
    logger.info(`[${res.locals.requestId}]   Parameters: ${params.join(", ")}`);
  }
  return next();
}

var authenticated, authScope;
if(process.env["SKIP_AUTH"] == "1") {
  authenticated = function(req, res, next) {
    res.locals.user_id = "0";
    res.locals.user = {};
    next();
  }
  authScope = function(...requiredScopes) {
    return function(req, res, next) {
      next();
    }
  }
} else {
  authenticated = function(req, res, next) {
    var api_key = req.headers["x-api-key"];
    var api_key_given = api_key != null && api_key != undefined && api_key != "";

    var authorization = req.headers["authorization"];
    var authorization_given = authorization != null && authorization != undefined && authorization != "";

    if(api_key_given && authorization_given) {
      var err = new Error('Both Authorization and X-Api-Key header are present.');
      err.status = 403;
      err.details = {
        code: 'auth_failed',
        detail: "Please provide etiher the Authorization OR the X-Api-Key header, but not both."
      };
      return next(err);
    }

    if(!api_key_given && !authorization_given) {
      var err = new Error('Authorization failed');
      err.status = 403;
      err.details = {
        code: 'auth_failed',
        detail: "Please authorize by providing either the Authorization or the X-Api-Key request header."
      };
      return next(err);
    }

    function checkIP(user, ip_passlist) {
      var ip = res.locals.remoteIp;

      // 2020-11-06 block abusive IP
      if(ip == "103.130.182.2") {
        return false;
      }

      // currently an enterprise-only-feature
      if(!user.enterprise) return true;
      // unset passlist means: all IPs permitted
      if(ip_passlist == null || ip_passlist == undefined) return true;

      return ipRangeCheck(ip, ip_passlist);
    }

    function assignUser() {
      credits.getUser(res.locals.user_id, res.locals.requestId).then((user) => {
        if(checkIP(user, res.locals.key ? res.locals.key.ip_passlist : null)) {
          res.locals.user = user;
          next();
        }
        else {
          var err = new Error('IP Address unauthorized');
          err.status = 403;
          err.details = {
            code: 'ip_address_unauthorized',
            detail: "The client IP address is not authorized to use the given API key."
          };
          next(err);
        }
      }).catch((e) => {
        logger.info(`[${res.locals.requestId}]   Auth error: ${e.code}`);

        if(e.code == 'user_not_found') {
          var err = new Error('Authorization failed');
          err.status = 403;
          err.details = {
            code: 'auth_failed',
            detail: "User not found."
          };
          next(err);
        }
        else {
          var err = new Error('Internal auth error');
          err.status = 500;
          err.details = {
            code: 'internal_auth_error',
            detail: "Failed to authenticate user"
          };
          next(err);
        }
      })
    }

    if(api_key_given) {
      key_auth.fromApiKeyHeader(api_key).then((key) => {
        res.locals.key = key;
        res.locals.user_id = key.user_id;
        logger.info(`[${res.locals.requestId}]   User: ${res.locals.user_id} (via X-Api-Key)`);
        assignUser();
      }).catch((error) => {
        next(error);
      });
    } else { // authorization_given
      token_auth.fromAuthorizationHeader(authorization).then((token) => {
        res.locals.token = token;
        res.locals.user_id = token.resource_owner_id;
        logger.info(`[${res.locals.requestId}]   User: ${res.locals.user_id} (via OAuth2)`);
        assignUser();
      }).catch((error) => {
        next(error);
      });
    }
  }

  authScope = function(...requiredScopes) {
    return function(req, res, next) {
      if(res.locals.token) {
        res.locals.token.requireScopes(requiredScopes).then(() => next()).catch((msg) => {
          var err = new Error(msg);
          err.status = 403;
          err.details = { code: 'auth_failed' };
          next(err);
        });
      }
      else {
        next();
      }
    }
  }
}

function setSharedRateLimitHeaders(res, rateLimiterRes) {
  res.set("X-RateLimit-Remaining", rateLimiterRes.remainingPoints);
  res.set("X-RateLimit-Reset", Math.ceil((Date.now() + rateLimiterRes.msBeforeNext) / 1000));
}

if(process.env["SKIP_RATELIMIT"] == "1") {
  applyRateLimit = function(res, pixelCount) {
    return Promise.resolve();
  }
}
else {
  ratelimit.init();

  applyRateLimit = function(res, pixelCount) {
    var user_id = res.locals.user_id;
    var user = res.locals.user;
    var applicableRateLimit = user.api_requests_per_minute;

    if(!user.enterprise && user.mcredits_monthly <= 0 && user.mcredits <= 1000) {
      applicableRateLimit = 50;
    }

    res.set("X-RateLimit-Limit", applicableRateLimit);

    var megapixels = Math.ceil(pixelCount / 1000000);
    
    return new Promise((resolve, reject) => {
      ratelimit.per_minute('rbgapirl', user_id, applicableRateLimit, megapixels).then((rateLimiterRes) => {
        setSharedRateLimitHeaders(res, rateLimiterRes);
        resolve();
      }).catch((rateLimiterRes) => {
        setSharedRateLimitHeaders(res, rateLimiterRes);
        res.set("Retry-After", Math.ceil(rateLimiterRes.msBeforeNext / 1000));

        sendError(res, 429, `Rate limit exceeded`, { code: "rate_limit_exceeded" });
        reject();
      });
    });
  }
}

var validSizes = {
  small: true,
  medium: true,
  hd: true,
  preview: true,
  full: true
};

function checkBalance(user_id, size, req, res, callback) {
  if(!validSizes[size]) {
    return sendError(res, 400, "Invalid value for parameter 'size'", { code: "invalid_size" });
  }

  var channels = getChannels(req);
  if(channels != "rgba" && channels != "alpha") {
    return sendError(res, 400, "Invalid value for parameter 'channels'", { code: "invalid_channels" });
  }

  credits.check(
    `api_removebg_${size}`,
    user_id,
    res.locals.user,
    res.locals.requestId,
    {
      success: callback,
      missing_credits: () => {
        sendError(res, 402, `Insufficient credits`, { code: "insufficient_credits" });
      },
    }
  )
}

function getChannels(req) {
  var channels = req.body.channels;
  if(channels == undefined) channels = "rgba";
  return channels;
}

function getSize(req, user) {
  var size = req.body.size;
  if(size == undefined || size == "500px" || size == "regular" || size == "small") size = "preview";
  if(size == "4k") size = "full";
  if(size == "auto") {
    size = credits.getMaxSize(user);
  }
  return size;
}

function getType(req) {
  var type = req.body.type;
  switch(type) {
    case "person":
      return "person";
    case "product":
      return "product";
    case "car":
      return "car";
    case "auto":
      return "auto";
    default:
      return "auto";
  }
}

function getTypeLevel(req) {
  switch(req.body.type_level) {
    case "none":
      return null;
    case "1":
      return "1";
    case "2":
      return "latest";
    case "latest":
      return "latest";
    default:
      return "1";
  }
}

function getCrop(req) {
  var crop = req.body.crop;
  switch(typeof(crop)) {
  case "boolean":
    return crop;
  case "number":
    return crop == 1;
  case "string":
    return crop == "true" || crop == "1";
  default:
    return false;
  }
}

function getAddShadow(req) {
  var add_shadow = req.body.add_shadow;
  switch(typeof(add_shadow)) {
  case "boolean":
    return add_shadow;
  case "number":
    return add_shadow == 1;
  case "string":
    return add_shadow == "true" || add_shadow == "1";
  default:
    return false;
  }
}

const cropMarginFormat = /^([0-9]{1,5})((%|px)?)([ ,]([0-9]{1,5})((%|px)?)([ ,]([0-9]{1,5})((%|px)?)([ ,]([0-9]{1,5})((%|px)?))?)?)?$/;
function getCropMargin(req) {
  var crop_margin = req.body.crop_margin;
  if(!crop_margin) return {
    top: 0,       top_relative: false,
    right: 0,   right_relative: false,
    bottom: 0, bottom_relative: false,
    left: 0,     left_relative: false,
  };
  if(typeof(crop_margin) != "string") return null;
  var match = cropMarginFormat.exec(crop_margin);
  if(!match) return null;

  var vals = [match[1], match[5], match[9], match[13]].filter((val) => val != undefined).map((val) => parseInt(val));
  var vals_relative = [match[2], match[6], match[10], match[14]].filter((val) => val != undefined).map((val) => val == '%');

  for(var i = 0; i < vals.length; i++) {
    if(vals[i] < 0) return null;
    if(vals_relative[i]) {
      if(vals[i] > 50) return null;
    }
    else {
      if(vals[i] > 500) return null;
    }
  }

  switch(vals.length) {
    case 1:
      return {
        top: vals[0],       top_relative: vals_relative[0],
        right: vals[0],   right_relative: vals_relative[0],
        bottom: vals[0], bottom_relative: vals_relative[0],
        left: vals[0],     left_relative: vals_relative[0],
      };
    case 2:
      return {
        top: vals[0],       top_relative: vals_relative[0],
        right: vals[1],   right_relative: vals_relative[1],
        bottom: vals[0], bottom_relative: vals_relative[0],
        left: vals[1],     left_relative: vals_relative[1],
      };
    case 4:
      return {
        top: vals[0],       top_relative: vals_relative[0],
        right: vals[1],   right_relative: vals_relative[1],
        bottom: vals[2], bottom_relative: vals_relative[2],
        left: vals[3],     left_relative: vals_relative[3],
      };
    default:
      return null;
  }
}

const scaleFormat = /^([0-9]{1,3})%$/;
function getScale(req) {
  var scale = req.body.scale;
  if(!scale || scale == "original") return "original";
  if(typeof(scale) != "string") return null;
  var match = scaleFormat.exec(scale);
  if(!match) return null;

  var val = parseInt(match[1]);
  if(val < 10 || val > 100) return null;

  return val;
}

const positionFormat = /^([0-9]{1,3})%([ ,]([0-9]{1,3})%)?$/;
function getPosition(req) {
  var position = req.body.position;
  if(!position || position == "original") return "original";
  if(typeof(position) != "string") return null;
  if(position == "center") return { x: 50, y: 50 };
  var match = positionFormat.exec(position);
  if(!match) return null;

  var vals = [match[1], match[3]].filter((val) => val != undefined).map((val) => parseInt(val));

  for(var i = 0; i < vals.length; i++) {
    if(vals[i] < 0 || vals[i] > 100) return null;
  }

  switch(vals.length) {
    case 1:
      return { x: vals[0], y: vals[0] };
    case 2:
      return { x: vals[0], y: vals[1] };
    default:
      return null;
  }
}

const roiFormat = /^([0-9]{1,5})((%|px)?)[ ,]([0-9]{1,5})((%|px)?)[ ,]([0-9]{1,5})((%|px)?)[ ,]([0-9]{1,5})((%|px)?)$/;
function getRoi(req) {
  var roi = req.body.roi;
  if(!roi) return [
    {x: 0, x_relative: true, y: 0, y_relative: true},
    {x: 100, x_relative: true, y: 100, y_relative: true},
  ];
  if(typeof(roi) != "string") return null;
  var match = roiFormat.exec(roi);
  if(!match) return null;
  var x1 = parseInt(match[1]);
  var x1_relative = match[2] == '%';
  var y1 = parseInt(match[4]);
  var y1_relative = match[5] == '%';
  var x2 = parseInt(match[7]);
  var x2_relative = match[8] == '%';
  var y2 = parseInt(match[10]);
  var y2_relative = match[11] == '%';
  if(x1_relative && x1 > 100 || y1_relative && y1 > 100 || x2_relative && x2 > 100 || y2_relative && y2 > 100) return null;
  return [
    { x: x1, x_relative: x1_relative, y: y1, y_relative: y1_relative },
    { x: x2, x_relative: x2_relative, y: y2, y_relative: y2_relative },
  ];
}

function getSemitransparency(req) {
  var semitransparency = req.body.semitransparency;
  if(semitransparency == undefined) {
    return true;
  }
  switch(typeof(semitransparency)) {
  case "boolean":
    return semitransparency;
  case "number":
    return semitransparency == 1;
  case "string":
    return semitransparency == "true" || semitransparency == "1";
  default:
    return null;
  }
}

function getFormat(req) {
  var format = req.body.format;
  if(!format) return "auto";
  switch(format) {
    case "jpg":
      return "jpg";
    case "png":
      return "png";
    case "zip":
      return "zip";
    case "auto":
      return "auto";
    default:
      return null;
  }
}

function getBgColor(req) {
  var bgColor = req.body.bg_color;
  if(!bgColor) return [255, 255, 255, 0];
  var named = namedColors[bgColor];
  if(named) {
    return [...named, 255];
  }
  try {
    var fromHex = hexRgb(bgColor);
    if(fromHex) {
      return [fromHex.red, fromHex.green, fromHex.blue, Math.round(fromHex.alpha*255)];
    }
  }
  catch(e) {
    return null;
  }
}

var db, token_auth, key_auth;
if(process.env["SKIP_DB"] != "1") {
  var db = new Db();
  var token_auth = new TokenAuth(db);
  var key_auth = new KeyAuth(db);
}

var core = new Core({
  onFirstConnect: startServer,
  monitoringUnit: 'images',
  waitForHealth: true,
});

var credits;

if(process.env["SKIP_AUTH"] == "1") {
  credits = new MockCredits();
  core.connect();
}
else {
   credits = new RemoteCredits(() => {
    core.connect();
  });
}
