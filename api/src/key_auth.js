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

const Key = require("./key");

class KeyAuth {
  constructor(db) {
    this.db = db;
    this.lookups = {};
    this.redis = new Redis(process.env.REDIS_URL);
    this.pendingDbFetches = [];

    setInterval(() => {
      this.fetchFromDb();
    }, sqlFetchInterval);
  }

  fromApiKeyHeader(header) {
    header = String(header);

    // a key is a 24-character base58 string
    // https://api.rubyonrails.org/classes/ActiveRecord/SecureToken/ClassMethods.html
    var authRegexp = /^([123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ]{24})$/;
    var authMatch = authRegexp.exec(header);
    if(authMatch) {
      var key = authMatch[1];
      return this.fromKey(key);
    }
    else {
      return new Promise((_resolve, reject) => {
        var err = new Error("API Key invalid");
        err.status = 403;
        err.details = { code: 'auth_failed' };
        reject(err);
      });
    }
  }

  fromKey(key) {
    return new Promise((resolve, reject) => {
      this.fetchKey(key).then((keyObj) => {
        if(keyObj.isAcceptable()) {
          resolve(keyObj);
        }
        else {
          var err = new Error(keyObj.toError());
          err.status = 403;
          err.details = { code: 'auth_failed' };
          reject(err);
        }
      }).catch(reject);
    })
  }

  fetchKeyOnce(key) {
    if(!(key in this.lookups)) {
      this.lookups[key] = this.fetchKey(key).finally(() => {
        delete this.lookups[key];
      });
    }
    return this.lookups[key];
  }

  fetchKey(key) {
    return new Promise((resolve, reject) => {
      this.redis.get(this.cacheKey(key), (err, result) => {
        if(err) {
          logger.info("Redis error while getting key:", err);
          return reject(this.internalError());
        }
        if(result == null) {
          this.handleCacheMiss(key).then(resolve).catch(reject);
        }
        else {
          try {
            var keyObj = Key.deserialize(result);
            resolve(keyObj);

            this.checkRefreshAhead(key);
          }
          catch(e) {
            logger.info("Failed to deserialize key from cache: ", e);
            reject(this.internalError());
          }
        }
      });
    })
  }

  checkRefreshAhead(key) {
    this.redis.ttl(this.cacheKey(key), (err, result) => {
      if(err) {
        logger.info("Failed to get TTL to ahead-refresh cache.")
        return;
      }
      const refreshAheadHitTTLFactor = refreshAheadHitTTLFactorMin + Math.random() * (refreshAheadHitTTLFactorMax - refreshAheadHitTTLFactorMin);
      const ttlThreshold = Math.round(refreshAheadHitTTLFactor * hitTTL);
      if(result >= 0 && result <= ttlThreshold) {
        this.handleCacheMiss(key).then(() => {
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

  handleCacheMiss(key) {
    return new Promise((resolve, reject) => {
      this.requestDbFetch(key).then((keyObj) => {
        var ttl = keyObj.exists ? hitTTL : missTTL;
        this.redis.setex(
          this.cacheKey(key),
          ttl,
          keyObj.serialize()
        ).catch((e) => {
          logger.info("Failed to set redis key cache", e);
        }).finally(() => {

          resolve(keyObj);
        });
      }).catch(() => {
        reject(this.internalError());
      });
    })
  }

  cacheKey(key) {
    return `api_key:${key}`;
  }

  requestDbFetch(key) {
    return new Promise((resolve, reject) => {
      this.pendingDbFetches.push({ key, resolve, reject });
    });
  }

  fetchFromDb() {
    if(this.pendingDbFetches.length == 0) return;
    logger.info(`Pending api key fetches from SQL: ${this.pendingDbFetches.length}`);

    var fetches = this.pendingDbFetches;
    this.pendingDbFetches = [];
    this.db.query(
      `
      SELECT id, key, old_key, user_id, ip_passlist
      FROM api_keys
      WHERE deleted_at IS NULL
      AND  ( key = ANY ($1) OR old_key = ANY ($1) )
      `,
      [ fetches.map((f) => f.key) ]
    ).then((res) => {
      var byKey = {};
      res.rows.forEach((row) => {
        byKey[row.key] = row;
        if(row.old_key) {
          byKey[row.old_key] = row; // support for key and old_key at the same time
        }
      });
      fetches.forEach((fetch) => {
        if(fetch.key in byKey) {
          fetch.resolve(Key.fromSql(byKey[fetch.key]));
        }
        else {
          fetch.resolve(Key.fromNotFound());
        }
      })
    }).catch((e) => {
      logger.info("Error while fetching api keys from SQL:", e);
      fetches.forEach((fetch) => {
        fetch.reject(e);
      })
    });
  }
}

module.exports = KeyAuth;
