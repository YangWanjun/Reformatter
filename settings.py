#coding: UTF-8

import os, sys
import common

from PyQt4 import QtSql


class Setting:

    CONNECTION_NAME = "settings"

    def __init__(self):
        self.db = None
        self.init_database()
        
        o = FindingOption(None)
        print o.get_create_table_sql()

    def init_database(self):
        db_path = os.path.join(common.get_root_path(), 'setting.db')
        if not os.path.exists(db_path):
            self.db = QtSql.QSqlDatabase.addDatabase("QSQLITE")
            self.db.setDatabaseName(db_path)

            sql_list = {
                "FindingOption" : "CREATE TABLE FindingOption"
                                  "("
                                  " id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                  ",is_whole_word INTEGER NOT NULL DEFAULT 0"
                                  ",is_case_sensitive INTEGER NOT NULL DEFAULT 0"
                                  ",is_regular INTEGER NOT NULL DEFAULT 0"
                                  ",is_show_message INTEGER NOT NULL DEFAULT 0"
                                  ",is_auto_close INTEGER NOT NULL DEFAULT 0"
                                  ",is_research INTEGER NOT NULL DEFAULT 0"
                                  ")",
                "FindingHistory" : "CREATE TABLE FindingHistory"
                                   "("
                                   " id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
                                   ",finding_option_id INTEGER NOT NULL"
                                   ",condition TEXT NOT NULL"
                                   ",FOREIGN KEY(finding_option_id) REFERENCES FindingOption(id)"
                                   ")",
            }
            for table_name, sql in sql_list.items():
                self.create_table(table_name, sql)
            self.db.close()

    def create_table(self, table_name, sql):
        if not self.db.isOpen():
            self.db.open()
        if self.db.lastError().isValid():
            print self.db.lastError().text()
            return False
        # テーブルが存在したら削除する。
        query = QtSql.QSqlQuery(self.db)
        if query.exec_("DROP TABLE IF EXISTS %s" % (table_name,)):
            print "Drop %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()

        # テーブル作成
        query = QtSql.QSqlQuery(self.db)
        if query.exec_(sql):
            print "Create %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()
        else:
            print "Create %s Failure!" % (table_name,)


class BaseOption:
    def __init__(self):
        pass

    def get_table_name(self):
        return self.__class__.__name__

    def get_table_name_by_attr(self, key):
        slice = [i.capitalize() for i in key.split("_")]
        class_name = "".join(slice)
        return getattr(sys.modules[__name__], class_name)

    def get_create_table_sql(self):
        sql_columns = ""
        for key in self.__dict__.keys():
            if key.find('__') < 0:
                sql_columns += self.get_create_column_sql(key)
        return "CREATE TABLE %s (%s %s)" % (self.get_table_name(), self.get_create_primary_key(), sql_columns)

    def get_create_primary_key(self):
        return " id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"

    def get_create_column_sql(self, key):
        value = getattr(self, key)
        if isinstance(value, bool):
            return ",%s INTEGER NOT NULL DEFAULT 0" % (key,)
        elif isinstance(value, int):
            return ",%s INTEGER" % (key,)
        elif isinstance(value, str):
            return ",%s TEXT" % (key,)
        elif isinstance(value, list):
            obj = self.get_table_name_by_attr(key)()
            print obj.get_create_table_sql()
            return ""
        else:
            return ""

    def load_settings(self):
        pass


class FindingOption(BaseOption):
    def __init__(self, db=None):
        self.__db = db
        self.finding_history = []
        self.is_whole_word = False
        self.is_case_sensitive = False
        self.is_regular = False
        self.is_show_message = False
        self.is_auto_close = False
        self.is_research = False


class FindingHistory(BaseOption):
    def __init__(self, db=None):
        self.__db = db
        self.finding_option_id = 0
        self.condition = ""
