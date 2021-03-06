# coding: UTF-8
# !/usr/bin/env python

import os
import common, constants

from PyQt4 import QtCore, QtGui
from editor import Editors, CodeEditor, SqlDatabaseDialog, ConnectionListDocker
from settings import Setting


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # エディターのTagWidget
        self.editors = None
        self.options = Setting()
        self.recent_files_menu = None
        self.toolbar_menu = None
        self.setContentsMargins(0, 0, 0, 0)
        self.conn_list = ConnectionListDocker(self)

        self.init_layout()
        self.new_file()

        self.setWindowIcon(QtGui.QIcon(os.path.join(common.get_root_path(), 'logo.ico')))

    def about(self):
        QtGui.QMessageBox.about(self, "About Syntax Highlighter",
                "<p>The <b>Syntax Highlighter</b> example shows how to "
                "perform simple syntax highlighting by subclassing the "
                "QSyntaxHighlighter class and describing highlighting "
                "rules using regular expressions.</p>")

    def init_layout(self):
        # エディター
        self.editors = Editors(self, self.options)
        self.setCentralWidget(self.editors)

        self.init_menu()
        self.init_file_toolbar()
        self.init_edit_toolbar()
        self.init_db_toolbar()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.conn_list)
        self.conn_list.hide()
    
    def init_menu(self):
        # ファイルメニュー
        self.init_file_menu()

        # 編集メニュー
        self.init_edit_menu()

        # 検索メニュー
        self.init_search_menu()

        # 表示メニュー
        self.init_view_menu()
        self.init_database_menu()

    def init_file_menu(self):
        file_menu = QtGui.QMenu(u"ファイル(&F)", self)
        self.menuBar().addMenu(file_menu)

        file_menu.addAction(common.get_icon('new_file'), u"新規(&N)", self.new_file, "Ctrl+N")
        file_menu.addAction(common.get_icon('open_file'), u"開く(&O)...", self.open_file, "Ctrl+O")
        codec_menu = file_menu.addMenu(u"開き直す")
        signal_mapper = QtCore.QSignalMapper(self)
        for codec in sorted(CodeEditor.CODEC_LIST):
            action = QtGui.QAction(str(codec), codec_menu)
            self.connect(action, QtCore.SIGNAL('triggered()'), signal_mapper, QtCore.SLOT('map()'))
            signal_mapper.setMapping(action, str(codec))
            codec_menu.addAction(action)
        codec_menu.addSeparator()
        codec_menu_all = QtGui.QMenu(u"すべて(&A)", self)
        codec_menu.addMenu(codec_menu_all)
        for codec in sorted(QtCore.QTextCodec.availableCodecs(), key=lambda s: str(s).lower()):
            action = QtGui.QAction(str(codec), codec_menu_all)
            self.connect(action, QtCore.SIGNAL('triggered()'), signal_mapper, QtCore.SLOT('map()'))
            signal_mapper.setMapping(action, str(codec))
            codec_menu_all.addAction(action)
        self.connect(signal_mapper, QtCore.SIGNAL('mapped(QString)'), self.menu_item_clicked)
        file_menu.addSeparator()
        file_menu.addAction(common.get_icon('save_file'), u"上書き保存(&S)", self.save_file, "Ctrl+S")
        file_menu.addAction(common.get_icon('save_as_file'), u"名前を付けて保存(&A)...", self.save_as_file, "Ctrl+Shift+S")
        file_menu.addSeparator()
        file_menu.addAction(common.get_icon('close_file'), u"閉じる(&C)", self.close_file, "Ctrl+F4")
        file_menu.addSeparator()
        # 最近使ったファイル
        self.recent_files_menu = file_menu.addMenu(u"最近使ったファイル(&F)")
        self.recent_folders_menu = file_menu.addMenu(u"最近使ったフォルダ(&D)")
        self.init_recent_files_menu()
        file_menu.addSeparator()
        file_menu.addAction(u"終了(&X)", QtGui.qApp.quit, "Ctrl+Q")

    def init_recent_files_menu(self):
        self.recent_files_menu.clear()
        mapper_recent_files = QtCore.QSignalMapper(self)
        for recent_file in self.options.recently.get_files():
            action = QtGui.QAction(recent_file, self.recent_files_menu)
            self.connect(action, QtCore.SIGNAL('triggered()'), mapper_recent_files, QtCore.SLOT('map()'))
            mapper_recent_files.setMapping(action, recent_file)
            self.recent_files_menu.addAction(action)
        self.connect(mapper_recent_files, QtCore.SIGNAL('mapped(QString)'), self.recent_file_clicked)

        self.recent_folders_menu.clear()
        mapper_recent_folders = QtCore.QSignalMapper(self)
        for recent_folder in self.options.recently.get_folders():
            action = QtGui.QAction(recent_folder, self.recent_folders_menu)
            self.connect(action, QtCore.SIGNAL('triggered()'), mapper_recent_folders, QtCore.SLOT('map()'))
            mapper_recent_folders.setMapping(action, recent_folder)
            self.recent_folders_menu.addAction(action)
        self.connect(mapper_recent_folders, QtCore.SIGNAL('mapped(QString)'), self.recent_folder_clicked)

    def init_edit_menu(self):
        edit_menu = QtGui.QMenu(u"編集(&E)", self)
        self.menuBar().addMenu(edit_menu)
        
        edit_menu.addAction(common.get_icon('undo'), constants.MENU_EDIT_UNDO, self.editor_undo, QtGui.QKeySequence.Undo)
        edit_menu.addAction(common.get_icon('redo'), constants.MENU_EDIT_REDO, self.editor_redo, QtGui.QKeySequence.Redo)
        edit_menu.addSeparator()
        edit_menu.addAction(u"ソース整形", self.source_reformat, "Ctrl+Shift+F")
        edit_menu.addSeparator()
        edit_menu.addAction(u"左(先頭)の空白を削除", self.delete_left_space, "ALT+L")
        edit_menu.addAction(u"右(末尾)の空白を削除", self.delete_right_space, "ALT+R")
        edit_menu.addSeparator()
        edit_menu.addAction(u"コメント設定・解除(&C)", self.comment_out, "Ctrl+/")

    def init_search_menu(self):
        search_menu = QtGui.QMenu(u"検索(&S)", self)
        self.menuBar().addMenu(search_menu)

        search_menu.addAction(u"検索(&F)...", self.show_find_dialog, "Ctrl+F")
        search_menu.addAction(u"次を検索(&N)", self.find_next, "F3")
        search_menu.addAction(u"前を検索(&P)", self.find_prev, "Shift+F3")
        search_menu.addAction(u"検索文字列の切替(&C)", self.change_find_text, "Ctrl+F3")
        search_menu.addSeparator()
        bookmark_menu = QtGui.QMenu(u"ブックマーク(&M)", self)
        bookmark_menu.addAction(u"ブックマーク設定・解除(&S)", self.set_bookmark, "Ctrl+F2")
        bookmark_menu.addAction(u"次のブックマークへ(&A)", self.next_bookmark, "F2")
        bookmark_menu.addAction(u"前のブックマークへ(&Z)", self.prev_bookmark, "Shift+F2")
        bookmark_menu.addAction(u"ブックマークの全解除(&X)", self.clear_bookmark, "Ctrl+Shift+F2")
        bookmark_menu.addAction(u"ブックマークの一覧(&V)", self.view_bookmarks, "ALT+F2")
        search_menu.addMenu(bookmark_menu)
        search_menu.addAction(u"指定行へジャンプ(&J)...", self.jump_to_line, "Ctrl+J")

    def init_view_menu(self):
        view_menu = QtGui.QMenu(u"表示(&V)", self)
        self.menuBar().addMenu(view_menu)

        view_menu.addAction(common.get_icon('win_v_sep'), u"ウインドウを表示／隠す(&B)", self.show_bottom_window, "F4")
        view_menu.addAction(common.get_icon('win_h_sep'), u"ウインドウを表示／隠す(&R)", self.show_right_window, "F6")
        view_menu.addSeparator()

        self.window_menu = QtGui.QMenu(u"ウインドウ(&W)", self)
        view_menu.addMenu(self.window_menu)
        self.window_menu.addAction(self.conn_list.toggleViewAction())
        self.toolbar_menu = QtGui.QMenu(u"ツールバー(&T)", self)
        view_menu.addMenu(self.toolbar_menu)

    def init_database_menu(self):
        db_menu = QtGui.QMenu(u"データベース(&D)", self)
        self.menuBar().addMenu(db_menu)

        db_menu.addAction(common.get_icon('database_add'), u"データベース追加(&A)", self.connect_database)
        db_menu.addAction(common.get_icon('database_list'), u"接続したデータベース(&L)", self.connected_database, "Ctrl+H")
        db_menu.addAction(common.get_icon('right_arrow'), u"ＳＱＬを実行(&E)", self.execute_sql, "F5")

    def init_file_toolbar(self):
        toolbar = self.addToolBar(constants.TOOLBAR_FILE)
        self.toolbar_menu.addAction(toolbar.toggleViewAction())
        toolbar.setIconSize(QtCore.QSize(16, 16))

        toolbar.addAction(common.get_icon('new_file'), u"新規(Ctrl+N)", self.new_file)
        toolbar.addAction(common.get_icon('open_file'), u"開く(Ctrl+O)", self.open_file)
        toolbar.addAction(common.get_icon('save_file'), u"上書き保存(Ctrl+S)", self.save_file)
        toolbar.addAction(common.get_icon('save_as_file'), u"名前を付けて保存(Ctrl+Shift+S)", self.save_as_file)
        toolbar.addAction(common.get_icon('close_file'), u"閉じる(Ctrl+F4)", self.close_file)

    def init_edit_toolbar(self):
        toolbar = self.addToolBar(constants.TOOLBAR_EDIT)
        self.toolbar_menu.addAction(toolbar.toggleViewAction())
        toolbar.setIconSize(QtCore.QSize(16, 16))

        toolbar.addAction(common.get_icon('undo'), constants.MENU_EDIT_UNDO, self.editor_undo)
        toolbar.addAction(common.get_icon('redo'), constants.MENU_EDIT_REDO, self.editor_redo)

    def init_db_toolbar(self, connection=None):
        toolbar = self.get_toolbar(constants.TOOLBAR_DATABASE_NAME)
        if not toolbar:
            toolbar = self.addToolBar(constants.TOOLBAR_DATABASE_NAME)
            self.toolbar_menu.addAction(toolbar.toggleViewAction())
            toolbar.setIconSize(QtCore.QSize(16, 16))
        else:
            toolbar.clear()

        # データベースに接続する
        toolbar.addAction(common.get_icon('database_add'), u"データベースに接続する。", self.connect_database)
        toolbar.addAction(common.get_icon('database_list'), u"接続したデータベース", self.connected_database)
        # 接続されているデータベース
        if connection and connection.database_name:
            combo_box = QtGui.QComboBox()
            for i, conn in enumerate(connection.get_connections()):
                combo_box.addItem(conn.get_connection_name())
                if conn.get_connection_name() == connection.get_connection_name():
                    combo_box.setCurrentIndex(i)
            combo_box.setFixedWidth(150)
            sp = combo_box.view().sizePolicy()
            sp.setHorizontalPolicy(QtGui.QSizePolicy.MinimumExpanding)
            combo_box.view().setSizePolicy(sp)
            toolbar.addWidget(combo_box)
        # SQLを実行する。
        toolbar.addAction(common.get_icon('right_arrow'), u"ＳＱＬを実行する。", self.execute_sql)
        # ウィンドウ分割
        toolbar.addSeparator()
        toolbar.addAction(common.get_icon('win_v_sep'), u"ウインドウを表示／隠す。(F4)", self.show_bottom_window)
        toolbar.addAction(common.get_icon('win_h_sep'), u"ウインドウを表示／隠す。(F6)", self.show_right_window)

    def set_window_title(self, title):
        self.setWindowTitle(title)

    def menu_item_clicked(self, name):
        if name and self.get_current_editor().path:
            self.open_file(self.get_current_editor().path, name)

    def recent_file_clicked(self, file_path):
        self.open_file(file_path)

    def recent_folder_clicked(self, folder_path):
        self.open_file(folder=folder_path)

    def new_file(self):
        self.editors.add_editor(None)

    def open_file(self, path=None, codec=None, folder=None):
        self.editors.open_file(path, codec, folder)

    def save_file(self):
        self.editors.save_file()

    def save_as_file(self):
        self.editors.save_as_file()

    def close_file(self):
        self.editors.removeTab(self.editors.currentIndex())

    def delete_left_space(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.delete_left_space()

    def delete_right_space(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.delete_right_space()

    def comment_out(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.comment_out()

    def editor_undo(self):
        code_editor = self.get_current_editor()
        if code_editor:
            print 'undo'
            code_editor.undo()

    def editor_redo(self):
        code_editor = self.get_current_editor()
        if code_editor:
            print 'redo'
            code_editor.redo()

    def source_reformat(self):
        if self.get_current_editor():
            self.get_current_editor().reformat()

    def show_find_dialog(self):
        if self.get_current_editor():
            self.get_current_editor().show_find_dialog()

    def find_next(self):
        if self.get_current_editor():
            self.get_current_editor().find_text(False)

    def find_prev(self):
        if self.get_current_editor():
            self.get_current_editor().find_text(True)

    def change_find_text(self):
        code_editor = self.get_current_editor()
        if code_editor:
            cursor = code_editor.textCursor()
            cursor.hasSelection()
            txt = cursor.selectedText()
            code_editor.finding.text = txt
            code_editor.finding.show_found_text_pos()

    def set_bookmark(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.set_bookmark()

    def next_bookmark(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.next_bookmark()

    def prev_bookmark(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.prev_bookmark()

    def clear_bookmark(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.clear_bookmark()

    def view_bookmarks(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.show_bookmarks_dialog()

    def jump_to_line(self):
        code_editor = self.get_current_editor()
        if code_editor:
            code_editor.show_jump_dialog()

    def connect_database(self):
        sql_tab = self.get_current_tab()
        dialog = SqlDatabaseDialog(self, self.options)
        ret = dialog.exec_()
        if ret == QtGui.QDialog.Accepted:
            if sql_tab:
                sql_tab.set_connection(dialog.connection)
                self.init_db_toolbar(dialog.connection)
                self.conn_list.add_connection(dialog.connection)
                self.conn_list.setVisible(True)
                return dialog.connection
        return None

    def connected_database(self):
        self.conn_list.setVisible(not self.conn_list.isVisible())

    def execute_sql(self):
        sql_tab = self.get_current_tab()
        if sql_tab:
            if sql_tab.connection:
                sql_tab.execute_sql()
            else:
                if self.connect_database():
                    sql_tab.execute_sql()

    def show_bottom_window(self):
        tab = self.get_current_tab()
        if tab:
            tab.show_bottom_window()

    def show_right_window(self):
        tab = self.get_current_tab()
        if tab:
            tab.show_right_window()

    def get_current_editor(self):
        if self.editors:
            if hasattr(self.editors.currentWidget(), 'code_editor'):
                return self.editors.currentWidget().code_editor
        return None

    def get_current_tab(self):
        if self.editors:
            return self.editors.currentWidget()
        else:
            return None

    def get_toolbar(self, window_title):
        for toolbar in self.findChildren(QtGui.QToolBar):
            if toolbar.windowTitle() == window_title:
                return toolbar
        return None

    def closeEvent(self, event):
        for i in range(self.editors.count()):
            editor = self.editors.widget(i)
            editor.close()
        event.accept()


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    #window.showMaximized()
    window.resize(1224, 800)
    window.show()
    sys.exit(app.exec_())
