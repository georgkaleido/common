const log = require("kaleido-api/modern_logger");

class MockRemoteCredits {
  constructor(callback) {
    log.info("Created mocked remote credits");
    this.connect(callback);
  }
  connect(callback) {
   log.info("Mocked Remote users-api - connecting");
   callback();
  }

  hasRecentlyFetched() {
    return true;
  }

  getUser(user_id, correlationId, tries = 5, tryDelayMs = 500) {
    return new Promise((resolve, reject) => {
      resolve({
        id: "abcd",
        free_api_calls: 100,
        mcredits_monthly: 100,
        mcredits: 100,
        mcredits_enterprise: 100,
        mcredits_enterprise_overdraft_limit: 100,
        enterprise: true,
        api_requests_per_minute: 100,
        improvement_api_requests_per_day: 100,
        last_fetch_date: Date.now(),
      })
    })
  }

  getMaxSize(user) {
   return "full";
  }

  check(api, user_id, user, correlationId, callbacks = {}) {
    callbacks.success({
      charge: (resolution) => {
        return {
          credits_charged: null
        }
      }
    })
  }

  report(correlationId, api, user_id, free_api_calls, mcredits_monthly, mcredits, mcredits_enterprise) {
    return true
  }

  distributeCharge(credits, amount) {
    return [0, 0, 0];
  }
}

module.exports = MockRemoteCredits;
