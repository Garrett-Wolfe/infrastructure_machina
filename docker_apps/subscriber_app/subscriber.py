import os
import logging
import redis.asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
from redis.exceptions import ConnectionError

log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=log_level,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)
logger = logging.getLogger(__name__)


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Hello World</title>
    </head>
    <body>
        <h1>Hello World Messages</h1>
        <ul id="messages"></ul>
        <script>
            const ws_scheme = window.location.protocol === "https:" ? "wss" : "ws";
            const ws_url = ws_scheme + "://" + window.location.host + "/ws";
            const ws = new WebSocket(ws_url);
            ws.onmessage = function(event) {
                const messages = document.getElementById('messages');
                const message = document.createElement('li');
                message.textContent = event.data;
                messages.appendChild(message);
            };
        </script>
    </body>
</html>
"""

redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Attempting to connect to redis at {redis_host}:{redis_port}")
    app.state.redis = redis.asyncio.Redis(
        host=redis_host,
        port=redis_port,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    logger.info("Connected")
    yield
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("accepted websocket connection")
    try:
        async with app.state.redis.pubsub() as pubsub:
            logger.info("created pubsub")
            await pubsub.subscribe('hello_channel')
            logger.info("subscribed to hello_channel")
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    logger.info("Received message from Redis")
                    await websocket.send_text(message['data'].decode())

    except ConnectionError as e:
        logger.error(f"Redis connection error: \n{e}")
    except Exception as e:
        logger.error(f"Error: \n{e}")
    finally:
        await websocket.close()
        if pubsub:
            await pubsub.unsubscribe('hello_channel')
            await pubsub.close()

