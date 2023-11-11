import asyncio
import websockets

async def handle_connection(websocket, path):
    addr = websocket.remote_address
    print("Client Connected {}".format(addr))
    await websocket.send('{"type": "message", "from": "WELCOME", "avatar": "assets/img/server.jpg", "msg": "Hello Client"}')

    # Loop to receive messages from the client
    async for message in websocket:
        print("Received message from `{}`: {}".format(addr, message))

start_server = websockets.serve(handle_connection, 'localhost', 12345)

print("Serving at 'localhost:12345'")

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
