#coding: UTF-8
#!/usr/bin/env python

from PyQt4 import QtGui
from PyQt4 import QtCore
from PyQt4 import QtSql


class DataTable:
    def __init__(self, name=''):
        self.Rows = []
        self.Columns = []
        self.name = name

    def add_row(self, row):
        self.Rows.append(row)
        row.Columns = self.Columns


class DataRow:
    def __init__(self):
        self.Columns = []
        self.Values = []

    def __getitem__(self, key):
        if isinstance(key, int):
            return self.Values[key]
        else:
            i = [col.name for col in self.Columns].index(key)
            return self.Values[i]


class DataColumn:
    def __init__(self, name='', t='', length=0):
        self.name = name
        self.type = t
        self.length = length
        self.precision = 0
        self.is_nullable = True
        self.description = ''
        self.is_primary_key = False

    def __str__(self):
        nullable = u"NULL"
        if not self.is_nullable:
            nullable += u"以外"
        return u"%s (%s、%s)" % (self.name, self.get_type_len(), nullable)

    def get_type_len(self):
        type_length = self.type
        if self.precision == 0:
            type_length += u'(%s)' % (self.length if self.length >=0 else 'max',)
        return type_length


class SqlQueryModel(QtCore.QAbstractTableModel):
    def __init__(self, data_table, parent=None):
        super(SqlQueryModel, self).__init__(parent)
        self.table = data_table

    def rowCount(self, index=None, *args, **kwargs):
        return len(self.table.Rows)

    def columnCount(self, index=None, *args, **kwargs):
        return len(self.table.Columns)

    def data(self, index, role=None):
        if not index.isValid():
            return QtCore.QVariant()
        if index.row() >= len(self.table.Rows) or index.row() < 0:
            return QtCore.QVariant()

        if role == QtCore.Qt.DisplayRole:
            data_row = self.table.Rows[index.row()]
            return data_row[index.column()]
        else:
            return QtCore.QVariant()

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.table.Columns[section].name
            elif orientation == QtCore.Qt.Vertical:
                return section + 1
        return QtCore.QVariant()


class SqlTableModel(QtSql.QSqlTableModel):
    def __init__(self, data_table, db, parent=None):
        super(SqlTableModel, self).__init__(parent, db)
        self.table = data_table


class TableItemDelegate(QtGui.QItemDelegate):
    def __init__(self, parent=None):
        super(TableItemDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.data().isNull():
            painter.fillRect(option.rect, QtGui.QBrush(QtGui.QColor(255, 255, 153)))
        super(TableItemDelegate, self).paint(painter, option, index)
