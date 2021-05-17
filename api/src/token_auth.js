const logger = require("kaleido-api/logger");

const Redis = require('ioredis');

const hitTTL = 60 * 3; // how long to cache tokens that exist (in seconds)
const missTTL = 60 * 10; // how long to cache tokens that do not exist (in seconds)
const sqlFetchInterval = 100; // in what interval to batch-query the SQL db for token (in milliseconds)

// once less than this fraction of the total hit cache TTL is left, try refreshing the cache before it expires
// e.g. a value of 0.3 means that once 70% of the TTL has passed, and another request comes in, the
// cache entry will be asynchronously updated in the background.
// the min and max values define a range, and within that a random value is picked to improve currency behaviour.
const refreshAheadHitTTLFactorMax = 0.3;
const refreshAheadHitTTLFactorMin = 0.1;

const Token = require("./token");

class TokenAuth {
  constructor(db) {
    this.db = db;
    this.lookups = {};
    this.redis = new Redis(process.env.REDIS_URL);
    this.pendingDbFetches = [];

    setInterval(() => {
      this.fetchFromDb();
    }, sqlFetchInterval);
  }

  fromAuthorizationHeader(header) {
    header = String(header);

    // a token length of 10-100 characters is just an arbitrarily set, reasonable boundary
    // that should not be too strict but it's not based on any specific spec as of 2020-05-22
    var authRegexp = /^Bearer (.{10,100})$/;
    var authMatch = authRegexp.exec(header);
    if(authMatch) {
      var token = authMatch[1];
      return this.fromToken(token);
    }
    else {
      return new Promise((_resolve, reject) => {
        var err = new Error("Auth token invalid");
        err.status = 403;
        err.details = { code: 'auth_failed' };
        reject(err);
      });
    }
  }

  fromToken(token) {
    return new Promise((resolve, reject) => {
      this.fetchTokenOnce(token).then((tokenObj) => {
        if(tokenObj.isAcceptable()) {
          resolve(tokenObj);
        }
        else {
          var err = new Error(tokenObj.toError());
          err.status = 403;
          err.details = { code: 'auth_failed' };
          reject(err);
        }
      }).catch(reject);
    })
  }

  fetchTokenOnce(token) {
    if(!(token in this.lookups)) {
      this.lookups[token] = this.fetchToken(token).finally(() => {
        delete this.lookups[token];
      });
    }
    return this.lookups[token];
  }

  fetchToken(token) {
    return new Promise((resolve, reject) => {
      this.redis.get(this.cacheKey(token), (err, result) => {
        if(err) {
          logger.info("Redis error while getting token:", err);
          return reject(this.internalError());
        }
        if(result == null) {
          this.handleCacheMiss(token).then(resolve).catch(reject);
        }
        else {
          try {
            var tokenObj = Token.deserialize(result);
            resolve(tokenObj);

            this.checkRefreshAhead(token);
          }
          catch(e) {
            logger.info("Failed to deserialize token from cache: ", e);
            reject(this.internalError());
          }
        }
      });
    })
  }

  checkRefreshAhead(token) {
    this.redis.ttl(this.cacheKey(token), (err, result) => {
      if(err) {
        logger.info("Failed to get TTL to ahead-refresh cache.")
        return;
      }
      const refreshAheadHitTTLFactor = refreshAheadHitTTLFactorMin + Math.random() * (refreshAheadHitTTLFactorMax - refreshAheadHitTTLFactorMin);
      const ttlThreshold = Math.round(refreshAheadHitTTLFactor * hitTTL);
      if(result >= 0 && result <= ttlThreshold) {
        this.handleCacheMiss(token).then(() => {
          // no-op
        }).catch((e) => {
          // no-op
        })
      }
    });
  }

  internalError() {
    var err = new Error('Internal auth error');
    err.status = 500;
    err.details = { code: 'internal_auth_error' };
    return err;
  }

  handleCacheMiss(token) {
    return new Promise((resolve, reject) => {
      this.requestDbFetch(token).then((tokenObj) => {
        var ttl = tokenObj.exists ? hitTTL : missTTL;
        this.redis.setex(
          this.cacheKey(token),
          ttl,
          tokenObj.serialize()
        ).catch((e) => {
          logger.info("Failed to set redis token cache", e);
        }).finally(() => {
          resolve(tokenObj);
        });
      }).catch(() => {
        reject(this.internalError());
      });
    })
  }

  cacheKey(token) {
    return `oauth2_token:${token}`;
  }

  requestDbFetch(token) {
    return new Promise((resolve, reject) => {
      this.pendingDbFetches.push({ token, resolve, reject });
    });
  }

  fetchFromDb() {
    if(this.pendingDbFetches.length == 0) return;
    logger.info(`Pending oauth token fetches from SQL: ${this.pendingDbFetches.length}`);

    var fetches = this.pendingDbFetches;
    this.pendingDbFetches = [];

    this.db.query(
      `
      SELECT token, created_at, expires_in, revoked_at, scopes, resource_owner_id, application_id
      FROM oauth_access_tokens
      WHERE oauth_access_tokens.token = ANY ($1)
      `,
      [ fetches.map((f) => f.token) ]
    ).then((res) => {
      var byToken = {};
      res.rows.forEach((row) => {
        byToken[row.token] = row;
      });

      fetches.forEach((fetch) => {
        if(fetch.token in byToken) {
          fetch.resolve(Token.fromSql(byToken[fetch.token]));
        }
        else {
          fetch.resolve(Token.fromNotFound());
        }
      })
    }).catch((e) => {
      logger.info("Error while fetching tokens from SQL:", e);
      fetches.forEach((fetch) => {
        fetch.reject(e);
      })
    });
  }
}

module.exports = TokenAuth;
