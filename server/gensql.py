"""
Use built-in sqlite3 library to operate sql in a more good way.
"""

import sqlite3
from typing import Any, Union

class Exp: pass
class Table: pass
class DataBase: pass


class DataBase:
    def __init__(self, db_name: str):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

        self.info = {
            "name": db_name
        }

        self._gather_info()

    def __getitem__(self, key: str) -> Table:
        return self.tables[key]

    def _gather_info(self):
        def get_all_tables():
            self.cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table';")
            return list(map(lambda x: x[0], self.cursor.fetchall()))

        self.tables = get_all_tables()
        self.tables = {tname: Table(self, tname) for tname in self.tables}

    def do(self, *sql: str) -> sqlite3.Cursor:
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

    def createTable(self, table_name: str) -> Table:
        """
        create a table in the database.

        Paras:
            table_name: str
                The name of the table.
        """
        if table_name in self.tables:
            raise Exception("Table already exists.")

        table = Table(self, table_name)
        # must be executed after Table.__init__()
        self.tables[table_name] = table

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

    def __getitem__(self, key: str) -> Exp:
        if key not in self.columns:
            raise Exception("Column not exists.")
        return Exp(key)

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
            self.db.do(
                f"ALTER TABLE {self.table_name} ADD COLUMN {name} {type}")

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


class Exp:
    def __init__(self, o1, op='', o2=''):
        self.o1 = o1
        self.op = op
        self.o2 = o2
    
    def __str__(self):
        if self.op == '':
            return str(self.o1)
        return f"({str(self.o1)} {str(self.op)} {str(self.o2)})"
    
    def __eq__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, '=', __value)
    
    def __ne__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, '<>', __value)
    
    def __lt__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, '<', __value)
    
    def __le__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, '<=', __value)
    
    def __gt__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, '>', __value)
    
    def __ge__(self, __value: Union[Exp, int, str]) -> Exp:  
        return Exp(self, '>=', __value)
    
    def between(self, __value1: Union[Exp, int, str], __value2: Union[Exp, int, str]) -> Exp:
        return Exp(self, 'BETWEEN', str(__value1) + ' AND ' + str(__value2))
    
    def in_(self, __value1: Union[list, tuple, set]) -> Exp:
        return Exp(self, 'IN', str(tuple(__value)))

    def like(self, __value: str) -> Exp:
        return Exp(self, 'LIKE', __value)
    
    def __and__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, 'AND', __value)
    
    def __or__(self, __value: Union[Exp, int, str]) -> Exp:
        return Exp(self, 'OR', __value)
    
    def __invert__(self) -> Union[Exp, int, str]:
        return Exp('', 'NOT', self)

if __name__ == '__main__':
    db = DataBase("test.db")
    print(db.info)

    test_table = db['test']
    print(db.tables)

    print((db['test']['id'] == 1) & (db['test']['name']=='test'))
    print(db['test'].columns)
