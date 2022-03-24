const logger = require("kaleido-api/logger");

const ApiCall = require("./api_call");

const request = require('request');

// this pool object needs to be global to have an effect according to https://www.npmjs.com/package/request
const httpPool = {
  maxSockets: 6,
};

class RemoteCredits {
  constructor(callback) {
    this.connect(callback);
  }

  connect(callback) {
    logger.info("Remote users-api - connecting ...")
    this.remote("/health", 'api-server-startup-health').then(() => {
      logger.info("Remote users-api - connected.")
      callback();
    }).catch(() => {
      // retry in a few seconds
      setTimeout(() => this.connect(callback), 5000);
    })
  }

  hasRecentlyFetched() {
    return true;
  }

  remote(path, correlationId, params = {}) {
    const profiler = logger.startTimer();
    return new Promise((resolve, reject) => {
      request({
        url: `${process.env.USERS_API_URL}${path}`,
        auth: {
          user: process.env.USERS_API_USER,
          pass: process.env.USERS_API_PASSWORD,
        },
        headers: {
          'Content-Type': 'application/json',
          'X-Correlation-ID': correlationId,
        },
        timeout: 5000,
        pool: httpPool,
        forever: true,
        strictSSL: false,
        ...params,
      },
      (error, response, body) => {
        profiler.done({message: `[${correlationId}] Remote users-api - request time`});

        if(error) {
          logger.warn(`[${correlationId}] Remote users-api - error: Connection ${error}`);
          reject();
          return;
        }

        resolve({ response, body });
      })
    });
  }

  getUser(user_id, correlationId, tries = 5, tryDelayMs = 500) {
    return new Promise((resolve, reject) => {
      this.getUserOnce(user_id, correlationId).then((user) => {
        resolve(user);
      }).catch((e) => {
        if(e.retryable && tries > 0) {
          setTimeout(() => {
            this.getUser(user_id, correlationId, tries - 1, tryDelayMs * 2).then(resolve).catch(reject);
          }, tryDelayMs);
        }
        else {
          reject(e);
        }
      });
    })
  }

  getUserOnce(user_id, correlationId) {
    return new Promise((resolve, reject) => {
      this.remote(`/v1.0/users/${user_id}`, correlationId).then(({response, body}) => {
        if(response.statusCode == 200) {
          try {
            var json = JSON.parse(body);
            resolve(json.data.attributes);
          }
          catch(e) {
            logger.warn(`[${correlationId}] Remote users-api - error: JSON ${e}`);
            reject({code: 'json_parse_error', retryable: true});
          }
        }
        else if(response.statusCode == 422) {
          // user not found
          reject({code: 'user_not_found'});
        }
        else {
          reject({code: `status_code_${response.statusCode}`, retryable: true});
        }
      }).catch(() => {
        reject({code: 'request_error', retryable: true});
      });
    })
  }

  getMaxSize(user) {
    var mcredits_spendable = user.mcredits_monthly + user.mcredits;
    if(user.enterprise) {
      mcredits_spendable += user.mcredits_enterprise + user.mcredits_enterprise_overdraft_limit;
    }
    if(mcredits_spendable >= 1000) return "full";
    return "preview";
  }

  check(api, user_id, user, correlationId, callbacks = {}, api_key_id = null) {
    var call = new ApiCall(api);

    var availableMcredits = user.mcredits_monthly + user.mcredits;
    if(user.enterprise) {
      availableMcredits += user.mcredits_enterprise + user.mcredits_enterprise_overdraft_limit;
    }

    if(user.free_api_calls > 0 && call.canBeFree() || availableMcredits >= call.requiredMCredits) {
      callbacks.success({
        charge: (resolution) => {
          var mcreditsCharged = null;
          call.updateForResolution(resolution);
          if(user.free_api_calls > 0 && call.canBeFree()) {
            this.report(correlationId, call.api, user_id, 1, 0, 0, 0, api_key_id);
            mcreditsCharged = 0;
          }
          else {
            var charge = this.distributeCharge(user, call.requiredMCredits);
            this.report(correlationId, call.api, user_id, 0, ...charge, api_key_id);
            mcreditsCharged = call.requiredMCredits;
          }
          return {
            credits_charged: (mcreditsCharged != null ? mcreditsCharged / 1000 : null)
          };
        }
      });
    }
    else {
      callbacks.missing_credits();
    }
  }

  report(correlationId, api, user_id, free_api_calls, mcredits_monthly, mcredits, mcredits_enterprise, api_key_id) {
    var data = {
      action: api,
      free_api_calls: free_api_calls,
      mcredits_monthly: mcredits_monthly,
      mcredits: mcredits,
      mcredits_enterprise: mcredits_enterprise,
      api_key_id: api_key_id,
    };

    this.remote(
      `/v1.0/users/${user_id}/charge`,
      correlationId,
      {
        method: 'POST',
        json: data
      }
    ).then(({ response, body }) => {
      if(response.statusCode != 200) {
        logger.warn(`[${correlationId}] Remote users-api - error: Failed to report credit usage (HTTP status ${response.statusCode}) for user ${user_id}: data ${JSON.stringify(data)}`);
      }
      // ok
    }).catch(() => {
      logger.warn(`[${correlationId}] Remote users-api - error: Failed to report credit usage (Connection) for user ${user_id}: data ${JSON.stringify(data)}`);
    });
  }

  distributeCharge(credits, amount) {
    var remaining = amount;

    var charge_mcredits_monthly_max = credits.mcredits_monthly > 0 ? credits.mcredits_monthly : 0;
    var charge_mcredits_monthly = remaining < charge_mcredits_monthly_max ? remaining : charge_mcredits_monthly_max;
    remaining -= charge_mcredits_monthly;

    var charge_mcredits_max = credits.mcredits > 0 ? credits.mcredits : 0;
    var charge_mcredits = remaining < charge_mcredits_max ? remaining : charge_mcredits_max;
    remaining -= charge_mcredits;

    var charge_mcredits_enterprise = 0;
    if(credits.enterprise) {
      var max_available_enterprise = credits.mcredits_enterprise + credits.mcredits_enterprise_overdraft_limit;
      var charge_mcredits_enterprise_max = max_available_enterprise > 0 ? max_available_enterprise : 0;
      charge_mcredits_enterprise = remaining < charge_mcredits_enterprise_max ? remaining : charge_mcredits_enterprise_max;
      remaining -= charge_mcredits_enterprise;
    }

    return [charge_mcredits_monthly, charge_mcredits, charge_mcredits_enterprise];
  }
}

module.exports = RemoteCredits;
