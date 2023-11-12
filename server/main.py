import asyncio
import websockets
from gensql import DataBase
import json

queue = {
    "chatID": ["processors"]
}

rev_queue = {
    "processor": "chatID"
}

def checkAccess(chatID, USERINFO):
    return True

async def handle_connection(websocket, path):
    addr = websocket.remote_address
    print("Client Connected {}".format(addr))
    # await websocket.send('{"type": "message", "from": "WELCOME", "avatar": "assets/img/server.jpg", "msg": "Hello Client"}')

    CHATID = None
    USERID = None

    # Loop to receive messages from the client
    async for message in websocket:
        message = json.loads(message)

        if message['type'] == 'close':
            # remove from queue
            queue[rev_queue[websocket]].remove(websocket)

            await websocket.close()
            return
        elif message['type'] == 'changeroom':
            # remove from queue
            queue[rev_queue[websocket]].remove(websocket)

            # add to queue
            if message['chatID'] not in queue:
                await websocket.send('{"type": "error", "code": 1, "msg": "Chat not found"}')
                continue

            if not checkAccess(message['chatID'], USERID):
                await websocket.send('{"type": "error", "code": 2, "msg": "Access denied"}')
                continue

            queue[message['chatID']].append(websocket)
            rev_queue[websocket] = message['chatID']

            # send chat history
            CHATID = message['chatID']
            await websocket.send(db_msg[chatID].select())


if __name__ == '__main__':
    start_server = websockets.serve(handle_connection, 'localhost', 12345)

    print(" [*] Opening Database ...")
    db_chat = DataBase("otchat.db")
    db_msg = DataBase("messages.db")
    print(" [*] Database Opened")

    print(" [*] Creating Table ...")
    db_chat.createTable("chats", "users")

    print("Serving at 'localhost:12345'")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
