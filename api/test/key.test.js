const mocha = require('mocha')
const chai = require('chai')

const key = require('../src/key')
const Key = require("../src/key");

const expect = chai.expect

describe('Key', function () {

  // We will describe each single test using it
  it('Key from SQL to be valid', () => {
    let row = {ip_passlist: "", user_id: ""}
    let result = Key.fromSql(row)
    expect(result.exists).to.equal(true)
  })

})
