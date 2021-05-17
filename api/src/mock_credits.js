const logger = require("kaleido-api/logger");

class MockCredits {
  hasRecentlyFetched() {
    return true;
  }

  getUser(user_id, correlationId, tries = 5, tryDelayMs = 500) {
    return {
      free_api_calls: 1000,
      mcredits_monthly: 1000000,
      mcredits: 1000000,
      mcredits_enterprise: 1000000,
      mcredits_enterprise_overdraft_limit: 1000000,
      enterprise: true,
      api_requests_per_minute: 1000000,
      improvement_api_requests_per_day: 0,
    };
  }

  getMaxSize(user) {
    return "full";
  }

  check(api, user_id, user, correlationId, callbacks = {}) {
    callbacks.success({
      charge: () => {
        return {
          credits_charged: 0,
        };
      }
    });
  }
}

module.exports = MockCredits;
