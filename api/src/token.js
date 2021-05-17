class Token {
  isAcceptable() {
    return this.exists && !this.isRevoked() && !this.isExpired();
  }

  isRevoked() {
    if(!this.revoked_at) return false;
    var now = new Date().getTime() / 1000;
    return this.revoked_at <= now;
  }

  isExpired() {
    if(!this.created_at || !this.expires_in) return false;
    var now = new Date().getTime() / 1000;
    return this.created_at + this.expires_in <= now;
  }

  serialize() {
    return JSON.stringify(this);
  }

  toError() {
    if(!this.exists) {
      return "Auth token invalid";
    }
    else if(this.isRevoked()) {
      return "Auth token revoked";
    }
    else if(this.isExpired()) {
      return "Auth token expired";
    }
  }

  requireScopes(requiredScopes) {
    return new Promise((resolve, reject) => {
      var scopes = this.scopes.split(" ");
      var missingScopes = requiredScopes.filter(requiredScope => !scopes.includes(requiredScope));
      if(missingScopes.length == 0) {
        resolve();
      }
      else {
        reject(`Auth token lacks scope(s) ${missingScopes.join(', ')}`);
      }
    });
  }

  static fromSql(row) {
    var t = new Token();
    t.exists = true;
    t.created_at = row.created_at ? Math.floor(row.created_at.getTime() / 1000) : null;
    t.expires_in = row.expires_in;
    t.revoked_at = row.revoked_at ? Math.floor(row.revoked_at.getTime() / 1000) : null;
    t.scopes = row.scopes;
    t.resource_owner_id = row.resource_owner_id;
    t.application_id = row.application_id;
    return t;
  }
  static deserialize(entryJson) {
    var data = JSON.parse(entryJson);
    var t = new Token();
    Object.keys(data).forEach((key) => {
      t[key] = data[key];
    });
    return t;
  }
  static fromNotFound() {
    var t = new Token();
    t.exists = false;
    return t;
  }
}

module.exports = Token;
