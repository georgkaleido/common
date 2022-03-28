const Redis = require("ioredis")
const PubSub = require("kaleido-api/gc_pub_sub")
const log = require("kaleido-api/modern_logger")
class RateLimitHitReporter {
  constructor(topic = process.env.PUBSUB_TOPIC_RATE_LIMIT, ttl = 86400) {
    this.redis = new Redis(process.env.REDIS_URL)
    this.pubSub = new PubSub(topic)
    this.ttl = ttl
  }

  async report(user) {
    const key = `rlh:${user}`
    const message = {
      user_id: user,
      brand: "remove_bg",
    }

    try {
      const result = await this.redis.get(key)
      if (result == null) {
        this.redis.set(key, true, "EX", this.ttl)
        this.pubSub.publish(message)
      }
    } catch (e) {
      log.error("Failed to report rate limit hit: " + e)
    }
  }
}

module.exports = RateLimitHitReporter

