const logger = require("kaleido-api/logger");

const actions = require("kaleido-api/removebg_actions");

class ApiCall {
  constructor(api) {
    this.setApi(api);
  }

  setApi(api) {
    this.api = api;
    this.action = actions[api];
    this.requiredMCredits = this.action.mcredits;
  }

  updateForResolution(resolution) {
    if(this.action.min_resolution && resolution < this.action.min_resolution) {
      this.setApi(this.action.min_resolution_alternative);
      this.updateForResolution(resolution);
    }
  }

  canBeFree() {
    return this.action.canBeFree;
  }
}

module.exports = ApiCall;
