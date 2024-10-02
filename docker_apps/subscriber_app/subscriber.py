import os
import asyncio
import redis.asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager


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
            const ws_url = ws_scheme + "://" + window.location.hostname + ":8000/ws";
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
    print(f"Attempting to connect to redis at {redis_host}:{redis_port}")
    app.state.redis = redis.asyncio.Redis(
        host=redis_host,
        port=redis_port,
        socket_connect_timeout=5,
        socket_keepalive=True,
    )
    print("Connected")
    yield
    await app.state.redis.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("accepted websocket connection")
    try:
        pubsub = app.state.redis.pubsub()
        await pubsub.subscribe('hello_channel')
        print("subscribed to hellow_channel")
        while True:
            message = await pubsub.get_message(ignore_subscribe_messages=True)
            if message:
                print("Received message from Redis")
                await websocket.send_text(message['data'].decode())
            await asyncio.sleep(0.1)
    except Exception as e:
        print(f"WebSocket connection error: {e}")
    finally:
        await pubsub.unsubscribe('hello_channel')
        await pubsub.close()

