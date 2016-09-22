# coding: UTF-8

import os, sys
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
        self.db = db
        self.finding_option = FindingOption(db)
        self.finding_history = FindingHistory(db)
        if is_new:
            self.finding_option.create_table()
            self.finding_history.create_table()
        else:
            self.finding_option.load_settings()
            self.finding_history.load_settings()

    def test(self):
        self.finding_option.is_regular = False
        self.finding_option.is_auto_close = True
        self.finding_option.is_case_sensitive = True
        self.finding_option.is_research = True
        self.finding_option.is_show_message = True
        self.finding_option.is_whole_word = False
        self.finding_option.save()


class BaseOption:
    def __init__(self, db):
        self.__db = db
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
            if key.find('__') < 0 and not isinstance(value, list) and key != 'id':
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

    def load_settings(self, *args, **kwargs):
        """DBから項目の設定を取得する。

        :param args:
        :param kwargs:
        :return:
        """
        if not self.__db.isOpen():
            self.__db.open()
        if self.__db.lastError().isValid():
            print self.__db.lastError().text()
            return False

        sql = "SELECT * FROM %s" % (self.get_table_name(),)
        wheres = []
        for k, v in kwargs.items():
            wheres.append('%s=%s' % (k, v))
        else:
            if wheres:
                sql += " WHERE " + " AND ".join(wheres)
        query = QtSql.QSqlQuery(self.__db)
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
        else:
            print query.lastError().text()
            return None

        # リスト項目を設定
        for column in self.get_children():
            table_name = get_table_name_by_attr(column)
            sql = 'SELECT * FROM %s' % (table_name,)
            if query.exec_(sql):
                lst = getattr(self, column)
                while query.next():
                    child = get_class_by_name(table_name)(self.__db)
                    # 主キーを設定
                    pk_idx = query.record().indexOf('id')
                    setattr(child, 'id', query.value(pk_idx).toInt()[0])
                    # 項目を設定
                    for sub_column in child.get_columns():
                        idx = query.record().indexOf(sub_column)
                        if isinstance(getattr(child, sub_column), bool):
                            # BOOLEANの場合
                            setattr(child, sub_column, query.value(idx).toBool())
                        elif isinstance(getattr(child, sub_column), int):
                            # INTEGERの場合
                            setattr(child, sub_column, query.value(idx).toInt()[0])
                        elif isinstance(getattr(child, sub_column), str):
                            # STRINGの場合
                            setattr(child, sub_column, query.value(idx).toString())
                    lst.append(child)

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

        # 項目を保存する。
        if getattr(self, 'id') > 0:
            sql = self.get_update_sql()
            kbn = 'updated'
        else:
            sql = self.get_insert_sql()
            kbn = 'inserted'
        if not sql:
            return False
        query = QtSql.QSqlQuery(self.__db)
        if query.exec_(sql):
            print "%s(pk=%s) %s!" % (self.get_table_name(), self.id, kbn)
        else:
            print query.lastError().text()
            return False

        # リスト項目を保存する。
        for key, value in self.__dict__.items():
            if isinstance(value, list):
                for obj in value:
                    obj.save()


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
