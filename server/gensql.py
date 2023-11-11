"""
Use built-in sqlite3 library to operate sql in a more good way.
"""

import sqlite3


class DataBase:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.info = {
            "name": db_name
        }

        self._gather_info()

    def _gather_info(self):
        def get_all_tables():
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            return list(map(lambda x: x[0], self.cursor.fetchall()))

        self.tables = get_all_tables()
        self.tables = {tname: Table(self, tname) for tname in self.tables}

    def do(self, *sql):
        """
        Execute a sql command on the database.
        
        Paras:
            sql: str
                The sql command(s).
        """
        for command in sql:
            self.cursor.execute(command)
        
        self.conn.commit()

        return self.cursor

    def createTable(self, table_name):
        """
        create a table in the database.

        Paras:
            table_name: str
                The name of the table.
        """
        if table_name in self.tables:
            raise Exception("Table already exists.")
        
        table = Table(self, table_name)
        self.tables[table_name] = table # must be executed after Table.__init__()

        return table


class Table:
    def __init__(self, db: DataBase, table_name: str):
        self.name = table_name

        self.db = db
        self.table_name = table_name
        
        if table_name in self.db.tables:
            # table exists
            self.isEmpty = False
        else:
            # table not exists
            # can't create a table with no columns, so it's a hackish way to create a table when adding a column.
            self.isEmpty = True

        self._gather_info()

    def _gather_info(self):
        def get_columns():
            cursor = self.db.do(f"PRAGMA table_info({self.table_name})")
            return list(map(lambda x: x[1], cursor.fetchall()))

        if not self.isEmpty:
            self.columns = get_columns()
        else:
            self.columns = []


    def newColumn(self, name, type, primaryKey=False):
        if name in self.columns:
            raise Exception("Column already exists.")

        if self.isEmpty:
            # create it first
            self.db.do(f"""
                CREATE TABLE IF NOT EXISTS {self.name} ({name} {type} {'PRIMARY KEY' if primaryKey else ''})
            """)
        else:
            self.db.do(f"ALTER TABLE {self.table_name} ADD COLUMN {name} {type}")
        
            if primaryKey:
                self.setPrimaryKey(name)

        self.columns.append(name)
    
    def setPrimaryKey(self, keyname):
        self.db.do(
            f"CREATE TABLE new_table ({keyname} INTEGER PRIMARY KEY, {', '.join([f'{name} {type}' for name, type in self.columns.items() if name != keyname])})",
            f"INSERT INTO new_table SELECT * FROM {self.table_name}",
            f"DROP TABLE {self.table_name}",
            f"ALTER TABLE new_table RENAME TO {self.table_name}"
        )


if __name__ == '__main__':
    db = DataBase("test.db")
    print(db.info)

    # print(db.tables)
    # db.createTable("test2")
    test_table = db.tables['test']
    print(db.tables)

    print(db.tables['test'].columns)
    # test_table.newColumn("id", "INTEGER", primaryKey=True)
    # test_table.newColumn("name", "TEXT")
    print(db.tables['test'].columns)
