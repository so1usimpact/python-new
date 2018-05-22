import mysql.connector
import json
import datetime
import io
import datetime
import pprint
from text_cleaner import text_cleaner

class MysqlConnector:

    #FROM EXTERNAL FILE
    connection_config={}

    #TABLES AND COLUMNS FROM connection_config['database']
    tables_config={'default':'structured_data'}

    def get_connection_config(self, loc):
        with open(loc, 'r') as f:
            read_data = []
            for line in f:
                for word in line.split():
                    if word == 'None':
                        read_data.append('')
                    else:
                        read_data.append(word)
        connection_config = dict(zip(read_data[::2], read_data[1::2]))
        return connection_config

    def get_tables(self):

     database = self.connection_config['database']

     query  = "SELECT TABLE_NAME "
     query += "FROM INFORMATION_SCHEMA.TABLES "
     query += "WHERE TABLE_TYPE = 'BASE TABLE' "
     query += "AND TABLE_SCHEMA = '"+database+"';"
     table_names=[]

     self.execute_query(query)
     for item in self.cursor:
         table_names.append(''.join(item))
     return table_names

    def get_columns(self, table=None):

        if table is None:
            table = self.tables_config['default']
        db_name = self.connection_config['database']

        query = " SELECT `COLUMN_NAME` "
        query += "FROM `INFORMATION_SCHEMA`.`COLUMNS` "
        query += "WHERE `TABLE_SCHEMA`='" + db_name + "'"
        query += "AND `TABLE_NAME`='" + table + "';"
        column_names = []

        self.execute_query(query)

        # Creating list
        for item in self.cursor:
            column_names.append(''.join(item))

        # Returns list
        return column_names

    def get_tables_config(self):
        return self.tables_config

    def select_query(self,columns,table,limit=None,where=None):

        query = "SELECT " + columns + " "
        query += "FROM " + table + " "
        if where is None:
            query += "WHERE" + where + ""
        if limit is None:
            query += "LIMIT" + limit + ""
        query +=";"

        return query

    def execute_query(self, query=""):

        if query == "":
            query = self.query
        print("executing")
        try:
            self.cursor.execute(query)
            self.cnx.commit()
            print("success.")
        except mysql.connector.Error as err:
            print(self.cnx.rollback())
            print(err)
            print("failure.")




    def init_tables(self):
        tables = self.get_tables()

        for table in tables:
            columns = self.get_columns(table)
            self.tables_config[table]=columns

    def __init__(self):
        self.connection_config = self.get_connection_config('../connection_config.txt')
        self.cnx = mysql.connector.connect(**self.connection_config)
        self.cursor = self.cnx.cursor(buffered=True)
        self.query = ""
        self.init_tables()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cnx:
            self.cnx.close()

def main():
    db = MysqlConnector()
    pprint.pprint(db.get_tables_config())
if __name__ == '__main__':
    main()