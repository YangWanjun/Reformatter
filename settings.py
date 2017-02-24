# coding: UTF-8

import os
import datetime
import sys
import common
import constants

from PyQt4 import QtSql
from PyQt4.QtCore import QFileInfo


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
        self.recently = Recently(db)
        if is_new:
            self.finding_option.create_table()
            FindingHistory(db).create_table()
            self.recently.create_table()
            OpenedFiles(db).create_table()
            Bookmarks(db).create_table()
            Database(db).create_table()
        else:
            self.finding_option.load_settings()
            self.recently.load_settings()

    def test(self):
        self.finding_option.is_regular = False
        self.finding_option.is_auto_close = True
        self.finding_option.is_case_sensitive = True
        self.finding_option.is_research = True
        self.finding_option.is_show_message = True
        self.finding_option.is_whole_word = False
        self.finding_option.save()


class BaseOption:

    ORDERS = ""

    def __init__(self, db):
        self.db = db
        self.id = 0

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
            if key.find('__') < 0 and not isinstance(value, list) and key not in ('db', 'id'):
                columns.append(key)
        return columns

    def get_children(self):
        """外部キー関連の項目を取得する。

        :return:
        """
        children = []
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                children.append(key)
        return children

    def get_child_foreign_key(self):
        letters = []
        for i in self.get_table_name():
            if not letters:
                letters.append(i.lower())
            elif i.isupper():
                letters.append('_' + i.lower())
            else:
                letters.append(i)
        return ''.join(letters) + "_id"

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
        if getattr(self, 'id') <= 0:
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
        return u"UPDATE %s SET %s WHERE id=%s" % (self.get_table_name(), ','.join(sql_cols), getattr(self, 'id'))

    def get_delete_sql(self):
        """データ削除用のSQLを取得する。

        pkが設定する必要ある、設定してなかったら、空白を戻す

        :return: SQL
        """
        if getattr(self, 'id') <= 0:
            return ''

        sql = 'DELETE FROM %s WHERE id=%s' % (self.get_table_name(), self.id)
        return sql

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
        elif isinstance(value, datetime.datetime):
            return ",%s DATETIME DEFAULT CURRENT_TIMESTAMP" % (name,)
        else:
            return ""

    def create_table(self):
        """テーブルを作成する。

        :return: なし
        """
        if not self.get_columns():
            return False
        if not self.db.isOpen():
            self.db.open()
        if self.db.lastError().isValid():
            print self.db.lastError().text()
            return False
        table_name = self.get_table_name()
        # テーブルが存在したら削除する。
        query = QtSql.QSqlQuery(self.db)
        if query.exec_("DROP TABLE IF EXISTS %s" % (table_name,)):
            print "Drop %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()

        # テーブル作成
        sql = self.get_create_table_sql()
        query = QtSql.QSqlQuery(self.db)
        if query.exec_(sql):
            print "Create %s Success!" % (table_name,)
        elif query.lastError().isValid():
            print query.lastError().text()
        else:
            print "Create %s Failure!" % (table_name,)

    def load_settings(self, *args, **kwargs):
        """DBから項目の設定を取得する。

        :param args:
        :param kwargs:
        :return:
        """
        if not self.db.isOpen():
            self.db.open()
        if self.db.lastError().isValid():
            print self.db.lastError().text()
            return False

        if self.get_columns():
            sql = "SELECT * FROM %s" % (self.get_table_name(),)
            wheres = []
            for k, v in kwargs.items():
                wheres.append('%s=%s' % (k, v))
            else:
                if wheres:
                    sql += " WHERE " + " AND ".join(wheres)
            query = QtSql.QSqlQuery(self.db)
            if query.exec_(sql):
                if query.next():
                    # 主キーを設定
                    pk_idx = query.record().indexOf('id')
                    setattr(self, 'id', query.value(pk_idx).toInt()[0])
                    # 項目を設定
                    for column in self.get_columns():
                        idx = query.record().indexOf(column)
                        if isinstance(getattr(self, column), bool):
                            # BOOLEANの場合
                            setattr(self, column, query.value(idx).toBool())
                        elif isinstance(getattr(self, column), int):
                            # INTEGERの場合
                            setattr(self, column, query.value(idx).toInt()[0])
                        elif isinstance(getattr(self, column), str):
                            # STRINGの場合
                            setattr(self, column, query.value(idx).toString())
                        elif isinstance(getattr(self, column), datetime.datetime):
                            # DATETIMEの場合
                            setattr(self, column, query.value(idx).toDateTime().toPyDateTime())
            else:
                print query.lastError().text()
                return None

        # リスト項目を設定
        for column in self.get_children():
            table_name = get_table_name_by_attr(column)
            obj_cls = get_class_by_name(table_name)
            if self.id > 0:
                sql = 'SELECT * FROM %s WHERE %s=%s %s' % (table_name,
                                                           self.get_child_foreign_key(),
                                                           self.id, obj_cls.ORDERS)
            else:
                sql = 'SELECT * FROM %s %s' % (table_name, obj_cls.ORDERS)
            query = QtSql.QSqlQuery(self.db)
            if query.exec_(sql):
                lst = getattr(self, column)
                while query.next():
                    child = obj_cls(self.db)
                    # 主キーを設定
                    pk_idx = query.record().indexOf('id')
                    setattr(child, 'id', query.value(pk_idx).toInt()[0])
                    # 項目を設定
                    child.load_settings(id=child.id)
                    # for sub_column in child.get_columns():
                    #     idx = query.record().indexOf(sub_column)
                    #     if isinstance(getattr(child, sub_column), bool):
                    #         # BOOLEANの場合
                    #         setattr(child, sub_column, query.value(idx).toBool())
                    #     elif isinstance(getattr(child, sub_column), int):
                    #         # INTEGERの場合
                    #         setattr(child, sub_column, query.value(idx).toInt()[0])
                    #     elif isinstance(getattr(child, sub_column), str):
                    #         # STRINGの場合
                    #         setattr(child, sub_column, query.value(idx).toString())
                    #     elif isinstance(getattr(child, sub_column), datetime.datetime):
                    #         # DATETIMEの場合
                    #         setattr(child, sub_column, query.value(idx).toDateTime().toPyDateTime())
                    lst.append(child)

    def save(self):
        """メンバー変数の値をテーブルに保存する。

        pkが設定したらデータを更新する、設定しなかったらデータを追加とする。

        :return:
        """
        if not self.db.isOpen():
            self.db.open()
        if self.db.lastError().isValid():
            print self.db.lastError().text()
            return False

        # 項目を保存する。
        if getattr(self, 'id') > 0:
            sql = self.get_update_sql()
            kbn = 'updated'
        else:
            sql = self.get_insert_sql()
            kbn = 'inserted'
        if not sql:
            return False
        query = QtSql.QSqlQuery(self.db)
        if query.exec_(sql):
            if kbn == 'inserted':
                self.id = query.lastInsertId().toInt()[0]
            print "%s(pk=%s) %s!" % (self.get_table_name(), self.id, kbn)
        else:
            print query.lastError().text()
            return False

        # # リスト項目を保存する。
        # for key, value in self.__dict__.items():
        #     if isinstance(value, list):
        #         for obj in value:
        #             obj.save()
        return True

    def delete(self):
        if getattr(self, 'id') > 0:
            sql = self.get_delete_sql()
            if not sql:
                return False
            if not self.db.isOpen():
                self.db.open()
            if self.db.lastError().isValid():
                print self.db.lastError().text()
                return False
            query = QtSql.QSqlQuery(self.db)
            if query.exec_(sql):
                print "%s(pk=%s) deleted!" % (self.get_table_name(), self.id)
                return True
        return False

    def delete_children(self, table_name):
        if not table_name:
            return False
        sql = 'DELETE FROM %s WHERE %s=%s' % (table_name, self.get_child_foreign_key(), self.id)
        query = QtSql.QSqlQuery(self.db)
        if query.exec_(sql):
            return True
        else:
            return False


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

    def add_history(self, text):
        text_list = [his.condition for his in self.finding_history]
        # 既に最後に追加された履歴なら、何もしない。
        if len(text_list) > 0 and text == text_list[-1]:
            return
        if text in text_list:
            idx = text_list.index(text)
            self.finding_history[idx].delete()
            del self.finding_history[idx]
        history = FindingHistory(self.db)
        history.finding_option_id = self.id
        history.condition = text
        history.save()
        self.finding_history.append(history)


class FindingHistory(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.finding_option_id = 0
        self.condition = ""


class Recently(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.opened_files = []
        self.database = []

    def get_files(self):
        file_list = [his for his in self.opened_files]
        file_list = sorted(file_list, key=lambda item: item.open_date, reverse=True)
        return [his.file_path for his in file_list]

    def get_file(self, filename):
        file_list = [his.file_path for his in self.opened_files]
        if filename in file_list:
            idx = file_list.index(filename)
            opened_file = self.opened_files[idx]
            return opened_file
        else:
            return None

    def get_folders(self):
        file_list = self.get_files()
        folder_list = [QFileInfo(file_path).absolutePath() for file_path in file_list]
        return list(set(folder_list))

    def add_file(self, filename):
        opened_file = self.get_file(filename)
        if opened_file:
            opened_file.open_date = datetime.datetime.now()
        else:
            opened_file = OpenedFiles(self.db)
            opened_file.file_path = filename
            self.opened_files.append(opened_file)
        opened_file.save()

    def add_db_connection(self, conn):
        conn.db = self.db
        self.database.append(conn)
        conn.save()

    def remove_database(self, conn_id):
        conn = self.get_saved_conn(conn_id)
        if conn:
            conn.delete()
            idx = self.database.index(conn)
            del self.database[idx]
            return True
        else:
            return False

    def rename_database(self, conn_id, new_name):
        conn = self.get_saved_conn(conn_id)
        if conn:
            conn.connection_name = new_name
            conn.save()
            return True
        else:
            return False

    def get_saved_conn(self, conn_id):
        conn = None
        for db in self.database:
            if db.id == conn_id:
                conn = db
                break
        return conn


class OpenedFiles(BaseOption):

    ORDERS = "ORDER BY open_date DESC"

    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.file_path = ""
        self.position = -1
        self.open_date = datetime.datetime.now()
        self.bookmarks = []

    def save(self, with_bookmark=False):
        BaseOption.save(self)
        if with_bookmark:
            self.delete_children(Bookmarks.__name__)
            for bookmark in self.bookmarks:
                bookmark.save()

    def add_bookmark(self, block_number):
        bookmark = Bookmarks(self.db)
        bookmark.opened_files_id = self.id
        bookmark.block_number = block_number
        self.bookmarks.append(bookmark)


class Bookmarks(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.block_number = -1
        self.opened_files_id = -1


class Database(BaseOption):
    def __init__(self, db):
        BaseOption.__init__(self, db)
        self.connection_name = ''
        self.database_type = ''
        self.server_name = ''
        self.port = ''
        self.database_name = ''
        self.auth_type = 0
        self.user_name = ''
        self.password = ''

    def check_input(self):
        if self.database_type == constants.DATABASE_SQL_SERVER:
            if self.auth_type == 0:
                # Sql Server認証
                return self.server_name and self.database_name and self.user_name and self.password
            else:
                # Windows認証
                return self.server_name and self.database_name
        elif self.database_type == constants.DATABASE_ORACLE:
            return self.database_name and self.user_name and self.password

        return False


def get_table_name_by_attr(key):
    """メンバー変数名からテーブル名を取得する。

    :param key:
    :return:
    """
    pieces = [i.capitalize() for i in key.split("_")]
    class_name = "".join(pieces)
    return class_name


def get_class_by_name(class_name):
    """クラス名から、クラスを取得する

    :param class_name:
    :return:
    """
    return getattr(sys.modules[__name__], class_name)


if __name__ == '__main__':
    setting = Setting()
    setting.test()
