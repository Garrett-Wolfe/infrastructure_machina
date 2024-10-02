import os
import random
import redis
import time

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port)

while True:
    r.publish('hello_channel', 'hello world')
    print("Published: hello world")
    time.sleep(random.randint(1, 10))



# monitor with
# docker logs -f demo