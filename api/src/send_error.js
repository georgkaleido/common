const logger = require("kaleido-api/logger");

function sendError(res, status, errorTitle, details={}) {
  res.status(status);
  var errorJson =  {
    errors: [
      {
        title: errorTitle,
        ...details
      }
    ]
  };
  res.json(errorJson);
  res.end();
  logger.info(`[${res.locals.requestId}]   Returned error message: ${errorTitle}`);
}

module.exports = sendError;
