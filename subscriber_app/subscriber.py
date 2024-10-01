import os
import redis

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))
r = redis.Redis(host=redis_host, port=redis_port)

pubsub = r.pubsub()
pubsub.subscribe('hello_channel')

print("Subscribed to hello_channel")
for message in pubsub.listen():
    if message['type'] == 'message':
        print(f"Received: {message['data'].decode()}")


# monitor with
# docker logs -f subscriber_app