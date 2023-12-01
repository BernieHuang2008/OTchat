import sqlite3

# Connect to the database
conn = sqlite3.connect('otchat.db')
cursor = conn.cursor()

# Execute a query to retrieve all cells
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

# insert: insert into users (username, password) values ('admin', 'admin')

# Print all cells
for row in rows:
    print(row)

# Close the connection
conn.close()
