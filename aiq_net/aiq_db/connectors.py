__author__ = 'vicident'

import sqlite3
from aiq_net.interfaces.idb import IDatabaseConnector
import os

class SqliteConnector(IDatabaseConnector):

    def __init__(self):
        self.conn = None
        self.name = None

    def connect(self, db_path):
        self.conn = sqlite3.connect(db_path)
        self.name = os.path.basename(db_path)

    def get_name(self):
        return self.name

    def get_tables(self):
        list_table_names = []
        for table_name in self.conn.execute("SELECT name FROM sqlite_master WHERE type=\'table\'"):
            list_table_names.append(table_name[0])

        return list_table_names

    def read_table(self, table_name):
        fields = self.get_table_columns(table_name)
        table = {}
        for key in fields:
            table[key] = []
            for row in self.conn.execute("SELECT * FROM " + table_name):
                table[key].append(row[0])

    def read_table_column(self, table_name, column_name, sort):
        sql_str = "SELECT " + column_name \
                  + " FROM " + table_name \
                  + " ORDER BY " + column_name
        if sort < 0:
            sql_str += " DESC"
        elif sort > 0:
            sql_str += " ASC"

        column = []
        for row in self.conn.execute(sql_str):
            column.append(row[0])

        return column


    def read_table_range(self, table_name, columns_read, column_range, first_value, last_value):
        sql_str = "SELECT " + reduce(lambda str, elem: str + "," + elem, columns_read) \
                  + " FROM " + table_name \
                  + " WHERE " + column_range + " >= " + str(first_value) \
                  + " AND " + column_range + " <= " + str(last_value)
        sub_table = []
        for row in self.conn.execute(sql_str):
            sub_table.append(row)

        return sub_table

    def get_table_columns(self, table_name):
        self.conn.row_factory = sqlite3.Row
        c = self.conn.cursor()
        c.execute("SELECT * FROM " + table_name)
        r = c.fetchone()
        return r.keys()


    def close(self):
        self.conn.close()