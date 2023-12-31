# class A:
#     def __iter__(self):
#         return iter({
#             "a": 1,
#             "b": 2
#         })
    

# print(dict(A()))













# import sqlite3

# conn = sqlite3.connect('otchat.db')
# c = conn.cursor()
# c.execute("SELECT * FROM users")

# print(c.fetchall())

# from MercurySQLite import DataBase
# db = DataBase("otchat.db")
# db['users'].insert(username="admin", password="admin")
# c.execute("SELECT * FROM users")

# print(c.fetchall())
# print(list(db['users'].select()))














# from hashlib import sha256

# def h(s):
#     return sha256(s.encode()).hexdigest()

# print(h("admin"))
# print(h(h("admin")+"0.8802701181325867"))













from MercurySQLite import DataBase
import MercurySQLite as Mercury

otchat = DataBase("otchat.db")

# otchat['users'].insert(username="joker", password="is me")

otchat.cursor.execute("SELECT * FROM users WHERE 1 = 1;")
otchat.conn.commit()
print(otchat.cursor.fetchall())

otchat.do("SELECT * FROM users WHERE 1 = ?;", paras=[(1,)])
otchat.conn.commit()
print(otchat.cursor.fetchall())

res = otchat.do("SELECT * FROM users WHERE 1 = ?;", paras=[(1,)])
otchat.conn.commit()
print(res.fetchall())

exp = Mercury.gensql.Exp(1, '=', 1)
print(exp)
print(exp.query(otchat['users'], select='*'))

print(list(otchat['users'].select()))


print(list(otchat['users'].select()))

"""
所有的查询都是查询表达式 Mercury.gensql.Exp 的实例, 这些实例被 python 删除的时候默认会调用__del__方法, 而__del__其实被我误用做了delete data!
"""















# import sqlite3

# # Connect to the database
# conn = sqlite3.connect('otchat.db')
# c = conn.cursor()

# # Create table if not exists
# c.execute('''CREATE TABLE IF NOT EXISTS users
#              (username text, password text)''')

# # Insert a row of data
# # c.execute("INSERT INTO users VALUES ('joker','is me')")

# # Save (commit) the changes
# conn.commit()

# # Now we can perform query on the data
# c.execute('SELECT * FROM users')
# print(c.fetchall())
# conn.commit()

# c.execute('SELECT * FROM users')
# print(c.fetchall())
# conn.commit()

# # Close the connection if we are done with it.
# conn.close()