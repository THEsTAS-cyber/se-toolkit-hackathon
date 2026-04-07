"""WebSocket bridge — bridges browser chat to nanobot gateway."""

import asyncio
import json
import os
import uuid
import websockets
from websockets.asyncio.server import serve

GATEWAY_HOST = os.environ.get("NANOBOT_GATEWAY_HOST", "127.0.0.1")
GATEWAY_PORT = int(os.environ.get("NANOBOT_GATEWAY_PORT", 18790))


async def wait_for_gateway(retries=20, delay=1):
    """Wait until nanobot gateway is ready."""
    for i in range(retries):
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(GATEWAY_HOST, GATEWAY_PORT),
                timeout=2,
            )
            writer.close()
            await writer.wait_closed()
            print(f"Gateway ready after {i * delay}s")
            return True
        except Exception:
            print(f"Gateway not ready yet (attempt {i+1}/{retries})...")
            await asyncio.sleep(delay)
    return False


async def handle_client(ws):
    """Handle a browser WebSocket connection."""
    chat_id = str(uuid.uuid4())
    print(f"Client connected: chat_id={chat_id}")

    # Connect to nanobot gateway
    gateway_url = f"ws://{GATEWAY_HOST}:{GATEWAY_PORT}"
    try:
        async with websockets.connect(gateway_url) as gateway_ws:
            print(f"Connected to nanobot gateway at {gateway_url}")

            # Forward messages from browser to gateway
            async def from_browser():
                async for raw in ws:
                    try:
                        data = json.loads(raw)
                        content = data.get("content", data.get("message", "")).strip()
                        if not content:
                            continue
                        print(f"User: {content}")
                        # Nanobot webchat protocol: {content}
                        await gateway_ws.send(json.dumps({"content": content}))
                    except Exception as e:
                        print(f"Error parsing browser message: {e}")

            # Forward messages from gateway to browser
            async def from_gateway():
                async for raw in gateway_ws:
                    try:
                        data = json.loads(raw)
                        # Nanobot sends structured messages: {type, content}
                        content = data.get("content", str(data))
                        print(f"Bot: {content[:200]}")
                        await ws.send(json.dumps({
                            "type": data.get("type", "text"),
                            "content": content,
                        }))
                    except Exception as e:
                        print(f"Error parsing gateway message: {e}")

            await asyncio.gather(from_browser(), from_gateway())

    except Exception as e:
        print(f"Gateway connection error: {e}")
        await ws.send(json.dumps({
            "type": "text",
            "content": f"Error connecting to assistant: {str(e)}",
        }))


async def main():
    port = int(os.environ.get("WEBSOCKET_PORT", 8765))
    print(f"WebSocket bridge listening on :{port}")
    print(f"Forwarding to nanobot gateway at {GATEWAY_HOST}:{GATEWAY_PORT}")

    # Wait for gateway to be ready
    if not await wait_for_gateway():
        print("ERROR: Gateway not available, exiting")
        return

    async with serve(handle_client, "0.0.0.0", port):
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
