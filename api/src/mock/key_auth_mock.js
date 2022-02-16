const logger = require("kaleido-api/logger");

class MockKeyAuth {
  constructor(db) {
    this.db = db;
    this.lookups = {};
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
      this.fetchKeyOnce(key).then((keyObj) => {
        resolve(keyObj);
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
      resolve({

      });
    })
  }
}

module.exports = MockKeyAuth;
