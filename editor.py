#coding: UTF-8
#!/usr/bin/env python

import os
import re
import common, constants, settings
import functools

from PyQt4 import QtCore, QtGui, QtSql
from highlighter import SqlHighlighter
from sqlparser import SqlLexer, SqlParser, Node
from model import DataColumn, DataRow, DataTable, SqlQueryModel, SqlTableQueryModel, SqlTableModel, TableItemDelegate


class Editors(QtGui.QTabWidget):
    def __init__(self, parent, options):
        super(Editors, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.options = options

        self.untitled_name_index = 0
        self.setTabBar(EditorTabBar())
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.current_changed)

        css = '''
        QTabWidget::pane {
            border-top: 1px solid gray;
        }
        '''
        self.setStyleSheet(css)

    def add_editor(self, path):
        if path:
            filename = os.path.basename(unicode(path))
            editor = self.get_editor_by_path(path)
            if editor:
                editor.setWindowState(QtCore.Qt.WindowActive)
                editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
                self.setCurrentWidget(editor)
                return editor
        else:
            filename = self.get_untitled_name()

        editor = SqlEditor(self, path, options=self.options, connection=self.get_last_connection())
        self.addTab(editor, filename)
        self.setCurrentWidget(editor)
        if path:
            self.setTabToolTip(self.currentIndex(), path)
        editor.setWindowState(QtCore.Qt.WindowActive)
        editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        self.set_window_title()
        return editor.code_editor

    def add_table(self, table_name, connection):
        if connection is None:
            connection = self.get_main_window().connect_database()
        if connection:
            editor = SqlTable(self, table_name, connection, self.options)
            self.addTab(editor, table_name)
            self.setCurrentWidget(editor)
            editor.setWindowState(QtCore.Qt.WindowActive)
            editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
            self.set_window_title()
            return editor

    def add_table_edit(self, table_name, connection):
        if connection is None:
            connection = self.get_main_window().connect_database()
        if connection:
            editor = SqlTableEdit(self, table_name, connection, self.options)
            self.addTab(editor, table_name)
            self.setCurrentWidget(editor)
            editor.setWindowState(QtCore.Qt.WindowActive)
            editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
            self.set_window_title()
            return editor

    def open_file(self, path=None, codec=None, folder=None):
        if not path:
            if not folder:
                folder = ''
            path = QtGui.QFileDialog.getOpenFileName(self.parent(), u"開く", folder, "Sql Files (*.sql);;All Files(*.*)")

        if path:
            # 開いたファイルの履歴を保存する。
            self.options.recently.add_file(path)
            # メニューを更新する
            self.get_main_window().init_recent_files_menu()

            codec = codec if codec else constants.DEFAULT_CODEC_NAME
            editor = self.add_editor(path)
            editor.codec = codec
            in_file = QtCore.QFile(path)
            if in_file.isReadable():
                mode = QtCore.QFile.ReadWrite | QtCore.QFile.Text
            else:
                mode = QtCore.QFile.ReadOnly | QtCore.QFile.Text
                QtGui.QMessageBox.information(self, '', constants.MSG_FILE_READONLY)
            if in_file.open(mode):
                text_stream = QtCore.QTextStream(in_file)
                text_stream.setCodec(codec)
                text = text_stream.readAll()
                editor.bom = text_stream.generateByteOrderMark()
                editor.codec = str(text_stream.codec().name())
                editor.setPlainText(text)
                # editor.set_readonly(in_file.isReadable())
            else:
                QtGui.QMessageBox.information(self, '', constants.MSG_FILE_CANNOT_READ)

    def save_file(self):
        pass

    def save_as_file(self):
        pass

    def get_untitled_name(self):
        self.untitled_name_index += 1
        return constants.UNTITLED_FILE % (self.untitled_name_index,)

    def get_editor_by_path(self, path):
        if path:
            for i in range(self.count()):
                if hasattr(self.widget(i), 'code_editor'):
                    editor = self.widget(i).code_editor
                    if editor.path == path:
                        return editor
        return None

    def get_main_window(self):
        return self.parentWidget()

    def get_last_connection(self):
        for i in range(self.count()):
            tab = self.widget(i)
            if isinstance(tab, SqlEditor) or isinstance(tab, SqlTable):
                return tab.connection
        return None

    def set_window_title(self):
        if not self.currentWidget():
            return
        if hasattr(self.currentWidget(), 'get_file_path'):
            path = self.currentWidget().get_file_path()
            if path:
                title = path
            else:
                title = self.tabText(self.currentIndex())
        else:
            title = self.tabText(self.currentIndex())
        self.get_main_window().setWindowTitle(title)

    def removeTab(self, index):
        tab = self.widget(index)
        super(Editors, self).removeTab(index)
        tab.close()
        del tab
        if self.count() == 0:
            self.add_editor(None)

    def current_changed(self, index):
        self.set_window_title()
        tab = self.currentWidget()
        if isinstance(tab, SqlEditor) or isinstance(tab, SqlTable):
            self.get_main_window().init_db_toolbar(tab.connection)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                if event.key() == QtCore.Qt.Key_Tab:
                    self.move_to_next()
                    return False
            elif event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                if event.key() == QtCore.Qt.Key_Tab:
                    self.move_to_prev()
                    return False

        return QtCore.QObject.eventFilter(self, obj, event)

    def move_to_prev(self):
        old_position = self.currentIndex()
        new_position = old_position - 1 if old_position > 0 else self.count() - 1
        self.setCurrentIndex(new_position)

    def move_to_next(self):
        old_position = self.currentIndex()
        new_position = old_position + 1 if old_position + 1 < self.count() else 0
        self.setCurrentIndex(new_position)


class EditorTabBar(QtGui.QTabBar):
    def __init__(self, parent=None):
        super(EditorTabBar, self).__init__(parent)
        self.previous_index = -1
        self.setShape(QtGui.QTabBar.TriangularNorth)
        self.setMovable(True)
        self.setContentsMargins(0,0,0,0)

        css = '''
        QTabBar:tab {
            min-width: 70px;
            height: 20px;
            max-width: 300px;
            border: 1px solid gray;
            border-right: 1px solid gray;
            border-top-left-radius: 5px;
            border-top-right-radius: 5px;
            border-bottom-width: 0px;
        }
        QTabBar:tab:selected {
            color: blue;
            border-color: blue;
            background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                              stop: 0 #FFAA00, stop: 0.4 #FFFFFF);
        }
        '''
        self.setStyleSheet(css)

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.MidButton:
            self.previous_index = self.tabAt(mouse_event.pos())
        QtGui.QTabBar.mousePressEvent(self, mouse_event)

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.MidButton and self.previous_index == self.tabAt(mouse_event.pos()):
            self.parentWidget().removeTab(self.previous_index)
        self.previous_index = -1
        QtGui.QTabBar.mouseReleaseEvent(self, mouse_event)


class SqlEditorBase(QtGui.QWidget):
    def __init__(self, parent=None, options=None, connection=None):
        super(SqlEditorBase, self).__init__(parent)
        self.options = options
        self.connection = None
        self.table_list = None

        self.right_splitter = None
        self.bottom_splitter = None
        self.status_bar = None

        self.init_base_layout()
        self.set_connection(connection)

    def init_base_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)

        self.right_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
        self.bottom_splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)
        self.right_splitter.addWidget(self.bottom_splitter)

        # ステータスバー
        self.status_bar = EditorStatusBar(self)

        layout.addWidget(self.right_splitter)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def get_window_title(self):
        pass

    def set_connection(self, connection):
        self.connection = connection

    def execute_sql(self):
        pass

    def show_count_message(self, count):
        msg = u'%s 件のレコードが取得されました。' % (count,)
        self.status_bar.showMessage(msg)

    def show_bottom_window(self):
        pass

    def show_right_window(self):
        if self.table_list:
            if self.table_list.isVisible():
                self.table_list.setVisible(False)
            else:
                self.table_list.setVisible(True)

    def show_sql_error(self, last_error):
        if last_error.isValid():
            title = last_error.driverText()
            msg = last_error.databaseText()
            if msg.contains(u"通信リンク"):
                msg += u"\nもう1回実行してください。"
                self.connection.db.open()
            QtGui.QMessageBox.information(self, title, msg if msg else title)
            self.status_bar.showMessage(last_error.text())
            return True
        else:
            return False


class SqlEditor(SqlEditorBase):
    def __init__(self, parent=None, path=None, codec=None, options=None, connection=None):
        super(SqlEditor, self).__init__(parent, options, connection)
        self.code_editor = None
        self.param_widget = None
        self.param_splitter = None
        self.result_views = QtGui.QTabWidget()
        self.init_layout(path, codec)

        css = '''
        QSplitter::handle:vertical {
            height: 1px;
        }
        '''
        self.setStyleSheet(css)
        self.result_views.currentChanged.connect(self.current_result_changed)

    def init_layout(self, path, codec):
        # エディター
        self.code_editor = CodeEditor(self.bottom_splitter, path, codec, options=self.options)
        self.param_splitter = QtGui.QSplitter(QtCore.Qt.Horizontal, self)
        self.param_splitter.addWidget(self.code_editor)
        self.bottom_splitter.addWidget(self.param_splitter)

    def closeEvent(self, event):
        self.save_settings()

    def current_result_changed(self, index):
        table_view = self.result_views.widget(index)
        if table_view:
            count = table_view.model().rowCount()
            self.show_count_message(count)

    def execute_sql(self):
        params = self.get_parameters()
        # params が NULL の場合パラメータがない
        if params is not None:
            # params が 空白リストの場合、パラメーターダイアログでパラメータを入力する必要がある。
            if not params:
                return
        sql = self.code_editor.toPlainText()
        if not self.connection.is_open():
            self.connection.open()

        models = self.connection.execute_sql(sql, params)
        if not models:
            return
        # データ検索の場合
        if isinstance(models, list):
            self.result_views.clear()
            for model in models:
                self.show_select_result(model)
        elif isinstance(models, QtSql.QSqlError):
            self.show_sql_error(models)

    def get_file_path(self):
        return self.code_editor.path

    def get_parameters(self):
        parameters = self.code_editor.get_parameters()
        if parameters:
            if self.param_widget is None:
                self.param_widget = ParametersDialog(parameters, self)
                self.param_splitter.addWidget(self.param_widget)
                self.param_splitter.setSizes([700, 300])
                self.param_splitter.setStretchFactor(0, 1)
                self.param_splitter.setStretchFactor(1, 0)
                return []
            else:
                if not self.param_widget.isVisible():
                    self.param_widget.setVisible(True)
                self.param_widget.parameters = parameters
                if self.param_widget.init_layout():
                    return []
                else:
                    return self.param_widget.parameters
        else:
            if self.param_widget is not None:
                self.param_widget.hide()
            return None

    def show_select_result(self, query_model):
        last_error = self.connection.last_error()
        if not self.show_sql_error(last_error):
            table_view = SqlQueryView()
            table_view.setSortingEnabled(False)
            table_view.setModel(query_model)
            table_view.resizeColumnsToContents()
            self.result_views.addTab(table_view, u"結果%s" % (self.result_views.count() + 1,))
            self.bottom_splitter.addWidget(self.result_views)
            if not self.result_views.isVisible():
                self.result_views.setVisible(True)

    def show_bottom_window(self):
        if self.result_views.isVisible():
            self.result_views.setVisible(False)
        elif self.result_views.count() > 0:
            self.result_views.setVisible(True)

    def save_settings(self):
        if self.options:
            # 検索履歴を保存する。
            if self.options.finding_option:
                self.options.finding_option.save()
            # ブックマークを保存する。
            opened_file = self.options.recently.get_file(self.get_file_path())
            if opened_file and self.code_editor.bookmarks:
                opened_file.position = self.code_editor.textCursor().position()
                for bookmark in self.code_editor.bookmarks:
                    opened_file.add_bookmark(bookmark.blockNumber())
                opened_file.save(with_bookmark=True)


class SqlQueryView(QtGui.QTableView):
    def __init__(self, parent=None, is_show_filter=False):
        super(SqlQueryView, self).__init__(parent)
        # 行の高さを設定
        self.verticalHeader().setDefaultSectionSize(22)
        self.verticalHeader().setResizeMode(QtGui.QHeaderView.Fixed)
        # ヘッダーを設定
        self.setHorizontalHeader(SqlQueryHeader(is_show_filter=is_show_filter))
        # 初回サイズ設定時（resizeColumnsToContents）を呼び出す時
        self.is_first_resize = False

        css = '''
        QTableView {
            background-color: rgb(255, 251, 240);
            border: none;
        }
        '''
        self.setStyleSheet(css)
        delegate = TableItemDelegate()
        self.setItemDelegate(delegate)
        self.connect(self.horizontalScrollBar(), QtCore.SIGNAL('valueChanged(int)'), self.scroll_value_changed)
        self.connect(self.horizontalScrollBar(), QtCore.SIGNAL('rangeChanged(int, int)'), self.scroll_range_changed)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenu)

    def scroll_value_changed(self, value):
        self.horizontalHeader().hide_all_filters()

    def scroll_range_changed(self, min, max):
        self.horizontalHeader().hide_all_filters()

    def resizeColumnsToContents(self):
        self.is_first_resize = True
        super(SqlQueryView, self).resizeColumnsToContents()
        self.is_first_resize = False

    def sizeHintForColumn(self, column):
        width = super(SqlQueryView, self).sizeHintForColumn(column)
        header_width = self.horizontalHeader().get_section_width(column)
        if width > 300 and self.is_first_resize:
            return 300
        elif header_width > width:
            return header_width
        else:
            return width

    def onCustomContextMenu(self, point):
        index = self.indexAt(point)
        if index.isValid():
            menu = QtGui.QMenu(self)
            menu.addAction(u"コピー(&C)", self.copy_value)
            menu.addAction(u"ヘッダー付きコピー", lambda who=1: self.copy_value(who))
            menu.addAction(u"ヘッダー付きコピー(HTML形式)", lambda who=2: self.copy_value(who, is_html=True))
            point += QtCore.QPoint(self.verticalHeader().width(), self.horizontalHeader().height())
            menu.exec_(self.mapToGlobal(point))

    def copy_value(self, with_header=False, is_html=False):
        selected_list = self.selectedIndexes()
        # 必须按行重新排序，否则粘贴出来的东西会在同一列内
        selected_list.sort(key=lambda idx: idx.row())

        plain_text = ""
        html_text = ''
        current_row = 0
        column_list = []
        css = '''
        <style type="text/css">
        table {
            font-size: 13px;
        }
        tbody td { 
            border-style: solid;
            border-width: thin;
            white-space: nowrap;
            background-color: rgb(146,205,220);
        }
        .text {mso-number-format:"\@";}
        .num {mso-number-format:General;}
        .null_style {
            border-style: solid;
            border-width: thin;
            white-space: nowrap;
            background-color: rgb(255,255,204);
        }
        .header_style {
            font-weight: bold;
            border-style: solid;
            border-width: thin;
            background-color: rgb(242,242,242);
            white-space: nowrap;
        }
        .primary_key {
            color: red;
            font-weight: bold;
            border-style: solid;
            border-width: thin;
            background-color: rgb(242,242,242);
            white-space: nowrap;
        }
        .type_style {
            border-style: solid;
            border-width: thin;
            color: rgb(63,63,63);
            white-space: nowrap;
            background-color: rgb(242,242,242);
        }
        .type_nullable_style {
            border-style: solid;
            border-width: thin;
            color: rgb(63,63,63);
            white-space: nowrap;
            background-color: rgb(191,191,191);
        }
        </style>
        '''
        for i, index in enumerate(selected_list):
            if index.column() not in column_list:
                column_list.append(index.column())

            if i == 0:
                pass
            elif index.row() != current_row:
                plain_text += "\n"
                html_text += "</tr><tr>"
            else:
                plain_text += "\t"
                html_text += ''
            current_row = index.row()
            if index.data().isNull():
                plain_text += "NULL"
                html_text += '<td class="null_style">NULL</td>'
            else:
                column = self.model().table.Columns[index.column()]
                if unicode(column.type)[:8].lower() in ('datetime',):
                    plain_text += index.data().toDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz")
                    html_text += '<td class="text">%s</td>' % (index.data().toDateTime().toString("yyyy-MM-dd HH:mm:ss.zzz"),)
                elif unicode(column.type).lower() in ('int', 'smallint', 'bigint'):
                    plain_text += index.data().toString()
                    html_text += '<td>%s</td>' % (index.data().toString(),)
                elif index.data().toString() == ' ':
                    plain_text += index.data().toString()
                    html_text += '<td>&nbsp;</td>'
                else:
                    plain_text += index.data().toString()
                    html_text += '<td class="text">%s</td>' % (index.data().toString().replace(' ', '&nbsp;'),)

        plain_header_list = []
        plain_type_list = []
        html_header_list = []
        html_type_list = []
        for column in column_list:
            column = self.model().table.Columns[column]
            plain_name = unicode(column.name)
            plain_type_len = unicode(column.get_type_len())
            style = 'primary_key' if column.is_primary_key else 'header_style'
            html_name = '<td class="%s">%s</td>' % (style, plain_name,)
            style = 'type_nullable_style' if column.is_nullable else 'type_style'
            html_type_len = '<td class="%s">%s</td>' % (style, plain_type_len,)
            plain_header_list.append(plain_name)
            plain_type_list.append(plain_type_len)
            html_header_list.append(html_name)
            html_type_list.append(html_type_len)
        if with_header and plain_header_list and plain_type_list:
            plain_text = "\t".join(plain_header_list) + "\n" + "\t".join(plain_type_list) + "\n" + plain_text
            html_text = "<thead><tr>%s</tr><tr>%s</tr></thead><tbody><tr>%s</tr></tbody>" % ("".join(html_header_list), "".join(html_type_list), html_text)
        data = QtCore.QMimeData()
        if is_html:
            html = '<html><head><title></title>%s</head><body><div>%s</div><table cellspacing="0" cellpadding="0">%s</table></body></html>' % (css, self.model().table.name, html_text)
            data.setText(plain_text)
            data.setHtml(html)
        else:
            data.setText(plain_text)
        QtGui.QApplication.clipboard().setMimeData(data)

    def get_tab_window(self):
        parent_widget = self.parentWidget()
        while not isinstance(parent_widget, Editors):
            parent_widget = parent_widget.parentWidget()
        return parent_widget

    def keyPressEvent(self, event):
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            # Ctrl + Shift
            if event.key() == QtCore.Qt.Key_Backtab:
                # Ctrl + Shift + Tab
                self.get_tab_window().move_to_prev()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            # Ctrl
            if event.key() == QtCore.Qt.Key_C:
                self.copy_value()
            elif event.key() == QtCore.Qt.Key_Tab:
                # Ctrl + Tab
                self.get_tab_window().move_to_next()
            else:
                QtGui.QTableView.keyPressEvent(self, event)
        else:
            QtGui.QTableView.keyPressEvent(self, event)


class SqlQueryHeader(QtGui.QHeaderView):
    def __init__(self, parent=None, is_show_filter=False):
        super(SqlQueryHeader, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setClickable(True)
        self.columns = []
        self.equal_filters = []
        self.le_filters = []
        self.ge_filters = []
        self.like_filters = []
        self.order_filters = []
        self.is_show_filter = is_show_filter

        css = '''
        QHeaderView {
            border: 1px solid lightgray;
            border-left-width: 0px;
            border-top-width: 0px;
            border-right-width: 0px;
            background-color: rgb(255, 251, 240);
        }
        /**QHeaderView::section {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #616161, stop: 0.5 #505050,
                                              stop: 0.6 #434343, stop:1 #656565);
            color: white;
            padding-left: 4px;
            border: 1px solid #6c6c6c;
        }
        QHeaderView::section:checked
        {
            background-color: red;
        }**/
        /* style the sort indicator */
        QHeaderView::down-arrow {
            image: url(icons/arrow_down.png);
            width: 12px;
            height: 12px;
            subcontrol-position: right;
        }
        QHeaderView::up-arrow {
            image: url(icons/arrow_up.png);
            width: 12px;
            height: 12px;
            subcontrol-position: right;
        }
        QLineEdit {
            border-top: 1px solid rgb(217, 217, 217);
            border-left: 0px;
            border-right: 0px;
            border-bottom: 0px;
        }
        '''
        self.setStyleSheet(css)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenu)

    def onCustomContextMenu(self, point):
        menu = QtGui.QMenu(self)
        logical_index = self.logicalIndexAt(point)
        if logical_index >= 0:
            menu.addAction(u"非表示(&H)", lambda who=logical_index: self.hide_section(who))
            if self.is_show_filter:
                menu.addAction(u"絞り込み条件クリア(&C)", lambda who=logical_index: self.clear_filter(who))
        menu.addAction(u"全て表示(&A)", self.show_all_section)
        menu.exec_(self.mapToGlobal(point))

    def show_all_section(self):
        if self.sectionsHidden():
            for i in range(self.count()):
                if self.isSectionHidden(i):
                    self.setSectionHidden(i, False)

    def hide_section(self, logical_index):
        self.setSectionHidden(logical_index, True)
        # フィルターも一緒に非表示
        if self.is_show_filter:
            self.equal_filters[logical_index].hide()
            self.ge_filters[logical_index].hide()
            self.le_filters[logical_index].hide()
            self.like_filters[logical_index].hide()
            self.order_filters[logical_index].hide()

    def clear_filter(self, logical_index):
        if self.is_show_filter:
            self.equal_filters[logical_index].clear()
            self.ge_filters[logical_index].clear()
            self.le_filters[logical_index].clear()
            self.like_filters[logical_index].clear()
            self.order_filters[logical_index].clear()

    def sizeHint(self):
        base_size = QtGui.QHeaderView.sizeHint(self)
        if self.is_show_filter:
            base_size.setHeight(140)
        else:
            base_size.setHeight(44)
        return base_size

    def setModel(self, model):
        super(SqlQueryHeader, self).setModel(model)
        if isinstance(model, SqlQueryModel) or isinstance(model, SqlTableModel) or isinstance(model, SqlTableQueryModel):
            self.columns = model.table.Columns
            self.init_filters()

    def init_filters(self):
        if not self.is_show_filter:
            return
        if not self.columns:
            return
        if self.equal_filters:
            return

        for i, column in enumerate(self.columns):
            # ＝ の絞り込み条件
            txt = FilterLineEdit(self, u"＝")
            txt.hide()
            self.equal_filters.append(txt)
            # <= の絞り込み条件
            txt = FilterLineEdit(self, u"<=")
            txt.hide()
            self.le_filters.append(txt)
            # >= の絞り込み条件
            txt = FilterLineEdit(self, u">=")
            txt.hide()
            self.ge_filters.append(txt)
            # LIKE の絞り込み条件
            txt = FilterLineEdit(self, u"LIKE")
            txt.hide()
            self.like_filters.append(txt)
            # 並び順 の絞り込み条件
            txt = FilterLineEdit(self, u"ORDER BY")
            txt.hide()
            self.order_filters.append(txt)

    def get_section_width(self, index):
        if index < 0 or index >= self.count():
            return 0
        if not self.columns:
            return 0
        column = self.columns[index]
        type_len = column.get_type_len()
        font_metrics = QtGui.QFontMetrics(self.font())
        name_width = font_metrics.width(column.name)
        type_width = font_metrics.width(type_len)
        return name_width if name_width > type_width else type_width + 4

    def hide_all_filters(self):
        for i in range(len(self.equal_filters)):
            txt = self.equal_filters[i]
            txt.hide()
            txt = self.ge_filters[i]
            txt.hide()
            txt = self.le_filters[i]
            txt.hide()
            txt = self.like_filters[i]
            txt.hide()
            txt = self.order_filters[i]
            txt.hide()

    def get_where_clause(self):
        if self.equal_filters is None:
            self.equal_filters = {}
        if self.le_filters is None:
            self.le_filters = {}
        if self.ge_filters is None:
            self.ge_filters = {}
        if self.like_filters is None:
            self.like_filters = {}
        if self.order_filters is None:
            self.order_filters = {}

        sql = ''
        wheres = []
        for i, txt in enumerate(self.equal_filters):
            if txt.text():
                column = self.columns[i]
                wheres.append("[%s]='%s'" % (column.name, txt.text()))
        else:
            if wheres:
                sql += " AND " + " AND ".join(wheres)
        wheres = []
        for i, txt in enumerate(self.le_filters):
            if txt.text():
                column = self.columns[i]
                wheres.append("[%s]<='%s'" % (column.name, txt.text()))
        else:
            if wheres:
                sql += " AND " + " AND ".join(wheres)
        wheres = []
        for i, txt in enumerate(self.ge_filters):
            if txt.text():
                column = self.columns[i]
                wheres.append("[%s]>='%s'" % (column.name, txt.text()))
        else:
            if wheres:
                sql += " AND " + " AND ".join(wheres)
        wheres = []
        for i, txt in enumerate(self.like_filters):
            if txt.text():
                column = self.columns[i]
                wheres.append("[%s] LIKE '%s'" % (column.name, txt.text()))
        else:
            if wheres:
                sql += " AND " + " AND ".join(wheres)
        if sql:
            return sql[4:]
        else:
            return sql

    def get_order_clause(self):
        if not self.columns and not self.order_filters:
            return None

        orders = []
        reg = re.compile(r'^\s*(\d+)\s*(asc|desc){0,1}\s*$', re.I)
        for i, txt in enumerate(self.order_filters):
            if txt.text():
                column = self.columns[i]
                m = reg.match(unicode(txt.text()))
                if not m:
                    txt.setText('')
                    continue
                orders.append((m.group(1), m.group(2), column.name))
        if orders:
            orders.sort(key=lambda x:x[0])
            str_orders = ['%s%s' % (name, ' ' + o.upper() if o else '') for n, o, name in orders]
            return ', '.join(str_orders)
        else:
            return None

    def paintSection(self, painter, rect, logical_index):
        if self.columns:
            divide = 7 if self.is_show_filter else 2
            column = self.columns[logical_index]
            type_length = column.get_type_len()
            # 列名のスタイル
            t_rect = QtCore.QRect(rect.x(), rect.y(), rect.width()-1, rect.height() / divide)
            painter.save()
            QtGui.QHeaderView.paintSection(self, painter, t_rect, logical_index)
            painter.restore()
            # 列型、長さなどのスタイル
            painter.setPen(QtGui.QColor(216, 213, 204))
            painter.drawLine(rect.topRight(), rect.bottomRight())
            b_rect = QtCore.QRect(rect.x(), rect.y() + (rect.height() / divide), rect.width() - 1, rect.height() / divide)
            if self.is_show_filter and column.is_nullable:
                painter.fillRect(b_rect, QtGui.QBrush(QtGui.QColor(230, 230, 230)))
            if column.is_primary_key:
                painter.setPen(QtCore.Qt.red)
            else:
                painter.setPen(QtCore.Qt.black)
            painter.drawText(b_rect, QtCore.Qt.AlignCenter, type_length)

            if self.is_show_filter and not self.isSectionHidden(logical_index):
                # ＝ の絞り込み条件
                txt = self.equal_filters[logical_index]
                rect_eq = QtCore.QRect(rect.x() + 1, rect.y() + (rect.height() / divide) * 2, rect.width() - 2, rect.height() / divide)
                txt.setGeometry(rect_eq)
                txt.show()
                # >= の絞り込み条件
                txt = self.ge_filters[logical_index]
                rect_ge = QtCore.QRect(rect.x() + 1, rect.y() + (rect.height() / divide) * 3, rect.width() - 2, rect.height() / divide)
                txt.setGeometry(rect_ge)
                txt.show()
                # <= の絞り込み条件
                txt = self.le_filters[logical_index]
                rect_le = QtCore.QRect(rect.x() + 1, rect.y() + (rect.height() / divide) * 4, rect.width() - 2, rect.height() / divide)
                txt.setGeometry(rect_le)
                txt.show()
                # LIKE の絞り込み条件
                txt = self.like_filters[logical_index]
                rect_like = QtCore.QRect(rect.x() + 1, rect.y() + (rect.height() / divide) * 5, rect.width() - 2, rect.height() / divide)
                txt.setGeometry(rect_like)
                txt.show()
                # 並び順 の絞り込み条件
                txt = self.order_filters[logical_index]
                rect_odder = QtCore.QRect(rect.x() + 1, rect.y() + (rect.height() / divide) * 6, rect.width() - 2, rect.height() / divide + 3)
                txt.setGeometry(rect_odder)
                txt.show()
        else:
            QtGui.QHeaderView.paintSection(self, painter, rect, logical_index)


class FilterLineEdit(QtGui.QLineEdit):
    def __init__(self, parent, filter_type):
        super(FilterLineEdit, self).__init__(parent)
        self.filter_type = filter_type

    def paintEvent(self, event):
        super(FilterLineEdit, self).paintEvent(event)

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QColor(217, 217, 217))
        painter.drawText(0, 0, self.width(), self.height(), QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter, self.filter_type)


class SqlTableList(QtGui.QTreeWidget):
    def __init__(self, connection, parent=None):
        super(SqlTableList, self).__init__(parent)
        self.setHeaderHidden(True)
        self.connection = connection
        self.setColumnCount(1)

        css = '''
        QTreeWidget {
            background-color: rgb(255, 251, 240);
            width: 100px;
        }'''
        self.setStyleSheet(css)

        self.itemExpanded.connect(self.load_table_schema)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.onCustomContextMenu)

    def get_tab_widget(self):
        return self.parentWidget().parentWidget().parentWidget().parentWidget()

    def load_table_schema(self, item):
        if item.childCount() > 0:
            return

        table_name = item.text(0)
        for column in self.connection.get_table_schema(table_name):
            col_item = QtGui.QTreeWidgetItem(item)
            col_item.setData(0, QtCore.Qt.DisplayRole, unicode(column))
            col_item.setData(0, QtCore.Qt.UserRole, column.name)
            if column.is_primary_key:
                path = os.path.join(common.get_root_path(), r"icons/data_primary_key.png")
            else:
                path = os.path.join(common.get_root_path(), r"icons/data_column.png")
            col_item.setIcon(0, QtGui.QIcon(path))
            item.addChild(col_item)

    def onCustomContextMenu(self, point):
        item = self.itemAt(point)
        table_name = item.text(0)
        menu = QtGui.QMenu(self)
        user_data = item.data(0, QtCore.Qt.UserRole).toString()
        if user_data == ConnectionListDocker.CATEGORY_TABLE:
            menu.addAction(u"上位 256 件を抽出(&W)", lambda who=item: self.select_top_1000(item))
            menu.addAction(u"テーブルのデータ編集(&E)", lambda who=item: self.edit_top_200(item))
            menu.addSeparator()
        menu.addAction(u"コピー(&C)", lambda who=user_data: self.copy_name(table_name))
        menu.exec_(self.mapToGlobal(point))

    def select_top_1000(self, item):
        tab = self.get_tab_widget()
        if tab:
            table_name = item.text(0)
            tab.add_table(table_name, self.connection)

    def edit_top_200(self, item):
        tab = self.get_tab_widget()
        if tab:
            table_name = item.text(0)
            tab.add_table_edit(table_name, self.connection)

    def copy_name(self, table_name):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(table_name)


class SqlTable(SqlEditorBase):
    def __init__(self, parent, table_name, connection, options=None):
        super(SqlTable, self).__init__(parent, options, connection)
        self.table_name = table_name
        self.table_view = None

        self.init_layout()
        self.execute_sql()

    def init_layout(self):
        self.table_view = SqlQueryView(is_show_filter=True)
        self.bottom_splitter.addWidget(self.table_view)

    def get_where_clause(self):
        where_clause = self.table_view.horizontalHeader().get_where_clause()
        return where_clause

    def get_order_clause(self):
        return self.table_view.horizontalHeader().get_order_clause()

    def execute_sql(self, *args):
        model = self.connection.select_top_1000(self.table_name, self.get_where_clause(), self.get_order_clause())
        if not model:
            return
        if isinstance(model, SqlQueryModel) or isinstance(model, SqlTableQueryModel):
            self.table_view.setModel(model)
            self.table_view.resizeColumnsToContents()
            self.show_count_message(model.rowCount())
        elif isinstance(model, QtSql.QSqlError):
            self.show_sql_error(model)


class SqlTableEdit(SqlTable):
    def __init__(self, parent, table_name, connection, options=None):
        super(SqlTableEdit, self).__init__(parent, table_name, connection, options)

    def execute_sql(self, *args):
        model = self.connection.edit_top_200(self.table_name, self.get_where_clause(), args)
        if not model:
            return

        self.table_view.setModel(model)
        self.show_count_message(model.rowCount())


class CodeEditor(QtGui.QPlainTextEdit):

    CODEC_LIST = ['SJIS', 'UTF-8', 'UTF-16', 'UTF-32']
    LEFT_BRACKETS = ('(', '[', '{')
    RIGHT_BRACKETS = (')', ']', '}')
    BRACKETS = {'(': ')', '[': ']', '{': '}',
                ')': '(', ']': '[', '}': '{'}

    def __init__(self, parent=None, path=None, codec=None, options=None):
        super(CodeEditor, self).__init__(parent)
        self.path = path
        self.codec = codec
        self.bom = False
        self.finding = Finding(self, options.finding_option)
        self.option = EditorOption()
        self.options = options
        self.bookmarks = []
        self.is_re_parse = True
        self.parse_result = []
        self.parse_errors = []
        self.multi_select_start = None

        font = QtGui.QFont()
        font.setFamily(u'ＭＳ ゴシック')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(2)
        self.document().setDocumentMargin(1)
        self.setTabStopWidth(self.get_tab_space_width())
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)
        self.setHorizontalScrollBar(EditorScrollBar(self))
        self.setVerticalScrollBar(EditorScrollBar(self))
        self.setMouseTracking(True)

        self.line_number_area = LineNumberArea(self)
        self.ruler_area = RulerArea(self)
        self.tooltip = EditorToolTip(self)

        self.highlighter = SqlHighlighter(self.document())

        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.cursor_position_changed)
        self.connect(self, QtCore.SIGNAL('textChanged()'), self.text_changed)
        self.connect(self.tooltip, QtCore.SIGNAL('open_table(PyQt_PyObject)'), self.open_table)

        self.update_line_number_area_width()
        self.highlight_current_line()

        css = '''
        QPlainTextEdit {
            background-color: rgb(255, 251, 240);
            border: none;
        }
        '''
        self.setStyleSheet(css)
        self.frame = QtGui.QFrame(self)
        self.frame.setStyleSheet("QFrame {background-color: rgb(240, 240, 240);border: none;}")

    def init_bookmarks(self):
        if self.options and self.options.recently:
            opened_file = self.options.recently.get_file(self.path)
            if not opened_file:
                return
            for bookmark in opened_file.bookmarks:
                block = self.document().findBlockByNumber(bookmark.block_number)
                self.bookmarks.append(block)
            # 前回のカーソル位置に留める
            if opened_file.position > 0:
                cursor = self.textCursor()
                cursor.setPosition(opened_file.position)
                self.setTextCursor(cursor)
                self.centerCursor()

    def delete_left_space(self):
        self.delete_block_space(False)

    def delete_right_space(self):
        """
        行の右側（末尾）の空白を削除する。
        """
        self.delete_block_space(True)

    def delete_block_space(self, is_right):
        cursor = self.textCursor()
        if cursor.hasSelection():
            cursor.beginEditBlock()
            start_block, end_block = self.get_selected_blocks()
            if start_block and end_block:
                while start_block.isValid() and start_block.blockNumber() <= end_block.blockNumber():
                    block_cursor = QtGui.QTextCursor(start_block)
                    block_cursor.movePosition(QtGui.QTextCursor.EndOfBlock if is_right
                                              else QtGui.QTextCursor.StartOfBlock,
                                              QtGui.QTextCursor.MoveAnchor)
                    i = 1
                    reg = QtCore.QRegExp('\s+')
                    while (reg.exactMatch(start_block.text().right(i)) and is_right) \
                            or (reg.exactMatch(start_block.text().left(i)) and not is_right):
                        block_cursor.movePosition(QtGui.QTextCursor.Left if is_right else QtGui.QTextCursor.Right,
                                                  QtGui.QTextCursor.KeepAnchor)
                        i += 1
                    block_cursor.removeSelectedText()
                    start_block = start_block.next()
            cursor.endEditBlock()

    def comment_out(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        start_block, end_block = self.get_selected_blocks()
        if start_block and end_block:
            # コメントのマークを入れる位置を見つける
            comment_index = -1
            # コメントを設定／解除の区分
            is_remove = True
            while start_block.isValid() and start_block.blockNumber() <= end_block.blockNumber():
                block_cursor = QtGui.QTextCursor(start_block)
                reg = QtCore.QRegExp('[^\s]+')
                index = reg.indexIn(start_block.text())
                text = start_block.text()[index:index+2]
                is_remove = (is_remove and text == '--')
                if comment_index == -1 or comment_index > index:
                    comment_index = index
                start_block = start_block.next()
            start_block, end_block = self.get_selected_blocks()

            while start_block.isValid() and start_block.blockNumber() <= end_block.blockNumber():
                block_cursor = QtGui.QTextCursor(start_block)
                if is_remove:
                    position = start_block.position() + start_block.text().indexOf('--')
                    block_cursor.setPosition(position, QtGui.QTextCursor.MoveAnchor)
                    block_cursor.setPosition(position + 2, QtGui.QTextCursor.KeepAnchor)
                    block_cursor.removeSelectedText()
                else:
                    position = start_block.position() + comment_index
                    block_cursor.setPosition(position, QtGui.QTextCursor.MoveAnchor)
                    block_cursor.insertText('--')
                start_block = start_block.next()
        cursor.endEditBlock()

    def get_main_window(self):
        return self.get_tab_window().parentWidget()

    def get_tab_window(self):
        return self.parentWidget().parentWidget().parentWidget().parentWidget().parentWidget().parentWidget()

    def get_sql_editor(self):
        return self.parentWidget().parentWidget().parentWidget().parentWidget()

    def get_status_bar(self):
        if hasattr(self.get_sql_editor(), 'status_bar'):
            return self.get_sql_editor().status_bar
        else:
            return None

    def get_tab_space_width(self):
        """
        タブの幅を取得する。
        """
        return self.get_char_width() * common.get_tab_space_count()

    def get_line_height(self):
        return self.fontMetrics().height()

    def get_char_width(self):
        font = self.currentCharFormat().font()
        return round(QtGui.QFontMetricsF(font).averageCharWidth())

    def get_current_row_number(self):
        return self.textCursor().blockNumber() + 1

    def get_current_col_number(self):
        r = self.cursorRect(self.textCursor())
        left_offset = r.left() - self.contentOffset().x() - self.document().documentMargin()
        return int(left_offset / self.get_char_width()) + 1

    def get_selected_blocks(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            start_block = self.document().findBlock(cursor.selectionStart())
            end_block = self.document().findBlock(cursor.selectionEnd() - 1)
            return start_block, end_block
        else:
            return cursor.block(), cursor.block()

    def get_next_pair_cursor(self, text, current_cursor):

        def find_next(r, c, t, is_back=False):
            times = 1
            if is_back:
                args = [r, c, QtGui.QTextDocument.FindBackward]
            else:
                args = [r, c]
            cur = self.document().find(*args)
            while cur.position() >= 0 and times > 0:
                if cur.selectedText() != t:
                    times += 1
                else:
                    times -= 1
                if times == 0:
                    return cur
                else:
                    args[1] = cur
                    cur = self.document().find(*args)

        if text in CodeEditor.BRACKETS.values():
            pair = CodeEditor.BRACKETS[str(text)]
            reg = QtCore.QRegExp('\\' + text + '|\\' + pair)
            if text in CodeEditor.RIGHT_BRACKETS:
                cursor = find_next(reg, current_cursor, pair, True)
            else:
                cursor = find_next(reg, current_cursor, pair, False)
            return cursor
        else:
            return None

    def get_parameters(self):
        result, errors = self.get_parse_result()
        parameters = []
        if result and not errors:
            parameters = result.get_parameters()

        tmp = []
        ret_lst = []
        for param in parameters:
            if param.sql not in tmp:
                tmp.append(param.sql)
                ret_lst.append(param)
        return ret_lst

    def text_changed(self):
        self.is_re_parse = True

    def cursor_position_changed(self):
        """
        カーソルが変わる場合の処理
        """
        self.highlight_current_line()
        self.set_line_number()

    def line_number_area_width(self):
        digits = 1
        max_count = max(1, self.blockCount())
        while max_count >= 10:
            max_count /= 10
            digits += 1
        if digits < 3:
            digits = 3

        space = 12 + self.fontMetrics().width('9') * digits
        return space

    def keyPressEvent(self, event):
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            # Ctrl + Shift
            if event.key() == QtCore.Qt.Key_Backtab:
                # Ctrl + Shift + Tab
                self.get_tab_window().move_to_prev()
                return
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            # Ctrl
            if event.key() == QtCore.Qt.Key_Tab:
                # Ctrl + Tab
                self.get_tab_window().move_to_next()
                return
            elif event.key() == QtCore.Qt.Key_C and self.is_multi_select():
                self.multi_copy()
            elif event.key() == QtCore.Qt.Key_X and self.is_multi_select():
                self.multi_cut()
        else:
            cursor = self.textCursor()
            if cursor.hasSelection() and event.key() in (QtCore.Qt.Key_Space, QtCore.Qt.Key_Tab):
                start_block, end_block = self.get_selected_blocks()
                if start_block and end_block and start_block.blockNumber() != end_block.blockNumber():
                    cursor.beginEditBlock()
                    while start_block.isValid() and start_block.blockNumber() <= end_block.blockNumber():
                        block_cursor = QtGui.QTextCursor(start_block)
                        block_cursor.movePosition(QtGui.QTextCursor.StartOfBlock,
                                                  QtGui.QTextCursor.MoveAnchor)
                        block_cursor.insertText(event.text())
                        start_block = start_block.next()
                    cursor.endEditBlock()
                    return
            elif self.is_multi_select():
                if event.key() in (QtCore.Qt.Key_Escape,) \
                    or (event.key() >= QtCore.Qt.Key_Home and event.key() <= QtCore.Qt.Key_PageDown):
                    self.setExtraSelections([])
                elif event.text():
                    extra_selections = self.extraSelections()
                    cursor.beginEditBlock()
                    is_reset = True
                    for extra_selection in extra_selections:
                        if event.key() in (QtCore.Qt.Key_Backspace, QtCore.Qt.Key_Delete):
                            extra_selection.cursor.removeSelectedText()
                            is_reset = False
                        else:
                            insert_cursor = QtGui.QTextCursor(extra_selection.cursor)
                            start_position = insert_cursor.selectionStart()
                            insert_cursor.clearSelection()
                            insert_cursor.setPosition(start_position)
                            insert_cursor.insertText(event.text())
                    cursor.endEditBlock()
                    if is_reset:
                        self.setExtraSelections(extra_selections)
                    return
        super(CodeEditor, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        QtGui.QPlainTextEdit.mousePressEvent(self, event)
        btn = event.button()
        if btn == QtCore.Qt.LeftButton:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.WordUnderCursor)
                self.setTextCursor(cursor)
            elif event.modifiers() == QtCore.Qt.AltModifier:
                self.multi_select_start = event.pos()
            self.highlight_current_text()

    def mouseMoveEvent(self, event):
        if self.multi_select_start:
            self.multi_select(self.multi_select_start, event.pos())
        else:
            QtGui.QPlainTextEdit.mouseMoveEvent(self, event)
            cursor = self.cursorForPosition(event.pos())
            cursor.select(QtGui.QTextCursor.WordUnderCursor)
            rect = self.get_selection_rect(cursor)
            if not rect:
                self.tooltip.hide()
                return
            if not rect.contains(event.pos()):
                self.tooltip.hide()
                return
            text = cursor.selectedText()
            if not text:
                return
            result, errors = self.get_parse_result()
            if result and not errors:
                for node in result.get_child_nodes('identifier'):
                    if (node.sql == text and cursor.selectionStart() == node.lexpos) \
                            or (node.sql == '[' + text + ']' and cursor.selectionStart() + 1 == node.lexpos):
                        pos = rect.bottomLeft()
                        pos += QtCore.QPoint(self.line_number_area.width(), self.ruler_area.height())

                        if node.data_type == Node.TABLE_NAME:
                            self.tooltip.show_text(pos=pos, table_name=text)
                        elif node.data_type == Node.COLUMN_NAME:
                            table_name = node.get_table_name()
                            self.tooltip.show_text(pos=pos, table_name=table_name, column_name=text)
                        else:
                            self.tooltip.hide()
                        break

    def mouseReleaseEvent(self, event):
        QtGui.QPlainTextEdit.mouseReleaseEvent(self, event)
        self.multi_select_start = None

    def multi_select(self, point1, point2):
        cursor1 = self.cursorForPosition(point1)
        cursor2 = self.cursorForPosition(point2)
        if cursor1.blockNumber() < cursor2.blockNumber():
            start_block = cursor1.block()
            end_block = cursor2.block()
        else:
            start_block = cursor2.block()
            end_block = cursor1.block()

        extra_selections = QtGui.QTextEdit.extraSelections(QtGui.QTextEdit())
        while start_block.isValid() and start_block.blockNumber() <= end_block.blockNumber():
            block_cursor = QtGui.QTextCursor(start_block)
            y = self.cursorRect(block_cursor).y()
            position1 = self.cursorForPosition(QtCore.QPoint(point1.x(), y)).position()
            position2 = self.cursorForPosition(QtCore.QPoint(point2.x(), y)).position()
            block_cursor.setPosition(position1, QtGui.QTextCursor.MoveAnchor)
            block_cursor.setPosition(position2, QtGui.QTextCursor.KeepAnchor)
            start_block = start_block.next()

            selection = QtGui.QTextEdit.ExtraSelection()
            selection.format.setBackground(self.palette().color(QtGui.QPalette.Highlight))
            selection.format.setForeground(self.palette().color(QtGui.QPalette.HighlightedText))
            selection.cursor = block_cursor
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def is_multi_select(self):
        extra_selections = self.extraSelections()
        if not extra_selections:
            return False
        if extra_selections[0].format.background().color().rgb() != self.palette().color(QtGui.QPalette.Highlight).rgb():
            return False
        if extra_selections[0].format.foreground().color().rgb() != self.palette().color(QtGui.QPalette.HighlightedText).rgb():
            return False
        return True

    def multi_copy(self, is_cut=False):
        extra_selections = self.extraSelections()
        selected_text = ""
        for extra_selection in extra_selections:
            temp_text = unicode(extra_selection.cursor.selectedText())
            if selected_text:
                selected_text += "\r\n" + temp_text
            else:
                selected_text += temp_text
            if is_cut:
                extra_selection.cursor.removeSelectedText()
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(selected_text)

    def multi_cut(self):
        cursor = self.textCursor()
        cursor.beginEditBlock()
        self.multi_copy(is_cut=True)
        cursor.endEditBlock()

    def get_selection_rect(self, cursor):
        if not cursor.hasSelection():
            return None
        start_pos = cursor.selectionStart()
        end_pos = cursor.selectionEnd()
        start_cur = self.textCursor()
        start_cur.setPosition(start_pos, QtGui.QTextCursor.MoveAnchor)
        if not start_cur:
            return
        top_left = self.cursorRect(start_cur).topLeft()
        end_cur = self.textCursor()
        end_cur.setPosition(end_pos, QtGui.QTextCursor.MoveAnchor)
        if not end_cur:
            return
        bottom_right = self.cursorRect(end_cur).bottomRight()
        return QtCore.QRect(top_left, bottom_right)

    def paintEvent(self, event):
        super(CodeEditor, self).paintEvent(event)

        # 縦線を表示する。
        if self.get_current_col_number() > 1:
            self.draw_cursor_line(self.option.get_cursor_vline_color())
        self.draw_column_line(self.option.get_fixed_vline_no(), self.option.get_fixed_vline_color())
        self.draw_eof_mark()
        self.draw_return_mark(event)
        self.draw_full_space(event)
        # 横線を表示する。
        self.draw_horizontal_line(self.option.get_cursor_hline_color())

    def resizeEvent(self, event):
        QtGui.QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top() + self.ruler_area.height(), self.line_number_area_width(), cr.height()))
        self.ruler_area.setGeometry(QtCore.QRect(cr.left() + self.line_number_area_width(), cr.top(),
                                                 cr.width() - self.line_number_area_width(), 20))
        self.frame.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), self.ruler_area.height()))

    #def dragEnterEvent(self, event):
    #    if event.mimeData().hasFormat("text/plain"):
    #        event.acceptProposedAction()
    #
    #def dropEvent(self, event):
    #    text = event.mimeData().text()
    #    if text:
    #        cursor = self.cursorForPosition(event.pos())
    #        cursor.insertText(text)

    def highlight_current_text(self):
        cursor = self.textCursor()
        cursor.select(QtGui.QTextCursor.WordUnderCursor)
        text = cursor.selectedText()
        if not text:
            return
        if unicode(text)[0] in CodeEditor.BRACKETS:
            return
        result, errors = self.get_parse_result()
        if result and not errors:
            extra_selections = QtGui.QTextEdit.extraSelections(QtGui.QTextEdit())
            for node in result.get_child_nodes('identifier'):
                if (node.sql == text or node.sql == '[' + text + ']') and node.lexpos:
                    cursor = self.textCursor()
                    cursor.setPosition(node.lexpos)
                    cursor.select(QtGui.QTextCursor.WordUnderCursor)
                    current_word = QtGui.QTextEdit.ExtraSelection()
                    current_word.format.setBackground(QtGui.QColor(217, 217, 217))
                    current_word.cursor = cursor
                    extra_selections.append(current_word)
            self.setExtraSelections(extra_selections)

    def highlight_current_line(self):
        extra_selections = QtGui.QTextEdit.extraSelections(QtGui.QTextEdit())

        # 括弧を highlight
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        if unicode(text) not in CodeEditor.BRACKETS.values():
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
            text = cursor.selectedText()
        if unicode(text) in CodeEditor.BRACKETS.values():
            word_color = QtGui.QColor('#00FF00')
            current_word = QtGui.QTextEdit.ExtraSelection()
            format = current_word.format
            format.setBackground(word_color)
            format.setFontWeight(QtGui.QFont.Bold)
            format.setFontUnderline(True)
            format.setUnderlineColor(QtCore.Qt.red)
            current_word.format = format
            current_word.cursor = cursor
            paired_cursor = self.get_next_pair_cursor(text, cursor)
            if paired_cursor:
                paired_word = QtGui.QTextEdit.ExtraSelection()
                paired_word.format = format
                paired_word.cursor = paired_cursor
                extra_selections.append(current_word)
                extra_selections.append(paired_word)

        self.setExtraSelections(extra_selections)

    def highlight_text(self, reg):
        if reg and len(self.highlighter.text_highlight_list) == 1:
            old = self.highlighter.text_highlight_list[0]
            if old.pattern() == reg.pattern() and old.caseSensitivity() == reg.caseSensitivity():
                return
        del self.highlighter.text_highlight_list[:]
        if reg:
            self.highlighter.text_highlight_list.append(reg)
        self.highlighter.rehighlight()

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), self.ruler_area.height(), 0, 0)
        self.update_bookmark()

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        self.ruler_area.update(0, rect.y(), rect.width(), self.ruler_area.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

    def draw_horizontal_line(self, color):
        r = self.cursorRect(self.textCursor())
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(color)
        painter.drawLine(0, r.bottom() + 1, self.width(), r.bottom() + 1)
        self.viewport().update()

    def draw_column_line(self, col, color):
        left = round(self.get_char_width() * col)
        left += self.contentOffset().x() + self.document().documentMargin()

        painter = QtGui.QPainter(self.viewport())
        painter.setPen(color)
        painter.drawLine(left, 0, left, self.height())
        self.viewport().update()

    def draw_cursor_line(self, color):
        r = self.cursorRect(self.textCursor())
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(color)
        painter.drawLine(r.left(), 0, r.left(), self.height())
        self.viewport().update()

    def draw_eof_mark(self):
        cur = self.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        r = self.cursorRect(cur)
        painter = QtGui.QPainter(self.viewport())
        painter.setBrush(QtCore.Qt.black)
        painter.drawRect(QtCore.QRectF(r.left() + 2, r.top(), self.fontMetrics().width('[EOF]'), r.height()))
        painter.setPen(QtCore.Qt.white)
        painter.drawText(QtCore.QPointF(r.left() + 2, r.bottom()), "[EOF]")

    def draw_return_mark(self, event):
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtGui.QColor(75, 172, 198))

        block = self.firstVisibleBlock()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        cur = self.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        position_eof = cur.position()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible():
                cur.setPosition(block.position())
                cur.movePosition(QtGui.QTextCursor.EndOfBlock)
                if cur.position() == position_eof:
                    # 最後に改行がなく、EOF だった場合
                    break
                r = self.cursorRect(cur)
                painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"↵")

            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block = block.next()

    def draw_full_space(self, event):
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtCore.Qt.lightGray)

        block = self.firstVisibleBlock()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        reg = QtCore.QRegExp(ur'　|\t')

        while block.isValid() and top <= event.rect().bottom():
            cur = QtGui.QTextCursor(block)
            cur.movePosition(QtGui.QTextCursor.EndOfBlock)
            cur = self.document().find(reg, cur, QtGui.QTextDocument.FindBackward)
            text = cur.selectedText()
            while text and cur.position() >= block.position():
                cur.movePosition(QtGui.QTextCursor.Left)
                r = self.cursorRect(cur)
                if text == u'　':
                    painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"□")
                elif text == '\t':
                    painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"^")

                cur = self.document().find(reg, cur, QtGui.QTextDocument.FindBackward)
                text = cur.selectedText()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block = block.next()

    def show_find_dialog(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            self.finding.text = cursor.selectedText()
        find_dialog = FindDialog(self, self.finding)
        find_dialog.show()

    def show_jump_dialog(self):
        jump_dialog = JumpDialog(self, self.blockCount())
        jump_dialog.show()
        jump_dialog.txt_line_no.selectAll()

    def show_bookmarks_dialog(self):
        bookmarks_dialog = BookmarkDialog(self, self.bookmarks)
        bookmarks_dialog.show()

    def show_message_box(self, title, msg):
        QtGui.QMessageBox.information(self, title, msg)

    def find_text(self, is_back=False):
        self.finding.find_text(is_back)

    def set_line_number(self):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        status_bar = self.get_status_bar()
        if status_bar:
            position = self.textCursor().position()
            status_bar.set_line_number(self.get_current_row_number(),
                                       self.get_current_col_number(),
                                       self.textCursor().columnNumber() + 1,
                                       position)

    def set_status_msg(self, msg, timeout=0):
        status_bar = self.get_status_bar()
        if status_bar:
            status_bar.showMessage(msg)

    def select_lines(self, start_line, end_line=None):
        block = self.document().findBlockByLineNumber(start_line)
        if block.isValid():
            cursor = self.textCursor()
            cursor.setPosition(block.position(), QtGui.QTextCursor.MoveAnchor)
            if end_line is not None:
                # 複数行選択時
                end_block = self.document().findBlockByLineNumber(end_line)
                if start_line > end_line:
                    # 上の行を選択
                    if block.next().isValid():
                        cursor.setPosition(block.next().position(), QtGui.QTextCursor.MoveAnchor)
                    else:
                        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)

                    if end_block.isValid():
                        cursor.setPosition(end_block.position(), QtGui.QTextCursor.KeepAnchor)
                    else:
                        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.KeepAnchor)
                else:
                    # 下の行を選択
                    if end_block.isValid() and end_block.next().isValid():
                        cursor.setPosition(end_block.next().position(), QtGui.QTextCursor.KeepAnchor)
                    else:
                        cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.KeepAnchor)
            else:
                # 一行だけ選択時
                if block.next().isValid():
                    cursor.setPosition(block.next().position(), QtGui.QTextCursor.KeepAnchor)
                else:
                    cursor.select(QtGui.QTextCursor.LineUnderCursor)
            self.setTextCursor(cursor)

    def setPlainText(self, text):
        super(CodeEditor, self).setPlainText(text)
        self.codec = self.codec if self.codec else 'UTF-8'
        self.init_bookmarks()
        status_bar = self.get_status_bar()
        if status_bar:
            if self.bom:
                status_bar.set_codec(self.codec + u" BOM付")
            else:
                status_bar.set_codec(self.codec)

    def set_bookmark(self):
        cursor = self.textCursor()
        block = cursor.block()
        if block in self.bookmarks:
            self.bookmarks.remove(block)
        else:
            self.bookmarks.append(block)

    def next_bookmark(self):
        cursor = self.textCursor()
        block = cursor.block()
        self.finding.next_bookmark(block, self.bookmarks)

    def prev_bookmark(self):
        cursor = self.textCursor()
        block = cursor.block()
        self.finding.prev_bookmark(block, self.bookmarks)

    def update_bookmark(self):
        if self.bookmarks:
            for i in range(len(self.bookmarks) - 1, -1, -1):
                block = self.bookmarks[i]
                if self.document().findBlockByNumber(block.blockNumber()) != block:
                    del self.bookmarks[i]

    def clear_bookmark(self):
        del self.bookmarks[:]
        self.line_number_area.update()

    def jump_to_line(self, line_no):
        if line_no > self.blockCount():
            line_no = self.blockCount()
        elif line_no < 0:
            line_no = 0

        block = self.document().findBlockByLineNumber(line_no)
        cursor = QtGui.QTextCursor(block)
        self.setTextCursor(cursor)
        self.centerCursor()

    def get_parse_result(self):
        if self.is_re_parse:
            print 'reparsed'
            self.is_re_parse = False
            text = self.document().toPlainText()
            if not text:
                return None, None

            p = SqlParser()
            parser = p.build()
            l = SqlLexer()
            lexer = l.build()
            self.parse_result = parser.parse(unicode(text), lexer=lexer)
            self.parse_errors = p.errors + l.errors
        return self.parse_result, self.parse_errors

    def reformat(self):
        """
        ソース整形
        """
        result, errors = self.get_parse_result()
        if result and not errors:
            text = result.to_sql()
            cursor = QtGui.QTextCursor(self.document())
            cursor.beginEditBlock()
            cursor.select(QtGui.QTextCursor.Document)
            cursor.removeSelectedText()
            cursor.insertText(text)
            cursor.endEditBlock()
        if errors:
            for error in errors:
                print error
            self.set_status_msg(errors[0])

    def open_table(self, data):
        table_name = data['table_name']
        tab_window = self.get_tab_window()
        sql_editor = self.get_sql_editor()
        if tab_window and sql_editor:
            tab_window.add_table(table_name, sql_editor.connection)


class EditorOption:
    def __init__(self):
        pass

    def get_cursor_vline_color(self):
        color = QtGui.QColor(QtCore.Qt.blue).lighter(100)
        color.setAlpha(120)
        return color

    def get_fixed_vline_color(self):
        color = QtGui.QColor(QtCore.Qt.lightGray).lighter(100)
        color.setAlpha(120)
        return color

    def get_fixed_vline_no(self):
        return 100

    def get_cursor_hline_color(self):
        return QtGui.QColor(QtCore.Qt.blue)


class EditorStatusBar(QtGui.QStatusBar):
    def __init__(self, parent=None):
        super(EditorStatusBar, self).__init__(parent)
        self.setFixedHeight(22)
        
        css = '''
        QStatusBar {
            background-color: rgb(240, 240, 240);
            border-top: 1px solid lightgray;
        }
        QLabel {
            font-family: Courier;
            font-size: 10;
            padding-right: 5px;
            /* border: 1px inset gray; */
        }
        '''
        self.setStyleSheet(css)

        self.lbl_line_no = None
        self.lbl_codec = None
        self.init_layout()

    def init_layout(self):
        # 行番号、列番号を表示する。
        self.lbl_line_no = QtGui.QLabel()
        self.lbl_line_no.setText(u"%s 行 %s 列 %s 文字" % (1, 1, 1))
        self.addPermanentWidget(self.lbl_line_no)
        # エンコード
        self.lbl_codec = QtGui.QLabel()
        self.lbl_codec.setMinimumWidth(50)
        self.addPermanentWidget(self.lbl_codec)

    def set_line_number(self, line, col, length, position=0):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if self.lbl_line_no:
            self.lbl_line_no.setText(u"%s 行 %s 列 %s 文字 %s" % (line, col, length, position))

    def set_codec(self, name):
        if name and self.lbl_codec:
            self.lbl_codec.setText(name)


class EditorScrollBar(QtGui.QScrollBar):
    def __init__(self, parent):
        super(EditorScrollBar, self).__init__(parent)

        self.positions = []
        self.max_height = None

        css = '''
        /* 水平のスクロールバー */
        QScrollBar:horizontal {
            border: 1px solid grey;
            height: 15px;
            margin: 0px 34px 0 0px;
            opacity: 1;
        }

        QScrollBar::handle:horizontal {
            background: rgb(188, 188, 188);
            min-width: 20px;
        }

        QScrollBar::add-line:horizontal {
            border: 1px solid grey;
            width: 16px;
            subcontrol-position: right;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:horizontal {
            border: 1px solid grey;
            width: 16px;
            subcontrol-position: top right;
            subcontrol-origin: margin;
            position: absolute;
            right: 17px;
        }
        /* 縦のスクロールバー */
        QScrollBar:vertical {
            border: 1px solid grey;
            margin: 17px 0 17px 0;
        }
        QScrollBar::handle:vertical {
            background: rgb(188, 188, 188);
            min-height: 20px;
        }
        QScrollBar::handle:horizontal:hover ,
        QScrollBar::handle:vertical:hover {
            background: rgb(170, 170, 171);
        }
        QScrollBar::add-line:vertical {
            border: 1px solid grey;
            height: 16px;
            subcontrol-position: bottom;
            subcontrol-origin: margin;
        }

        QScrollBar::sub-line:vertical {
            border: 1px solid grey;
            height: 16px;
            subcontrol-position: top;
            subcontrol-origin: margin;
        }
        QScrollBar:left-arrow:horizontal, QScrollBar::right-arrow:horizontal,
        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            border: 1px solid grey;
            width: 3px;
            height: 3px;
            background: white;
        }

        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal,
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        '''
        # self.setStyleSheet(css)

    def paintEvent(self, event):
        super(EditorScrollBar, self).paintEvent(event)

        if self.orientation() == QtCore.Qt.Vertical and self.max_height and self.positions:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QColor(255, 150, 50))
            painter.setBrush(QtCore.Qt.yellow)
            painter.setOpacity(0.6)
            for pos in self.positions:
                y = self.get_position(pos)
                painter.drawRect(0, y, self.width(), 2)

    def get_position(self, position):
        relative = float(position) / self.max_height
        h1 = self.get_sub_line_height()
        h2 = self.get_add_line_height()
        y = (self.height() - h1 - h2) * relative
        return int(y) + h1

    def get_sub_line_height(self):
        option = QtGui.QStyleOptionSlider()
        option.initFrom(self)
        rect = self.style().subControlRect(QtGui.QStyle.CC_ScrollBar, option, QtGui.QStyle.SC_ScrollBarSubLine, self)
        return 18

    def get_add_line_height(self):
        option = QtGui.QStyleOptionSlider()
        option.initFrom(self)
        rect = self.style().subControlRect(QtGui.QStyle.CC_ScrollBar, option, QtGui.QStyle.SC_ScrollBarAddLine, self)
        return 18


class RulerArea(QtGui.QFrame):

    HEIGHT = 13

    def __init__(self, parent):
        super(RulerArea, self).__init__(parent)
        self.editor = parent
        self.setFixedHeight(RulerArea.HEIGHT)
        self.char_width = self.editor.fontMetrics().width('9')

        css = '''
        RulerArea {
            border-bottom: 1px solid black;
            background-color: rgb(240, 240, 240);
        }
        '''
        self.setStyleSheet(css)

    def paintEvent(self, event):
        super(RulerArea, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setPen(QtCore.Qt.black)

        offset = self.editor.contentOffset().x()
        count = (self.width() + abs(int(offset))) / self.char_width
        for i in range(count):
            left = i * self.char_width + offset
            if left < 0 or left > self.width():
                continue

            if i % 10 == 0:
                top = 2
                painter.drawText(left + 2, self.height() - 2, str(i / 10))
            elif i % 5 == 0:
                top = 5
            else:
                top = 9
            painter.drawLine(left + 1, top, left + 1, self.height())


class LineNumberArea(QtGui.QFrame):
    def __init__(self, parent):
        super(LineNumberArea, self).__init__(parent)
        self.editor = parent
        self.is_dragged = False
        self.select_start_line = -1
        self.select_end_line = -1

        font = QtGui.QFont()
        font.setFamily(u'ＭＳ ゴシック')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)

        css = '''
        LineNumberArea {
            border-right: 1px solid blue;
            background-color: rgb(240, 240, 240);
        }
        '''
        self.setStyleSheet(css)

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        super(LineNumberArea, self).paintEvent(event)
        painter = QtGui.QPainter(self)
        painter.setBrush(QtGui.QColor(0, 128, 192))

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if self.editor.bookmarks and block in self.editor.bookmarks:
                    painter.setPen(QtCore.Qt.white)
                    painter.drawRect(-1, top - 1, self.width(), self.editor.fontMetrics().height() + 1)
                else:
                    painter.setPen(QtCore.Qt.blue)
                painter.drawText(0, top, self.width() - 5, self.editor.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.editor.blockBoundingRect(block).height()
            block_number += 1

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == QtCore.Qt.LeftButton:
            line_no = self.editor.cursorForPosition(event.pos()).blockNumber()
            self.editor.select_lines(line_no)
            self.is_dragged = True
            self.select_start_line = line_no

    def mouseMoveEvent(self, event):
        if self.is_dragged:
            line_no = self.editor.cursorForPosition(event.pos()).blockNumber()
            self.editor.select_lines(self.select_start_line, line_no)

    def mouseReleaseEvent(self, event):
        self.is_dragged = False


class EditorToolTip(QtGui.QFrame):
    def __init__(self, parent):
        QtGui.QFrame.__init__(self, parent)
        self.btn_table_name = QtGui.QPushButton()
        self.lbl_comma = QtGui.QLabel('.')
        self.btn_column_name = QtGui.QPushButton()
        self.pos = None
        self.table_name = None
        self.column_name = None
        self.init_layout()
        self.setVisible(False)
        self.timer = QtCore.QTimer()
        self.timer.setInterval(500)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.show_in_timeout)

        css = '''
        EditorToolTip {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #F0F0F0, stop: 0.5 #FFFFFF,
                                              stop: 0.6 #FFFFFF, stop:1 #F0F0F0);
            color: white;
            border: 1px solid gray;
            padding: 2px;
        }
        QPushButton {
            margin: 0px;
            padding: 0px;
            border: 0px;
            color: blue;
            text-decoration: underline;
            text-align: left;
        }
        QPushButton:hover {
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                              stop:0 #F0F0F0, stop: 0.5 #FFFFFF,
                                              stop: 0.6 #FFFFFF, stop:1 #F0F0F0);
            color: red;
        }
        '''
        self.setStyleSheet(css)

    def init_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setMargin(2)
        layout.setSpacing(0)
        h_box = QtGui.QHBoxLayout()
        h_box.setMargin(0)
        h_box.setSpacing(0)
        # テーブル名
        self.btn_table_name.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_table_name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.btn_table_name.setToolTip(u"クリックすると、テーブルを開き、データ参照できます。")
        self.btn_table_name.setIcon(common.get_icon('data_table'))
        self.btn_table_name.clicked.connect(self.open_table)
        h_box.addWidget(self.btn_table_name)
        # コンマ
        h_box.addWidget(self.lbl_comma)
        # 列名
        self.btn_column_name.setCursor(QtCore.Qt.PointingHandCursor)
        self.btn_column_name.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        h_box.addWidget(self.btn_column_name)
        h_box.addStretch(0)

        layout.addLayout(h_box)
        self.setLayout(layout)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

    def show_text(self, pos=None, table_name=None, column_name=None):
        self.pos = pos
        self.table_name = table_name
        self.column_name = column_name
        self.timer.start()

    def show_in_timeout(self):
        QtGui.QFrame.hide(self)
        self.move(self.pos)
        if self.table_name and self.column_name:
            self.btn_table_name.setText(self.table_name)
            self.btn_table_name.setVisible(True)
            self.lbl_comma.setVisible(True)
            self.btn_column_name.setText(self.column_name)
            self.btn_column_name.setVisible(True)
            self.show()
        elif self.table_name:
            self.btn_table_name.setText(self.table_name)
            self.btn_table_name.setVisible(True)
            self.lbl_comma.setVisible(False)
            self.btn_column_name.setVisible(False)
            self.show()
        else:
            self.btn_table_name.setVisible(False)
            self.lbl_comma.setVisible(False)
            self.btn_column_name.setVisible(False)
            self.hide()

    def hide(self):
        QtGui.QFrame.hide(self)
        self.timer.stop()

    def text(self):
        lst = []
        if self.btn_table_name.isVisible() and self.btn_table_name.text():
            lst.append(unicode(self.btn_table_name.text()))
        if self.btn_column_name.isVisible() and self.btn_column_name.text():
            lst.append(unicode(self.btn_column_name.text()))
        return ".".join(lst)

    def open_table(self):
        table_name = self.btn_table_name.text()
        if table_name:
            self.emit(QtCore.SIGNAL("open_table(PyQt_PyObject)"), {"table_name": table_name})


class FindDialog(QtGui.QDialog):
    def __init__(self, parent, finding):
        super(FindDialog, self).__init__(parent)
        self.finding = finding
        self.txt_condition = None

        css = '''
        FindDialog {
            line-height: 1;
        }
        QCheckBox {
            margin: 0;
            padding: 0;
        }
        '''
        self.setStyleSheet(css)

        self.init_layout()
        self.setFixedSize(480, 150)
        self.setWindowTitle(u"検索")

    def init_layout(self):
        hbox = QtGui.QHBoxLayout()
        hbox.setSpacing(5)
        hbox.setMargin(10)
        left_vbox = QtGui.QVBoxLayout()
        left_vbox.setContentsMargins(-1, -1, -1, 0)
        right_vbox = QtGui.QVBoxLayout()

        # 検索文字列
        sub_hbox = QtGui.QHBoxLayout()
        label = QtGui.QLabel(u"条件(&N)")
        self.txt_condition = QtGui.QComboBox()
        self.txt_condition.setEditable(True)
        self.txt_condition.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        if self.finding and self.finding.option.finding_history:
            text_list = [his.condition for his in sorted(self.finding.option.finding_history,
                                                         key=lambda item:item.id, reverse=True)]
            self.txt_condition.addItems(text_list)
            self.txt_condition.setCurrentIndex(-1)
        if self.finding and self.finding.text:
            self.txt_condition.lineEdit().setText(self.finding.text)
            self.txt_condition.lineEdit().selectAll()
        label.setBuddy(self.txt_condition)
        sub_hbox.addWidget(label)
        sub_hbox.addWidget(self.txt_condition)
        left_vbox.addLayout(sub_hbox)
        left_vbox.addStretch()
        # 単語単位
        chk = QtGui.QCheckBox(u"単語単位で探す(&W)")
        if self.finding and self.finding.option.is_whole_word:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_whole_word)
        left_vbox.addWidget(chk)
        # 大文字と小文字を区別する
        chk = QtGui.QCheckBox(u"大文字と小文字を区別する(&C)")
        if self.finding and self.finding.option.is_case_sensitive:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_case_sensitive)
        left_vbox.addWidget(chk)
        # 正規表現
        chk = QtGui.QCheckBox(u"正規表現で探す(&E)")
        if self.finding and self.finding.option.is_regular:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_regular)
        left_vbox.addWidget(chk)
        # 見つからないときにメッセージ表示
        chk = QtGui.QCheckBox(u"見つからないときにメッセージ表示(&M)")
        if self.finding and self.finding.option.is_show_message:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_show_message)
        left_vbox.addWidget(chk)
        # 検索ダイアログを自動的に閉じる
        chk = QtGui.QCheckBox(u"検索ダイアログを自動的に閉じる(&L)")
        if self.finding and self.finding.option.is_auto_close:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_auto_close)
        left_vbox.addWidget(chk)
        # 先頭（末尾）から再検索する
        chk = QtGui.QCheckBox(u"先頭（末尾）から再検索する(&Z)")
        if self.finding and self.finding.option.is_research:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_research)
        left_vbox.addWidget(chk)

        # 上検索
        btn = QtGui.QPushButton(u"上検索(&U)")
        btn.clicked.connect(self.find_prev)
        right_vbox.addWidget(btn)
        # 下検索
        btn = QtGui.QPushButton(u"下検索(&D)")
        btn.clicked.connect(self.find_next)
        btn.setDefault(True)
        right_vbox.addWidget(btn)
        # キャンセル
        btn = QtGui.QPushButton(u"キャンセル(&X)")
        btn.clicked.connect(self.reject)
        right_vbox.addWidget(btn)
        right_vbox.addStretch()

        hbox.addLayout(left_vbox)
        hbox.addLayout(right_vbox)
        self.setLayout(hbox)

    def get_editor(self):
        return self.parentWidget()

    def set_whole_word(self, state):
        self.finding.option.is_whole_word = (state == QtCore.Qt.Checked)

    def set_case_sensitive(self, state):
        self.finding.option.is_case_sensitive = (state == QtCore.Qt.Checked)

    def set_regular(self, state):
        self.finding.option.is_regular = (state == QtCore.Qt.Checked)

    def set_show_message(self, state):
        self.finding.option.is_show_message = (state == QtCore.Qt.Checked)

    def set_auto_close(self, state):
        self.finding.option.is_auto_close = (state == QtCore.Qt.Checked)

    def set_research(self, state):
        self.finding.option.is_research = (state == QtCore.Qt.Checked)

    def find_next(self):
        self.finding.text = self.txt_condition.currentText()
        self.get_editor().finding = self.finding
        self.get_editor().find_text(False)
        if self.finding.option.is_auto_close:
            self.reject()

    def find_prev(self):
        self.finding.text = self.txt_condition.currentText()
        self.get_editor().finding = self.finding
        self.get_editor().find_text(True)
        if self.finding.option.is_auto_close:
            self.reject()


class JumpDialog(QtGui.QDialog):
    def __init__(self, parent, maximum):
        super(JumpDialog, self).__init__(parent)
        self.setModal(True)
        self.txt_line_no = None
        self.maximum = maximum
        self.editor = parent

        self.init_layout()
        self.setFixedSize(280, 70)
        self.setWindowTitle(u"指定行へジャンプ")

    def init_layout(self):
        layout = QtGui.QHBoxLayout()
        left_hbox = QtGui.QHBoxLayout()
        right_vbox = QtGui.QVBoxLayout()

        # 行番号
        label = QtGui.QLabel(u"行番号(&N)")
        self.txt_line_no = QtGui.QSpinBox()
        self.txt_line_no.setRange(1, self.maximum)
        label.setBuddy(self.txt_line_no)
        left_hbox.addWidget(label)
        left_hbox.addWidget(self.txt_line_no)
        left_hbox.addStretch()

        # ジャンプ
        btn = QtGui.QPushButton(u"ジャンプ(&J)")
        btn.clicked.connect(self.jump_to_line)
        btn.setDefault(True)
        right_vbox.addWidget(btn)
        # キャンセル
        btn = QtGui.QPushButton(u"キャンセル(&X)")
        btn.clicked.connect(self.reject)
        right_vbox.addWidget(btn)
        right_vbox.addStretch()

        layout.addLayout(left_hbox)
        layout.addLayout(right_vbox)
        self.setLayout(layout)

    def jump_to_line(self):
        line_no = self.txt_line_no.value()
        self.editor.jump_to_line(line_no - 1)
        self.accept()


class BookmarkDialog(QtGui.QDialog):
    def __init__(self, parent, bookmarks):
        super(BookmarkDialog, self).__init__(parent)
        self.editor = parent
        self.bookmarks = bookmarks

        self.setMinimumSize(400, 400)
        self.init_layout()
        self.setWindowTitle(u"ブックマーク")

        css = "QTreeView::branch {  border-image: url(none.png); }"
        self.setStyleSheet(css)

    def init_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        tree = QtGui.QTreeWidget(self)
        tree.setColumnCount(3)
        tree.setHeaderLabels(['', u"行番号", u"テキスト"])
        tree.resizeColumnToContents(1)
        tree.setColumnHidden(0, True)
        for bookmark in sorted(self.bookmarks, key=lambda item: item.blockNumber()):
            item = QtGui.QTreeWidgetItem(tree)
            item.setData(1, QtCore.Qt.DisplayRole, bookmark.blockNumber() + 1)
            item.setData(2, QtCore.Qt.DisplayRole, bookmark.text().trimmed().replace('\t', ''))
            tree.addTopLevelItem(item)
        tree.itemDoubleClicked.connect(self.jump_to_line)

        layout.addWidget(tree)
        self.setLayout(layout)

    def jump_to_line(self, item, column):
        line_number = item.data(1, QtCore.Qt.DisplayRole)
        no, ret = line_number.toInt()
        if ret:
            self.editor.jump_to_line(no - 1)


class ConnectionListDialog(QtGui.QDialog):
    def __init__(self, parent):
        super(ConnectionListDialog, self).__init__(parent)

        # self.init_layout()

    def init_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        tree = QtGui.QTreeWidget(self)
        tree.setColumnCount(3)
        tree.setHeaderLabels(['', u"接続名称", u"データベース名", u"接続状態"])
        tree.setColumnHidden(0, True)
        for i, connection_name in enumerate(Connection.get_connections()):
            db = QtSql.QSqlDatabase.database(connection_name, False)
            item = QtGui.QTreeWidgetItem(tree)
            item.setData(1, QtCore.Qt.DisplayRole, connection_name)
            item.setData(2, QtCore.Qt.DisplayRole, db.driverName())
            if db.isOpen():
                status = "Opened"
            else:
                status = "Closed"
            item.setData(3, QtCore.Qt.DisplayRole, status)
            tree.addTopLevelItem(item)
        tree.resizeColumnToContents(1)
        tree.setColumnWidth(2, 200)
        # tree.resizeColumnToContents(2)

        layout.addWidget(tree)
        self.setLayout(layout)
        width = tree.columnWidth(1) + tree.columnWidth(2) + tree.columnWidth(3) + 5
        self.resize(width, 300)


class ConnectionListDocker(QtGui.QDockWidget):

    TITLE = u"データベース接続"

    CATEGORY_TABLES = 'tables'
    CATEGORY_TABLE = 'table'
    CATEGORY_VIEWS = 'views'
    CATEGORY_VIEW = 'view'

    def __init__(self, parent):
        super(ConnectionListDocker, self).__init__(parent)
        self.tree = QtGui.QTreeWidget(self)
        self.connections = {}
        # self.drag_start_position = None

        self.init_layout()

        css = '''
        QTreeWidget {
            background-color: rgb(255, 251, 240);
        }
        QDockWidget {
            border: 5px solid lightgray;
        }
        QDockWidget::title {
            text-align: left;
            background: lightgray;
            padding-left: 35px;
        }
        '''
        self.setStyleSheet(css)
        self.setWindowTitle(ConnectionListDocker.TITLE)

    def init_layout(self):
        widget = QtGui.QWidget()
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        self.tree.setHeaderHidden(True)
        for conn in Connection.get_connections():
            self.add_connection(conn)
        layout.addWidget(self.tree)
        widget.setLayout(layout)
        self.setWidget(widget)

        self.tree.itemExpanded.connect(self.expand_item)
        self.tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.onCustomContextMenu)
        self.tree.setDragEnabled(True)

    def add_connection(self, conn):
        name = conn.get_connection_name()
        if unicode(name) not in self.connections:
            self.connections[name] = conn
            item = QtGui.QTreeWidgetItem(self.tree)
            item.setData(0, QtCore.Qt.DisplayRole, conn.get_connection_name())
            if conn.database_type == constants.DATABASE_SQL_SERVER:
                item.setIcon(0, common.get_icon('database_sqlserver'))
            self.add_category(item)
            self.tree.addTopLevelItem(item)

    def add_category(self, parent_item):
        item = QtGui.QTreeWidgetItem(parent_item)
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setData(0, QtCore.Qt.DisplayRole, u"テーブル")
        item.setData(0, QtCore.Qt.UserRole, ConnectionListDocker.CATEGORY_TABLES)
        item.setIcon(0, common.get_icon('folder'))
        parent_item.addChild(item)
        item = QtGui.QTreeWidgetItem(parent_item)
        item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
        item.setData(0, QtCore.Qt.DisplayRole, u"ビュー")
        item.setData(0, QtCore.Qt.UserRole, ConnectionListDocker.CATEGORY_VIEWS)
        item.setIcon(0, common.get_icon('folder'))
        parent_item.addChild(item)

    def get_top_level_item(self, item):
        parent = item.parent()
        if parent:
            return self.get_top_level_item(parent)
        else:
            return item

    def get_tab_widget(self):
        return self.parentWidget().editors

    def expand_item(self, item):
        if item.childCount() > 0:
            return

        category = item.data(0, QtCore.Qt.UserRole)
        conn_string = self.get_top_level_item(item).text(0)
        conn = self.connections[unicode(conn_string)]
        text = item.text(0)
        if category == ConnectionListDocker.CATEGORY_TABLES:
            self.load_tables(item, conn)
        elif category == ConnectionListDocker.CATEGORY_VIEWS:
            self.load_views(item, conn)
        elif category == ConnectionListDocker.CATEGORY_TABLE:
            self.load_columns(item, conn, text)

    def load_tables(self, parent_item, connection):
        for table in connection.get_tables():
            item = QtGui.QTreeWidgetItem(parent_item)
            item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.ShowIndicator)
            item.setData(0, QtCore.Qt.DisplayRole, table)
            item.setData(0, QtCore.Qt.UserRole, ConnectionListDocker.CATEGORY_TABLE)
            path = os.path.join(common.get_root_path(), r"icons/data_table.png")
            item.setIcon(0, QtGui.QIcon(path))
            parent_item.addChild(item)

    def load_views(self, parent_item, connection):
        for table in connection.get_views():
            item = QtGui.QTreeWidgetItem(parent_item)
            item.setChildIndicatorPolicy(QtGui.QTreeWidgetItem.DontShowIndicator)
            item.setData(0, QtCore.Qt.DisplayRole, table)
            item.setData(0, QtCore.Qt.UserRole, ConnectionListDocker.CATEGORY_VIEW)
            path = os.path.join(common.get_root_path(), r"icons/data_table.png")
            item.setIcon(0, QtGui.QIcon(path))
            parent_item.addChild(item)

    def load_columns(self, parent_item, connection, table_name):
        for column in connection.get_table_schema(table_name):
            col_item = QtGui.QTreeWidgetItem(parent_item)
            col_item.setData(0, QtCore.Qt.DisplayRole, unicode(column))
            col_item.setData(0, QtCore.Qt.UserRole, column.name)
            if column.is_primary_key:
                path = os.path.join(common.get_root_path(), r"icons/data_primary_key.png")
            else:
                path = os.path.join(common.get_root_path(), r"icons/data_column.png")
            col_item.setIcon(0, QtGui.QIcon(path))
            parent_item.addChild(col_item)

    def onCustomContextMenu(self, point):
        item = self.tree.itemAt(point)
        if not item:
            return
        conn_string = self.get_top_level_item(item).text(0)
        conn = self.connections[unicode(conn_string)]
        menu = QtGui.QMenu(self.tree)
        user_data = item.data(0, QtCore.Qt.UserRole).toString()
        if user_data == ConnectionListDocker.CATEGORY_TABLE:
            menu.addAction(u"上位 1000 件を抽出(&W)", lambda who=item: self.select_top_1000(who, conn))
            menu.addAction(u"テーブルのデータ編集(&E)", lambda who=item: self.edit_top_200(who, conn))
            menu.addSeparator()
        menu.addAction(u"コピー(&C)", lambda who=user_data: self.copy_name(item.text(0)))
        menu.exec_(self.tree.mapToGlobal(point))

    def select_top_1000(self, item, conn):
        tab = self.get_tab_widget()
        if tab:
            table_name = item.text(0)
            tab.add_table(table_name, conn)

    def edit_top_200(self, item, conn):
        tab = self.get_tab_widget()
        if tab:
            table_name = item.text(0)
            tab.add_table_edit(table_name, conn)

    #def mousePressEvent(self, event):
    #    super(ConnectionListDocker, self).mousePressEvent(event)
    #    if event.button() == QtCore.Qt.LeftButton:
    #        self.drag_start_position = event.pos()
    #        print self.drag_start_position
    #
    #def mouseMoveEvent(self, event):
    #    super(ConnectionListDocker, self).mouseMoveEvent(event)
    #    if not (event.buttons() == QtCore.Qt.LeftButton):
    #        return
    #    if not self.drag_start_position:
    #        return
    #    if (event.pos() - self.drag_start_position).manhattanLength() < QtGui.QApplication.startDragDistance():
    #        return
    #
    #    print 'mouseMoveEvent'
    #    item = self.itemAt(self.drag_start_position)
    #    drag = QtGui.QDrag(self)
    #    mime_data = QtCore.QMimeData()
    #    mime_data.setText(item.data(0, QtCore.Qt.UserRole).toString())
    #    drag.setMimeData(mime_data)
    #    dropAction = drag.exec_(QtCore.Qt.CopyAction)

    def copy_name(self, table_name):
        clipboard = QtGui.QApplication.clipboard()
        clipboard.setText(table_name)


class SqlDatabaseDialog(QtGui.QDialog):

    TITLE_SQL_SERVER = u"SqlServer接続"

    def __init__(self, parent=None, options=None):
        super(SqlDatabaseDialog, self).__init__(parent)
        self.conn_list = QtGui.QListWidget(self)
        self.connection = None
        self.options = options
        self.tabs = {}

        self.setModal(True)
        self.init_layout()
        self.setMinimumSize(600, 400)
        self.setWindowTitle(SqlDatabaseDialog.TITLE_SQL_SERVER)
        self.conn_list.itemChanged.connect(self.conn_list_edit_end)

        css = '''
        QFormLayout {
            width: 160px;
            border: 1px solid red;
        }
        '''
        self.setStyleSheet(css)

    def init_layout(self):
        layout = QtGui.QHBoxLayout()
        layout.setSpacing(5)
        layout.setMargin(10)

        # 接続リスト
        self.conn_list.setFixedWidth(250)
        self.conn_list.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.conn_list.customContextMenuRequested.connect(self.onCustomContextMenu)
        self.init_conn_list()

        # 接続タブ
        vbox = QtGui.QVBoxLayout()
        tab_sqlserver = SqlConnectTab(constants.DATABASE_SQL_SERVER, self)
        self.tabs[constants.DATABASE_SQL_SERVER] = tab_sqlserver
        tab_oracle = SqlConnectTab(constants.DATABASE_ORACLE, self)
        self.tabs[constants.DATABASE_ORACLE] = tab_oracle
        vbox.addWidget(tab_sqlserver)
        vbox.addWidget(tab_oracle)

        bottom_hbox = QtGui.QHBoxLayout()
        btn = QtGui.QPushButton(u"保存(&S)")
        btn.clicked.connect(self.save_connection)
        bottom_hbox.addWidget(btn)
        bottom_hbox.addStretch()
        btn = QtGui.QPushButton(u"接続(&C)")
        btn.setDefault(True)
        btn.clicked.connect(self.connect_database)
        bottom_hbox.addWidget(btn)
        btn = QtGui.QPushButton(u"キャンセル(&X)")
        btn.clicked.connect(self.reject)
        bottom_hbox.addWidget(btn)
        bottom_hbox.addStretch()
        vbox.addLayout(bottom_hbox)

        layout.addWidget(self.conn_list)
        layout.addLayout(vbox)
        self.setLayout(layout)

        self.conn_list.setCurrentRow(0)
        self.select_conn_type(self.conn_list.item(0))

    def init_conn_list(self, selected_text=''):
        self.conn_list.clear()

        for conn in self.options.recently.database:
            if conn.database_type == constants.DATABASE_SQL_SERVER:
                icon = common.get_icon('database_sqlserver')
            else:
                icon = common.get_icon('database_oracle')
            item = QtGui.QListWidgetItem(icon, conn.connection_name, self.conn_list)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            item.setData(QtCore.Qt.UserRole, conn.id)
            self.conn_list.addItem(item)
            if selected_text and selected_text == conn.connection_name:
                self.conn_list.setCurrentItem(item)

        item = QtGui.QListWidgetItem(constants.DATABASE_SQL_SERVER, self.conn_list)
        item.setData(QtCore.Qt.UserRole, 0)
        self.conn_list.addItem(item)
        item = QtGui.QListWidgetItem(constants.DATABASE_ORACLE, self.conn_list)
        item.setData(QtCore.Qt.UserRole, 0)
        self.conn_list.addItem(item)
        self.conn_list.itemClicked.connect(self.select_conn_type)

    def conn_list_edit_end(self, item):
        conn_id = item.data(QtCore.Qt.UserRole).toInt()[0]
        self.options.recently.rename_database(conn_id, item.text())

    def onCustomContextMenu(self, point):
        item = self.conn_list.itemAt(point)
        if not item:
            return

        conn_id = item.data(QtCore.Qt.UserRole).toInt()[0]
        if conn_id > 0:
            menu = QtGui.QMenu(self.conn_list)
            menu.addAction(u"コピー(&C)", lambda who=conn_id: self.copy_conn(who))
            menu.addAction(u"削除(&D)", lambda who=conn_id: self.delete_conn(who))
            menu.addAction(u"名前の変更(&M)", lambda who=conn_id: self.rename_conn(who))
            menu.exec_(self.mapToGlobal(point))

    def copy_conn(self, conn_id):
        conn = self.options.recently.get_saved_conn(conn_id)
        if conn:
            item = self.get_conn_item_by_name(conn.database_type)
            if item:
                self.conn_list.setCurrentItem(item)

    def delete_conn(self, conn_id):
        if self.options.recently.remove_database(conn_id):
            self.init_conn_list()

    def rename_conn(self, conn_id):
        conn = self.options.recently.get_saved_conn(conn_id)
        item = self.get_conn_item_by_name(conn.connection_name)
        if item:
            self.conn_list.editItem(item)

    def get_conn_item_by_name(self, name):
        items = self.conn_list.findItems(name, QtCore.Qt.MatchExactly | QtCore.Qt.MatchCaseSensitive)
        if items and len(items) == 1:
            return items[0]
        else:
            return None

    def select_conn_type(self, item):
        for tab in self.tabs.values():
            tab.hide()

        name = unicode(item.text())
        conn_id = item.data(QtCore.Qt.UserRole).toInt()[0]
        conn = self.options.recently.get_saved_conn(conn_id)
        if name in self.tabs and conn_id == 0:
            tab = self.tabs[name]
            tab.show()
            tab.clear_input()
        elif conn and str(conn.database_type) in self.tabs:
            tab = self.tabs[str(conn.database_type)]
            tab.show()
            tab.set_connection(conn)

    def connect_database(self):
        tab = self.get_current_tab()
        if not tab:
            return
        conn = tab.get_connection()
        if not conn:
            return
        if conn.check_input():
            connection = Connection(conn.database_type, conn.server_name, conn.database_name, conn.auth_type,
                                    conn.user_name, conn.password)
            if connection.is_open():
                self.connection = connection
                self.accept()
                # self.emit(QtCore.SIGNAL("connected(PyQt_PyObject)"), {"connection": connection})
            elif connection.open():
                connection.close()
                self.connection = connection
                self.accept()
                # self.emit(QtCore.SIGNAL("connected(PyQt_PyObject)"), {"connection": connection})
            else:
                error = connection.last_error()
                if error:
                    msg = error.text()
                else:
                    msg = u"データベールに接続できません！"
                QtGui.QMessageBox.information(self, SqlDatabaseDialog.TITLE_SQL_SERVER, msg)
        else:
            QtGui.QMessageBox.information(self, SqlDatabaseDialog.TITLE_SQL_SERVER, u"入力してない項目があります！")

    def save_connection(self):
        tab = self.get_current_tab()
        if not tab:
            return
        conn = tab.get_connection()
        if not conn:
            return
        if conn.id > 0:
            conn.save()
        else:
            dialog = ConnectionNameDialog(self, conn.database_name, conn.server_name, conn.user_name, self.options)
            if dialog.exec_() and dialog.get_conn_name():
                conn.connection_name = dialog.get_conn_name()
                self.options.recently.add_db_connection(conn)
                self.init_conn_list(dialog.get_conn_name())

    def get_current_tab(self):
        for key, tab in self.tabs.items():
            if tab.isVisible():
                return tab
        return None


class SqlConnectTab(QtGui.QWidget):
    def __init__(self, database_type, parent=None):
        super(SqlConnectTab, self).__init__(parent)
        self.database_type = database_type

        self.txt_server_name = None
        self.txt_port = None
        self.txt_database_name = None
        self.cmb_authentication = None
        self.txt_username = None
        self.txt_password = None

        if database_type == constants.DATABASE_SQL_SERVER:
            self.init_mssql_layout()
        elif database_type == constants.DATABASE_ORACLE:
            self.init_oracle_layout()

    def init_mssql_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setMargin(10)
        form = QtGui.QFormLayout()
        form.setMargin(0)
        self.txt_server_name = QtGui.QLineEdit()
        form.addRow(u"サーバー名(&S)：", self.txt_server_name)

        self.txt_database_name = QtGui.QLineEdit()
        form.addRow(u"データベース名(&D)：", self.txt_database_name)

        self.cmb_authentication = QtGui.QComboBox()
        self.cmb_authentication.addItem(u"Sql Server認証", 0)
        self.cmb_authentication.addItem(u"Windows認証", 1)
        self.cmb_authentication.currentIndexChanged.connect(self.change_mssql_auth)
        form.addRow(u"認証(&A):", self.cmb_authentication)

        self.txt_username = QtGui.QLineEdit()
        self.txt_username.setEnabled(True)
        form.addRow(u"ユーザ名(&U)：", self.txt_username)

        self.txt_password = QtGui.QLineEdit()
        self.txt_password.setEchoMode(QtGui.QLineEdit.Password)
        form.addRow(u"パスワード(&P)：", self.txt_password)

        layout.addLayout(form)
        layout.addStretch()
        self.setLayout(layout)

    def init_oracle_layout(self):
        layout = QtGui.QVBoxLayout()
        form = QtGui.QFormLayout()
        form.setMargin(0)
        #self.txt_server_name = QtGui.QLineEdit()
        #form.addRow(u"ホスト名(&H)：", self.txt_server_name)
        #
        #self.txt_port = QtGui.QLineEdit('1521')
        #self.txt_port.setFixedWidth(80)
        #form.addRow(u"ポート番号(&O)：", self.txt_port)

        self.txt_database_name = QtGui.QLineEdit()
        form.addRow(u"ＴＮＳ名(&S)：", self.txt_database_name)

        self.txt_username = QtGui.QLineEdit()
        self.txt_username.setEnabled(True)
        form.addRow(u"ユーザ名(&U)：", self.txt_username)

        self.txt_password = QtGui.QLineEdit()
        self.txt_password.setEchoMode(QtGui.QLineEdit.Password)
        form.addRow(u"パスワード(&P)：", self.txt_password)

        layout.addLayout(form)
        layout.addStretch()

        self.setLayout(layout)

    def change_mssql_auth(self, index):
        if index == 0:
            self.txt_username.setEnabled(True)
            self.txt_password.setEnabled(True)
        else:
            self.txt_username.setEnabled(False)
            self.txt_password.setEnabled(False)

    def clear_input(self):
        if self.txt_server_name:
            self.txt_server_name.setText('')
        if self.txt_port:
            self.txt_port.setText('1521')
        self.txt_database_name.setText('')
        if self.cmb_authentication:
            self.cmb_authentication.setCurrentIndex(0)
        self.txt_username.setText('')
        self.txt_password.setText('')

    def get_connection(self):
        server_name = self.txt_server_name.text() if self.txt_server_name else ''
        database_name = self.txt_database_name.text()
        user_name = self.txt_username.text()
        password = self.txt_password.text()
        conn = settings.Database(None)
        conn.database_type = self.database_type
        conn.server_name = server_name
        conn.database_name = database_name
        conn.user_name = user_name
        conn.password = password
        if self.cmb_authentication:
            auth_type = self.cmb_authentication.currentIndex()
            conn.auth_type = auth_type
        if self.txt_port:
            conn.port = self.txt_port.text()
        return conn

    def set_connection(self, conn):
        if not conn:
            return

        if self.txt_server_name:
            self.txt_server_name.setText(conn.server_name)
        if self.txt_port:
            self.txt_port.setText(conn.port)
        self.txt_database_name.setText(conn.database_name)
        if self.cmb_authentication:
            self.cmb_authentication.setCurrentIndex(conn.auth_type)
        self.txt_username.setText(conn.user_name)
        self.txt_password.setText(conn.password)


class ConnectionNameDialog(QtGui.QDialog):
    def __init__(self, parent=None, db_name='', server_name='', user_name='', options=None):
        super(ConnectionNameDialog, self).__init__(parent)
        self.txt_conn_name = QtGui.QLineEdit(common.get_default_conn_name(db_name, server_name, user_name))
        self.options = options

        self.setFixedSize(300, 80)
        self.init_layout()
        self.setWindowTitle(SqlDatabaseDialog.TITLE_SQL_SERVER)

    def init_layout(self):
        layout = QtGui.QVBoxLayout()
        hbox1 = QtGui.QHBoxLayout()
        label = QtGui.QLabel(u"接続名称(&C)")
        label.setBuddy(self.txt_conn_name)
        hbox1.addWidget(label)
        hbox1.addWidget(self.txt_conn_name)

        button_box = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel, QtCore.Qt.Horizontal)
        self.connect(button_box, QtCore.SIGNAL('accepted()'), self.accept)
        self.connect(button_box, QtCore.SIGNAL('rejected()'), self.reject)

        layout.addLayout(hbox1)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def get_conn_name(self):
        return self.txt_conn_name.text()

    def accept(self):
        if self.get_conn_name():
            if self.options.recently.get_saved_conn(self.get_conn_name()):
                QtGui.QMessageBox.information(self, SqlDatabaseDialog.TITLE_SQL_SERVER, u"既に存在している接続名称です。")
            else:
                super(ConnectionNameDialog, self).accept()


class ParametersDialog(QtGui.QWidget):
    def __init__(self, parameters, parent=None):
        super(ParametersDialog, self).__init__(parent)
        self.parameters = parameters

        self.init_layout()

    def init_layout(self):
        form = self.findChild(QtGui.QFormLayout)
        if form is None:
            form = QtGui.QFormLayout()
            for parameter in self.parameters:
                txt = QtGui.QLineEdit()
                txt.setObjectName(parameter.sql)
                form.addRow(parameter.sql, txt)
            self.setLayout(form)
            return True
        else:
            if self.is_reset_layout(form):
                # レイアウト再設定必要
                self.reset_layout(form)
                return True
            else:
                # レイアウト再設定必要ない、このままパラメータの値を取得する。
                return False

    def is_reset_layout(self, form):
        if len(self.parameters) == self.get_row_count():
            for parameter in self.parameters:
                txt = self.findChild(QtGui.QLineEdit, parameter.sql)
                if txt is None:
                    return True
                else:
                    parameter.value = txt.text()
            return False
        else:
            return True

    def reset_layout(self, form):
        for parameter in self.parameters:
            txt = self.findChild(QtGui.QLineEdit, parameter.sql)
            if txt is None:
                # 存在しない場合は、一行追加する
                txt = QtGui.QLineEdit()
                txt.setObjectName(parameter.sql)
                form.addRow(parameter.sql, txt)
        for i in range(self.get_row_count()):
            item = form.itemAt(i * 2 + 1)
            if not item:
                continue
            txt = item.widget()
            params = [param for param in self.parameters if param.sql == txt.objectName()]
            if params and len(params) == 1:
                pass
            else:
                # パラメーターのテキストボックスを削除する。
                label = form.labelForField(txt)
                if label:
                    label.deleteLater()
                txt.deleteLater()

    def get_row_count(self):
        form = self.findChild(QtGui.QFormLayout)
        count = 0
        if form:
            for i in range(form.rowCount()):
                item = form.itemAt(i * 2 + 1)
                if item:
                    count += 1
        return count


class Finding:
    def __init__(self, editor, option):
        self.text = ''
        self.option = option
        self.editor = editor

    def get_find_reg(self):
        if self.text:
            if self.option.is_whole_word:
                reg = QtCore.QRegExp(r'\b' + self.text + r'\b')
            else:
                reg = QtCore.QRegExp(self.text)
            if self.option.is_case_sensitive:
                reg.setCaseSensitivity(QtCore.Qt.CaseSensitive)
            else:
                reg.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

            return reg
        else:
            return None

    def find_text(self, is_back=False):
        count = self.show_found_text_pos()

        reg = self.get_find_reg()
        if not reg:
            return

        # 検索履歴を保存する。
        self.option.add_history(self.text)
        cursor = self.editor.textCursor()
        args = [reg, cursor]
        if is_back:
            args.append(QtGui.QTextDocument.FindBackward)
        cursor = self.editor.document().find(*args)
        self.editor.highlight_text(self.get_find_reg())
        if cursor.position() >= 0:
            self.editor.setTextCursor(cursor)
            self.clear_status_bar_message()
        else:
            if self.option.is_research and count > 0:
                # 先頭から再検索
                cursor = self.editor.textCursor()
                if is_back:
                    cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
                else:
                    cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
                self.editor.setTextCursor(cursor)
                self.find_text(is_back)
                self.show_message_research(is_back)
            else:
                self.show_message_not_found(is_back, is_bookmark=False)

    def clear_status_bar_message(self):
        self.editor.set_status_msg('')

    def show_message_research(self, is_back):
        if is_back:
            msg = constants.MSG_RESEARCH_BACKWARD
        else:
            msg = constants.MSG_RESEARCH_FORWARD
        self.editor.set_status_msg(msg)

    def show_message_not_found(self, is_back, is_bookmark):
        if is_back:
            title = constants.TITLE_NOT_FOUND_BACKWARD
            if is_bookmark:
                msg = constants.MSG_BOOKMARK_NOT_FOUND_BACKWARD
            else:
                msg = constants.MSG_TEXT_NOT_FOUND_BACKWARD % (self.text,)
        else:
            title = constants.TITLE_NOT_FOUND_FORWARD
            if is_bookmark:
                msg = constants.MSG_BOOKMARK_NOT_FOUND_FORWARD
            else:
                msg = constants.MSG_TEXT_NOT_FOUND_FORWARD % (self.text,)
        self.editor.set_status_msg(title)
        if not self.option.is_show_message:
            return
        self.editor.show_message_box(title, msg)

    def show_found_text_pos(self):
        count = 0
        reg = self.get_find_reg()
        self.editor.highlight_text(reg)

        if not reg:
            self.editor.verticalScrollBar().positions = []
            self.editor.verticalScrollBar().max_height = None
            self.editor.verticalScrollBar().update()
            return count

        cursor = self.editor.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
        positions = []
        cursor = self.editor.document().find(reg, cursor)
        while cursor.position() >= 0:
            block_number = cursor.block().blockNumber()
            if block_number not in positions:
                positions.append(block_number)
            cursor = self.editor.document().find(reg, cursor)
            count += 1
        self.editor.verticalScrollBar().positions = positions
        self.editor.verticalScrollBar().max_height = self.editor.blockCount()
        self.editor.verticalScrollBar().update()
        return count

    def next_bookmark(self, block, bookmarks):
        if bookmarks:
            b = self.get_block_number(block, bookmarks, True)
            if b and b.isValid():
                self.editor.jump_to_line(b.blockNumber())
        else:
            self.show_message_not_found(is_back=False, is_bookmark=True)

    def prev_bookmark(self, block, bookmarks):
        if bookmarks:
            b = self.get_block_number(block, bookmarks, False)
            if b and b.isValid():
                self.editor.jump_to_line(b.blockNumber())
        else:
            self.show_message_not_found(is_back=True, is_bookmark=True)

    def get_block_number(self, block, bookmarks, is_next=True):
        self.clear_status_bar_message()
        lst = sorted(bookmarks, key=lambda item: item.blockNumber()) \
            if is_next else sorted(bookmarks, key=lambda item: item.blockNumber(), reverse=True)
        for b in lst:
            if is_next:
                if b.blockNumber() > block.blockNumber():
                    return b
            else:
                if b.blockNumber() < block.blockNumber():
                    return b

        if self.option.is_research and lst:
            self.show_message_research(not is_next)
            return lst[0]
        return None


class Connection:

    DRIVER_MSSQL = 'QODBC'
    DRIVER_ORACLE = 'QOCI'

    def __init__(self, database_type, server_name, database_name, auth_type, user_name, password):
        self.db = None
        self.database_type = database_type
        self.server_name = server_name
        self.database_name = database_name
        self.auth_type = auth_type
        self.user_name = user_name
        self.password = password

        self.init_database()

    def init_database(self):
        db = QtSql.QSqlDatabase.database(self.get_connection_name(), False)
        if self.database_type == constants.DATABASE_SQL_SERVER:
            if self.auth_type == 0:
                # Sql Server認証
                conn_format = "DRIVER={{SQL Server}};Server={0};Database={1};Uid={2};Pwd={3};"
                connection_string = conn_format.format(self.server_name, self.database_name, self.user_name, self.password)
            else:
                # Windows認証
                conn_format = "DRIVER={{SQL Server}};Server={0};Database={1};Persist Security Info=True"
                connection_string = conn_format.format(self.server_name, self.database_name)
            if not db.isValid():
                self.db = QtSql.QSqlDatabase.addDatabase(Connection.DRIVER_MSSQL, self.get_connection_name())
                self.db.setDatabaseName(connection_string)
            else:
                self.db = db
        elif self.database_type == constants.DATABASE_ORACLE:
            print 'oracle'
            if not db.isValid():
                self.db = QtSql.QSqlDatabase.addDatabase(Connection.DRIVER_ORACLE, self.get_connection_name())
                # self.db.setHostName(self.server_name)
                self.db.setDatabaseName(self.database_name)
                self.db.setUserName(self.user_name)
                self.db.setPassword(self.password)
            else:
                self.db = db

    @staticmethod
    def load_database(db):
        if db and db.isValid():
            d = {}
            if db.driverName() == Connection.DRIVER_MSSQL:
                d = {'database_type': constants.DATABASE_SQL_SERVER, 'auth_type': 0}
                for s in db.databaseName().split(';'):
                    if not s.trimmed():
                        continue
                    if s.startsWith('DRIVER'):
                        continue
                    else:
                        d[unicode(s.split('=')[0])] = s.split('=')[1]
                if 'Uid' not in d:
                    d['auth_type'] = 1
                    d['Uid'] = None
                    d['Pwd'] = None
            return Connection(d['database_type'], d['Server'], d['Database'], d['auth_type'], d['Uid'], d['Pwd'])
        return None

    def get_connection_name(self):
        return common.get_default_conn_name(self.database_name, self.server_name, self.user_name)

    @staticmethod
    def get_connections():
        name_list = QtSql.QSqlDatabase.connectionNames()
        if name_list.contains(settings.Setting.CONNECTION_NAME):
            idx = name_list.indexOf(settings.Setting.CONNECTION_NAME)
            name_list.removeAt(idx)

        conn_list = []
        for connection_name in name_list:
            db = QtSql.QSqlDatabase.database(connection_name, False)
            conn = Connection.load_database(db)
            conn_list.append(conn)
        return conn_list

    def get_databases(self):
        sql = "select name from master.dbo.sysdatabases order by name"
        self.db.open()
        query = QtSql.QSqlQuery(sql, self.db)
        databases = []
        while query.next():
            databases.append(query.value(0).toString())
        return databases

    def get_tables(self):
        sql = "select name from sys.tables order by name"
        self.db.open()
        query = QtSql.QSqlQuery(sql, self.db)
        tables = []
        while query.next():
            tables.append(query.value(0).toString())
        return tables

    def get_views(self):
        sql = "select name from sys.views order by name"
        self.db.open()
        query = QtSql.QSqlQuery(sql, self.db)
        tables = []
        while query.next():
            tables.append(query.value(0).toString())
        return tables

    def get_table_schema(self, name):
        sql = "SELECT c.name" \
              "     , typ.name AS data_type" \
              "     , c.max_length" \
              "     , c.precision" \
              "     , c.is_nullable" \
              "     , ep.value AS 'description'" \
              "     , OBJECTPROPERTY(OBJECT_ID(k.CONSTRAINT_SCHEMA + '.' + k.CONSTRAINT_NAME)," \
              "                      'IsPrimaryKey') AS 'is_primary_key' " \
              "  FROM sys.tables t " \
              "       INNER JOIN sys.columns c  ON c.object_id = t.object_id" \
              "       LEFT JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE k  ON t.name = k.TABLE_NAME" \
              "                                                       AND c.name = k.COLUMN_NAME" \
              "       LEFT JOIN sys.extended_properties ep  ON ep.major_id = c.object_id" \
              "                                            AND ep.minor_id = c.column_id" \
              "                                            AND ep.name LIKE 'MS_Description' " \
              "       LEFT JOIN sys.types typ  ON typ.user_type_id = c.user_type_id " \
              " WHERE t.name = :name " \
              " ORDER BY c.column_id"
        self.open()
        query = QtSql.QSqlQuery(self.db)
        query.prepare(sql)
        query.bindValue(0, name)
        query.exec_()
        columns = []
        while query.next():
            column = DataColumn(query.value(0).toString(), query.value(1).toString(), query.value(2).toInt()[0])
            column.precision = query.value(3).toInt()[0]
            column.is_nullable = query.value(4).toBool()
            column.description = query.value(5).toString()
            column.is_primary_key = query.value(6).toBool()
            columns.append(column)
        return columns

    def has_feature(self, feature):
        return self.db.driver().hasFeature(feature)

    def open(self):
        if not self.is_open():
            return self.db.open()
        if not self.db.isValid():
            return self.db.open()
        return True

    def close(self):
        return self.db.close()

    def is_open(self):
        return self.db.isOpen()

    def execute_sql(self, sql, parameters):
        self.open()
        if sql and self.db:
            query = QtSql.QSqlQuery(self.db)
            if parameters:
                for i, parameter in enumerate(parameters):
                    # ＠ を ： に変換する。
                    new_param_sql = parameter.sql
                    new_param_sql = new_param_sql.replace('@', ':')
                    sql = sql.replace(parameter.sql, new_param_sql)
            query.prepare(sql)
            if parameters:
                # 引数がある場合、引数を設定する
                for i, parameter in enumerate(parameters):
                    new_param_sql = parameter.sql
                    new_param_sql = new_param_sql.replace('@', ':')
                    query.bindValue(new_param_sql, parameter.value)
            query.exec_()
            if query.lastError().isValid():
                return query.lastError()

            tables = []
            if query.isForwardOnly():
                tables.append(self.get_data_table(query))
                while query.nextResult():
                    tables.append(self.get_data_table(query))
            else:
                tables.append(self.get_data_table(query))
            self.close()
            return tables
        else:
            self.close()
            return None

    def edit_top_200(self, table_name, where_clause=None, orders=None):
        if not table_name:
            return None

        columns = self.get_table_schema(table_name)
        self.open()
        table = DataTable(table_name)
        table.Columns = columns
        model = SqlTableModel(table, db=self.db)
        model.setTable(table_name)
        model.setEditStrategy(QtSql.QSqlTableModel.OnRowChange)
        model.setFilter(where_clause)
        if orders:
            model.setSort(*orders)
        model.select()
        return model

    def select_top_1000(self, table_name, where_clause=None, order_clause=None):
        if not table_name:
            return None

        columns = self.get_table_schema(table_name)
        sql = u'SELECT TOP 256 * FROM [%s]' % (table_name,)
        if where_clause:
            sql += u' WHERE ' + where_clause
        if order_clause:
            sql += u' ORDER BY ' + order_clause
        self.open()
        print sql
        query = QtSql.QSqlQuery(self.db)
        if query.exec_(sql):
            table = DataTable(table_name)
            table.Columns = columns
            while query.next():
               row = DataRow()
               table.add_row(row)
               for i in range(len(columns)):
                   row.Values.append(query.value(i))
            return SqlQueryModel(table)
            # model = SqlTableQueryModel(table)
            # model.setQuery(query)
            # return model
        else:
            return query.lastError()

    def last_error(self):
         return self.db.lastError()

    def get_data_table(self, query):
        columns = []
        for i in range(query.record().count()):
            field = query.record().field(i)
            name = field.name()
            if not name:
                name = u"(列 %s)" % (i + 1,)
            column = DataColumn(name, common.get_db_type(field.type()), field.length())
            columns.append(column)

        table = DataTable()
        table.Columns = columns
        while query.next():
            row = DataRow()
            table.add_row(row)
            for i in range(len(columns)):
                row.Values.append(query.value(i))
        return SqlQueryModel(table)
