class Key {
  isAcceptable() {
    return this.exists;
  }

  serialize() {
    return JSON.stringify(this);
  }

  toError() {
    if(!this.exists) {
      return "API Key invalid";
    }
  }

  static fromSql(row) {
    var k = new Key();
    k.exists = true;
    k.ip_passlist = row.ip_passlist;
    k.user_id = row.user_id;
    return k;
  }
  static deserialize(entryJson) {
    var data = JSON.parse(entryJson);
    var k = new Key();
    Object.keys(data).forEach((key) => {
      k[key] = data[key];
    });
    return k;
  }
  static fromNotFound() {
    var k = new Key();
    k.exists = false;
    return k;
  }
}

module.exports = Key;
