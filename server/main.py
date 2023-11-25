import asyncio
import websockets
from MercurySQLite import DataBase
import json
from hashlib import sha256 as hash
import time
import random


class ChatApp:
    def __init__(self):
        print(" [*] Opening Database ...")
        self.db_chat = DataBase("otchat.db")
        self.db_msg = DataBase("messages.db")
        print(" [\u2713] Database Opened")

        print(" [*] Creating Table ...")
        self.db_chat.createTable("users", "tokens", "chats")

        print(" [*] Initializing Table ...")
        self.db_chat['users'].struct({
            "username": str,
            "password": str
        }, primaryKey="username")

        self.db_chat['tokens'].struct({
            "token": str,
            "pwd": str,
            "username": str,
            "expiry": int
        }, primaryKey="token")

        self.db_chat['chats'].struct({
            "chatID": str,
            "users": str
        }, primaryKey="chatID")
        print(" [\u2713] Table Initialized")

        print(" [\u2713] Table Created")

    class Authen:
        def __init__(self, fa, code):
            """
            code:
             *  0: success
             * -1: waiting
             *  1: invalid username/password
             *  2: token expired
            """
            self.fa = fa
            self.db_chat = self.fa.db_chat

            self.code = code
            self.id = ""

        def result(self):
            return {
                "type": "auth",
                "code": self.code,
                "id": self.id
            }

        def auth_pwd(self, username, password, salt):
            """
            username: username
            password: password
            """
            tb = self.db_chat['users']
            res = tb.select(tb['username'] == username, 'username, password')
            print("log71", tb.select(), len(res))


            # if user not found
            if len(res) == 0:
                self.code = 1
                return

            # if password is wrong
            if hash(f"{res[0].password}{salt}".encode()).hexdigest() != password:
                self.code = 1
                return

            # success
            self.code = 0
            self.id = res[0].username
            print(self.id, "logged in")

        def auth_token(self, token, salt):
            """
            token: token
            """
            tb = self.db_chat['tokens']
            token, pwd = token[:64], token[64:]
            res = tb.select(tb['token'] == token, 'pwd, username, expiry')

            # if token not found
            if len(res) == 0:
                self.code = 1
                return

            # if token is expired
            if res[0].expiry < time.time():
                tb.delete(tb['token'] == token)  # delete token
                self.code = 2
                return

            # if password is wrong
            if hash(f"{res[0].pwd}{salt}".encode()).hexdigest() != pwd:
                self.code = 1
                return

            # success
            self.code = 0
            self.id = res[0].username

    def auth(self, msg) -> Authen:
        a = ChatApp.Authen(self, -1)

        if msg['authmethod'] == 'password':
            a.auth_pwd(msg['username'], msg['password'], msg['salt'])
        elif msg['authmethod'] == 'token':
            a.auth_token(msg['token'], msg['salt'])

        return a

    def checkAccess(self, chatID, uid):
        tb = self.db_chat['chats']
        res = tb.select(tb['chatID'] == chatID)

        if len(res) == 0:
            return False

        if uid in res[0].users.split(','):
            return True

        return False

    def random(self):
        s = str(time.time())

        for _ in range(random.randint(20, 40)):
            s += str(random.random())

        return hash(s.encode()).hexdigest()

    def genToken(self, username, password):
        token = hash(
            f"{username}{self.random()}{password}".encode()).hexdigest()
        pwd = hash(f"{password}{self.random()}{username}".encode()).hexdigest()

        self.db_chat['tokens'].insert(
            token=token,
            pwd=pwd,
            username=username,
            expiry=int(time.time() + 30*24*60*60)
        )

        return token + pwd

    def newUser(self, username, password):
        self.db_chat['users'].insert(username=username, password=password)


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
        print('   [{}] {}'.format(addr, message['type']))

        if message['type'] == 'close':
            # remove from queue
            queue[rev_queue[websocket]].remove(websocket)

            await websocket.close()
            return

        if message['type'] == 'auth':
            status = otchat.auth(message)
            if status.code == 0:
                USERID = status.id

                res = status.result()
                if message['authmethod'] == 'password' and message['AuthNeedToken']:
                    res['token'] = otchat.genToken(USERID, message['password'])

                await websocket.send(json.dumps(res))
            else:
                await websocket.send(json.dumps(status.result()))
            continue
        if message['type'] == 'checkauth':
            await websocket.send(json.dumps({
                "type": "checkauth",
                "uid": USERID
            }))

        if message['type'] == 'changeroom':
            # remove from queue
            queue[rev_queue[websocket]].remove(websocket)

            # add to queue
            if message['chatID'] not in queue:
                await websocket.send('{"type": "error", "code": 1, "msg": "Chat not found"}')
                continue

            if not otchat.checkAccess(message['chatID'], USERID):
                await websocket.send('{"type": "error", "code": 2, "msg": "Access denied"}')
                continue

            queue[message['chatID']].append(websocket)
            rev_queue[websocket] = message['chatID']

            # send chat history
            CHATID = message['chatID']
            await websocket.send(otchat.db_msg[CHATID].select())


if __name__ == '__main__':
    otchat = ChatApp()

    otchat.newUser('admin', hash('admin'.encode()).hexdigest())

    start_server = websockets.serve(handle_connection, 'localhost', 12345)

    print("Serving at 'localhost:12345'")

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
