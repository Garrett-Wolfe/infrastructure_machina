import datetime
import logging
import os
import random
import redis
import time

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port)

while True:
    r.publish('hello_channel', f'hello world  {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    logger.info("Published: hello world")
    time.sleep(random.randint(1, 10))