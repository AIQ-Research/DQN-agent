__author__ = 'vicident'

from abc import ABCMeta, abstractmethod

class IDatabaseConnector:
    __metaclass__ = ABCMeta

    @abstractmethod
    def connect(self, db_path): pass

    @abstractmethod
    def close(self): pass

    @abstractmethod
    def get_name(self): pass

    @abstractmethod
    def get_tables(self): pass

    @abstractmethod
    def read_table_column(self, table_name, column_name, sort): pass

    @abstractmethod
    def read_table(self, table_name): pass

    @abstractmethod
    def get_table_columns(self, table_name): pass

    @abstractmethod
    def read_table_range(self, table_name, columns_read, column_range, first_value, last_value): pass

    @abstractmethod
    def read_tables_rows(self, column_range, first_value, last_value, columns_exclude=[]): pass
