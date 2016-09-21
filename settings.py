# coding: UTF-8

import os
import common

from PyQt4 import QtSql


class Setting:

    CONNECTION_NAME = "settings"

    def __init__(self):
        db_path = os.path.join(common.get_root_path(), 'setting.db')
        is_new = False
        if not os.path.exists(db_path):
            db = QtSql.QSqlDatabase.addDatabase("QSQLITE", Setting.CONNECTION_NAME)
            db.setDatabaseName(db_path)
            is_new = True
        else:
            db = QtSql.QSqlDatabase.database(Setting.CONNECTION_NAME, False)
            if not db.isValid():
                db = QtSql.QSqlDatabase.addDatabase("QSQLITE", Setting.CONNECTION_NAME)
                db.setDatabaseName(db_path)
        self.finding_option = FindingOption(db)
        self.finding_history = FindingHistory(db)
        if is_new:
            self.finding_option.create_table()
            self.finding_history.create_table()
        else:
            self.finding_option.load_settings()
            self.finding_history.load_settings()
        print self.finding_option.get_insert_sql()
        print self.finding_history.get_insert_sql()
        print self.finding_option.get_update_sql()
        print self.finding_history.get_update_sql()


class BaseOption:
    def __init__(self, db):
        self.__db = db
        self.__pk = None

    def get_table_name(self):
        """クラス名をそのままテーブル名にする

        :return: テーブル名を返す
        """
        return self.__class__.__name__

    def get_columns(self):
        """クラスのメンバー変数からテーブルの項目を取得する

        プライベート変数とリスト以外のメンバー変数を項目とする。

        :return:
        """
        columns = []
        for key, value in self.__dict__.items():
            if key.find('__') < 0 and not isinstance(value, list):
                columns.append(key)
        return columns

    def get_create_table_sql(self):
        """テーブル作成のSQLを取得する。

        :return: SQL
        """
        sql_columns = ""
        for key in self.get_columns():
            sql_columns += self.get_create_column_sql(key)
        primary_key = " id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT"
        return "CREATE TABLE %s (%s %s)" % (self.get_table_name(), primary_key, sql_columns)

    def get_insert_sql(self):
        """データ追加用のSQLを取得する。

        :return: SQL
        """
        sql_cols = []
        sql_values = []
        for column in self.get_columns():
            sql_cols.append(column)
            value = getattr(self, column)
            if isinstance(value, bool):
                value = 1 if value else 0
            sql_values.append(u"'%s'" % (value,))
        return u"INSERT INTO %s (%s) VALUES (%s)" % (self.get_table_name(), ','.join(sql_cols), ','.join(sql_values))

    def get_update_sql(self):
        """データ更新用のSQLを取得する。

        pkが設定する必要ある、設定してなかったら、空白を戻す

        :return: SQL
        """
        if not self.__pk:
            return ''

        sql_cols = []
        for column in self.get_columns():
            value = getattr(self, column)
            if isinstance(value, bool):
                value = 1 if value else 0
            elif isinstance(value, int):
                pass
            else:
                value = u"'%s'" % (value,)
            sql_cols.append(u"%s = %s" % (column, value))
        return u"UPDATE %s SET %s WHERE id=%s" % (self.get_table_name(), ','.join(sql_cols), self.__pk)

    def get_create_column_sql(self, name):
        """項目定義のSQLを取得する。

        Boolean型はIntegerとする、
        文字列はTextとする。

        :param name: 項目名
        :return:
        """
        value = getattr(self, name)
        if isinstance(value, bool):
            return ",%s INTEGER NOT NULL DEFAULT 0" % (name,)
        elif isinstance(value, int):
            return ",%s INTEGER" % (name,)
        elif isinstance(value, str):
            return ",%s TEXT" % (name,)
        else:
            return ""

    def create_table(self):
        """テーブルを作成する。

        :return: なし
        """
        if not self.__db.isOpen():
            self.__db.open()
        if self.__db.lastError().isValid():
            print self.__db.lastError().text()
            return False
        table_name = self.get_table_name()
        # テーブルが存在したら削除する。
        query = QtSql.QSqlQuery(self.__db)
        if query.exec_("DROP TABLE IF EXISTS %s" % (table_name,)):
            print "Drop %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()

        # テーブル作成
        sql = self.get_create_table_sql()
        query = QtSql.QSqlQuery(self.__db)
        if query.exec_(sql):
            print "Create %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()
        else:
            print "Create %s Failure!" % (table_name,)

    def load_settings(self):
        """DBから項目の設定を取得する。

        :return:
        """
        if not self.__db.isOpen():
            self.__db.open()
        if self.__db.lastError().isValid():
            print self.__db.lastError().text()
            return False

        sql = "SELECT * FROM %s" % (self.get_table_name(),)
        query = QtSql.QSqlQuery(self.__db)
        if query.exec_(sql):
            ret = []
            while query.next():
                obj = self.__class__.__init__(self, self.__db)
                ret.append(obj)
                # 主キーを設定
                pk_idx = query.record().indexOf('id')
                setattr(self, '__pk', query.value(pk_idx).toBool())
                setattr(obj, '__pk', query.value(pk_idx).toBool())
                for column in self.get_columns():
                    idx = query.record().indexOf(column)
                    if isinstance(getattr(self, column), bool):
                        # BOOLEANの場合
                        setattr(self, column, query.value(idx).toBool())
                        setattr(obj, column, query.value(idx).toBool())
                    elif isinstance(getattr(self, column), int):
                        # INTEGERの場合
                        setattr(self, column, query.value(idx).toInt())
                        setattr(obj, column, query.value(idx).toInt())
                    elif isinstance(getattr(self, column), str):
                        # STRINGの場合
                        setattr(self, column, query.value(idx).toString())
                        setattr(obj, column, query.value(idx).toString())
        else:
            print query.lastError().text()
            return None

    def save(self):
        """メンバー変数の値をテーブルに保存する。

        pkが設定したらデータを更新する、設定しなかったらデータを追加とする。

        :return:
        """
        if not self.__db.isOpen():
            self.__db.open()
        if self.__db.lastError().isValid():
            print self.__db.lastError().text()
            return False

        if self.__pk:
            sql = self.get_update_sql()
        else:
            sql = self.get_insert_sql()
        query = QtSql.QSqlQuery(self.__db)
        if query.exec_(sql):
            print "%s saved!" % (self.get_table_name())
        else:
            print query.lastError().text()


class FindingOption(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.finding_history = []
        self.is_whole_word = False
        self.is_case_sensitive = False
        self.is_regular = False
        self.is_show_message = False
        self.is_auto_close = False
        self.is_research = False


class FindingHistory(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.finding_option_id = 0
        self.condition = ""


if __name__ == '__main__':
    setting = Setting()
