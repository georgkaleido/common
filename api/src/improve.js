const logger = require("kaleido-api/logger")
const sendError = require("./send_error")
const Danni = require("kaleido-api/danni")
const validUrl = require("valid-url")
const download = require("kaleido-api/download")
const remoteIp = require("kaleido-api/remote_ip")
const ratelimit = require("kaleido-api/rate_limit")
const Validation = require("./validation")
const url = require("url")
const path = require("path")

const maxFileSize = 12*1024*1024
const rateLimitUser = 100
const rateLimitEnterprise = 1000

const Improve = {
  process: (req, res) => {
    let image_url = req.body.image_url
    let image_file = req.files ? req.files.image_file : null
    let image_file_b64 = req.body.image_file_b64
    let image_filename = req.body.image_filename
    let tag = req.body.tag
  
    validateImageInput(image_url, image_file_b64, image_file, res)
    if (res.headersSent) {
      // Input validation failed
      return
    }
  
    const imageFetched = (image, detected_filename) => {
      var dataValid = Validation.validateImageData(image);
      if(!dataValid.valid) {
        return sendError(res, 400, dataValid.message, { detail: dataValid.detail });
      }

      const danni = new Danni({
          user: process.env.DANNI_USER,
          password: process.env.DANNI_PASSWORD,
          host: process.env.DANNI_HOST
      })
      
      const image_b64 = Buffer.from(image).toString("base64")
      const filename = (image_filename && image_filename.length > 0) ? image_filename : detected_filename
      
      const payload = {
        "image": image_b64,
        "name": filename,
        "tag": tag,
      }
  
      let source =  {
        "user_id": res.locals.user_id,
        "ip_address": remoteIp(req),
      }
  
      danni.submit(payload, source).then((response) => {
        logger.info(`[${res.locals.requestId}]   Image ${response["id"]} submitted to Danni.`)
        res.json({ id: response["id"] })
        res.end()
      }).catch((error) => {
        logger.info(`[${res.locals.requestId}]   Image ${filename}, submitted by ${res.locals.user_id}, could not be submitted to Danni. (${error})`)
        sendError(res, 500, error)
      })
    }
  
    fetchImage(image_url, image_file_b64, image_file, res, imageFetched)
  }
}

function validateImageInput(image_url, image_file_b64, image_file, res) {
  if(image_url && image_file || image_file && image_file_b64 || image_file_b64 && image_url) {
    return sendError(res, 400, "Multiple image sources given: Please provide either the image_url, image_file or image_file_b64 parameter.");
  }

  if(!image_url && !image_file && !image_file_b64) {
    return sendError(res, 400, "No image given", { detail: "Please provide the source image in the image_url, image_file or image_file_b64 parameter." });
  }

  if(image_url) {
    if(!validUrl.isWebUri(image_url)) {
      return sendError(res, 400, "Invalid image_url: Please provide a valid URL.");
    }
  }
}

function fetchImage(image_url, image_file_b64, image_file, res, callback) {
  if(image_url) {
    const profiler = logger.startTimer();
    const filename = path.basename(url.parse(image_url).pathname)

    download(image_url, maxFileSize, res.locals.requestId, (data) => {
      profiler.done({message: `[${res.locals.requestId}]   download-image`});
      callback(data, filename)
    }, (error) => {
      profiler.done({message: `[${res.locals.requestId}]   download-image`});
      logger.info(`[${res.locals.requestId}]   Fetch URL error: `, error);
      return sendError(res, 400, `Failed to download image from given image_url: ${error}`);
    });
    return
  }

  if(image_file_b64) {
    image_file_b64 = image_file_b64.replace(/^data:image\/(png|jpeg);base64,/, "");
    callback(Buffer.from(image_file_b64, "base64"), "unnamed");
    return
  }

  if(image_file) {
    callback(image_file.data, image_file.name)
    return
  }
}

function setSharedRateLimitHeaders(res, rateLimiterRes) {
  res.set("X-RateLimit-Remaining", rateLimiterRes.remainingPoints);
  res.set("X-RateLimit-Reset", Math.ceil((Date.now() + rateLimiterRes.msBeforeNext) / 1000));
}

function applyImproveRateLimit(res) {
  const user_id = res.locals.user_id
  const user = res.locals.user
  const applicableRateLimit = user.improvement_api_requests_per_day;
 
  return new Promise((resolve, reject) => {
    ratelimit.per_day("improverl", user_id, applicableRateLimit, 1).then((rateLimiterRes) => {
      setSharedRateLimitHeaders(res, rateLimiterRes);
      resolve()
    }).catch((rateLimiterRes) => {
      setSharedRateLimitHeaders(res, rateLimiterRes);
      res.set("Retry-After", Math.ceil(rateLimiterRes.msBeforeNext / 1000))

      sendError(res, 429, "Rate limit exceeded", { code: "rate_limit_exceeded" })
      reject()
    })
  })
}

module.exports = { Improve, applyImproveRateLimit }
