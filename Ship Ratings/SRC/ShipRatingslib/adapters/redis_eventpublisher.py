import json
import logging
from dataclasses import asdict
import redis

from ShipRatingslib import config
from ShipRatingslib.Domain import ReviewMistakes

logger = logging.getLogger(__name__)

r = redis.Redis(**config.get_redis_host_and_port())


def publish(channel, event: ReviewMistakes.Event):
    logging.info("publishing: channel=%s, event=%s", channel, event)
    r.publish(channel, json.dumps(asdict(event)))
