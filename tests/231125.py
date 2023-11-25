# class A:
#     def __iter__(self):
#         return iter({
#             "a": 1,
#             "b": 2
#         })
    

# print(dict(A()))

import sqlite3

conn = sqlite3.connect('otchat.db')
c = conn.cursor()
c.execute("SELECT * FROM users")

print(c.fetchall())

from MercurySQLite import DataBase
db = DataBase("otchat.db")
db['users'].insert(username="admin", password="admin")
c.execute("SELECT * FROM users")

print(c.fetchall())
print(list(db['users'].select()))


# from hashlib import sha256

# def h(s):
#     return sha256(s.encode()).hexdigest()

# print(h("admin"))
# print(h(h("admin")+"0.8802701181325867"))