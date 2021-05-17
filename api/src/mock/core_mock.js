const logger = require("kaleido-api/logger")

class CoreMock {
  constructor(opts={}) {
    this.pending = {}
    this.processed = 0

    if(opts.onFirstConnect) {
      this.onFirstConnect = opts.onFirstConnect
    }
    logger.info("Created mocked core")
  }

  async connect() {
    if(this.onFirstConnect) {
      this.onFirstConnect()
      this.onFirstConnect = null
    }
    
    logger.info("Mocked core connected")
    return true
  }

  process(request_id, msg, callback, opts = {}) {
    logger.info(`[${request_id}]   Sending to mock core... `)

    this.pending[request_id] = {
      started: new Date(),
      callback: callback,
      counts: ('counts' in opts ? opts.counts : true),
      body: msg.data,
    }

    this.handleResponse({ "properties": { "correlationId": request_id }})
  }

  handleResponse(msg) {
    var request_id = msg.properties.correlationId
    var request = this.pending[request_id]

    if(request) {
      logger.info(`[${request_id}]   Received from mock core (took ${new Date() - request.started} ms).`)
      let result = null

      if(process.env.API_SERVICE == 'removebg') {
        result = this.removebgResponse(msg, request)
      } else {
        result = this.unscreenResponse(msg, request)
      }

      request.callback(result)

      if(request.counts) {
        this.processed += 1
      }
      delete this.pending[request_id]
    } else {
      logger.error(`[${request_id}]   Could not find pending request for ID`)
    }
  }

  removebgResponse(msg, request) {
    return {
      status: "ok",
      format: "image/png",
      width: 800,
      height: 600,
      maxwidth: 1920,
      maxheight: 1090,
      width_uncropped: 800,
      height_uncropped: 600,
      type: "other",
      data: request.body
    }
  }

  unscreenResponse(msg, request) {
    return {
      status: "ok",
      description: "Mocked response",
      data: request.body
    }
  }

  isConnected() {
    return true
  }
 }

 module.exports = CoreMock
