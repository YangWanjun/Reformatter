#coding: UTF-8
#!/usr/bin/env python

import os, re
import common, constants

from PyQt4 import QtCore, QtGui
from highlighter import SqlHighlighter
from sqlparser import SqlLexer, SqlParser


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        # エディターのTagWidget
        self.editors = None
        self.status_bar = None

        self.init_layout()
        self.new_file()

        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        self.setCentralWidget(self.editors)
        self.setWindowTitle("Reformatter")

    def about(self):
        QtGui.QMessageBox.about(self, "About Syntax Highlighter",
                "<p>The <b>Syntax Highlighter</b> example shows how to "
                "perform simple syntax highlighting by subclassing the "
                "QSyntaxHighlighter class and describing highlighting "
                "rules using regular expressions.</p>")

    def init_layout(self):
        # エディター
        self.editors = Editors(self)

        # ステータスバー
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        
        self.init_menu()
    
    def init_menu(self):
        # ファイルメニュー
        file_menu = QtGui.QMenu(u"ファイル(&F)", self)
        self.menuBar().addMenu(file_menu)

        file_menu.addAction(u"新規(&N)", self.new_file, "Ctrl+N")
        file_menu.addAction(u"開く(&O)", self.open_file, "Ctrl+O")
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
        file_menu.addAction(u"閉じる(&C)", self.close_file, "Ctrl+F4")
        file_menu.addSeparator()
        file_menu.addAction(u"終了(&X)", QtGui.qApp.quit, "Ctrl+Q")
        
        # 編集メニュー
        edit_menu = QtGui.QMenu(u"編集(&E)", self)
        self.menuBar().addMenu(edit_menu)
        
        edit_menu.addAction(u"ソース整形", self.source_reformat, "Ctrl+Shift+F")
        edit_menu.addSeparator()
        edit_menu.addAction(u"左(先頭)の空白を削除", self.delete_left_space, "ALT+L")
        edit_menu.addAction(u"右(末尾)の空白を削除", self.delete_right_space, "ALT+R")
        
        # 検索メニュー
        find_menu = QtGui.QMenu(u"検索(&S)", self)
        self.menuBar().addMenu(find_menu)

        find_menu.addAction(u"検索", self.show_find_dialog, "Ctrl+F")
        find_menu.addAction(u"次を検索", self.find_next, "F3")
        find_menu.addAction(u"前を検索", self.find_prev, "Shift+F3")

    def menu_item_clicked(self, name):
        if name and self.get_current_editor().path:
            self.open_file(self.get_current_editor().path, name)

    def new_file(self):
        self.editors.add_editor(None)

    def open_file(self, path=None, codec=None):
        self.editors.open_file(path, codec)

    def close_file(self):
        self.editors.removeTab(self.editors.currentIndex())

    def delete_left_space(self):
        if self.editors.currentWidget():
            self.editors.currentWidget().delete_left_space()

    def delete_right_space(self):
        if self.editors.currentWidget():
            self.editors.currentWidget().delete_right_space()

    def source_reformat(self):
        if self.get_current_editor():
            errors = self.get_current_editor().reformat()
            if errors:
                self.set_status_message(errors[0])
            else:
                self.set_status_message('Success!', 3000)

    def show_find_dialog(self):
        if self.get_current_editor():
            self.get_current_editor().show_find_dialog()

    def find_next(self):
        if self.get_current_editor():
            self.get_current_editor().find_text(False)

    def find_prev(self):
        if self.get_current_editor():
            self.get_current_editor().find_text(True)

    def get_current_editor(self):
        if self.editors:
            return self.editors.currentWidget()
        else:
            return None

    def set_status_message(self, message, times=0):
        """
        ステータスバーにメッセージを表示する。
        """
        if self.status_bar:
            self.status_bar.showMessage(message, times)

    def closeEvent(self, event):
        event.accept()


class StatusBar(QtGui.QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        
        css = '''
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

    def set_line_number(self, line, col, length):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if self.lbl_line_no:
            self.lbl_line_no.setText(u"%s 行 %s 列 %s 文字" % (line, col, length))

    def set_codec(self, name):
        if name and self.lbl_codec:
            self.lbl_codec.setText(name)


class EditorTabBar(QtGui.QTabBar):
    def __init__(self, parent=None):
        super(EditorTabBar, self).__init__(parent)
        self.previous_index = -1
        self.setShape(QtGui.QTabBar.TriangularNorth)
        self.setMovable(True)

        css = '''
        QTabBar:tab {
            min-width: 70px;
            height: 20px;
            max-width: 300px;
        }
        QTabBar:tab:selected {
            color: blue;
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


class Editors(QtGui.QTabWidget):
    def __init__(self, parent):
        super(Editors, self).__init__(parent)

        self.untitled_name_index = 0
        self.setTabBar(EditorTabBar())
        self.tabCloseRequested.connect(self.removeTab)

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

        editor = CodeEditor(self, path)
        self.addTab(editor, filename)
        self.setCurrentWidget(editor)
        if path:
            self.setTabToolTip(self.currentIndex(), path)
        editor.setWindowState(QtCore.Qt.WindowActive)
        editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        return editor

    def open_file(self, path=None, codec=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self.parent(), u"開く", '', "Sql Files (*.sql);;All Files(*.*)")

        if path:
            codec = codec if codec else constants.DEFAULT_CODEC_NAME
            editor = self.add_editor(path)
            editor.codec = codec
            in_file = QtCore.QFile(path)
            if in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text_stream = QtCore.QTextStream(in_file)
                text_stream.setCodec(codec)
                text = text_stream.readAll()
                editor.bom = text_stream.generateByteOrderMark()
                editor.codec = str(text_stream.codec().name())
                editor.setPlainText(text)

    def get_untitled_name(self):
        self.untitled_name_index += 1
        return constants.UNTITLED_FILE % (self.untitled_name_index,)

    def get_editor_by_path(self, path):
        if path:
            for i in range(self.count()):
                editor = self.widget(i)
                if editor.path == path:
                    return editor
        return None

    def removeTab(self, index):
        super(Editors, self).removeTab(index)
        if self.count() == 0:
            self.add_editor(None)

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.modifiers() == QtCore.Qt.ControlModifier:
                if event.key() == QtCore.Qt.Key_Tab:
                    self.move_to_next()
                    return False  # eat alt+tab or alt+shift+tab key
            elif event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
                if event.key() == QtCore.Qt.Key_Tab:
                    self.move_to_prev()
                    return False  # eat alt+tab or alt+shift+tab key

        return QtCore.QObject.eventFilter(self, obj, event)

    def move_to_prev(self):
        old_position = self.currentIndex()
        new_position = old_position - 1 if old_position > 0 else self.count() - 1
        self.setCurrentIndex(new_position)

    def move_to_next(self):
        old_position = self.currentIndex()
        new_position = old_position + 1 if old_position + 1 < self.count() else 0
        self.setCurrentIndex(new_position)


class FindText:
    def __init__(self):
        self.text = ''
        self.is_whole_word = False
        self.is_case_sensitive = False
        self.is_regular = False
        self.is_show_message = False
        self.is_auto_close = False
        self.is_research = False

    def get_find_reg(self):
        if self.text:
            if self.is_whole_word:
                reg = QtCore.QRegExp(r'\b' + self.text + r'\b')
            else:
                reg = QtCore.QRegExp(self.text)
            if self.is_case_sensitive:
                reg.setCaseSensitivity(QtCore.Qt.CaseSensitive)
            else:
                reg.setCaseSensitivity(QtCore.Qt.CaseInsensitive)

            return reg
        else:
            return None


class FindDialog(QtGui.QDialog):
    def __init__(self, parent, finding_text):
        super(FindDialog, self).__init__(parent)
        self.finding_text = finding_text
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
        self.setFixedSize(470, 160)
        self.setWindowTitle(u"検索")

    def init_layout(self):
        hbox = QtGui.QHBoxLayout()
        left_vbox = QtGui.QVBoxLayout()
        left_vbox.setContentsMargins(-1, -1, -1, 0)
        right_vbox = QtGui.QVBoxLayout()

        # 検索文字列
        sub_hbox = QtGui.QHBoxLayout()
        label = QtGui.QLabel(u"条件(&N)")
        self.txt_condition = QtGui.QLineEdit()
        if self.finding_text and self.finding_text.text:
            self.txt_condition.setText(self.finding_text.text)
        label.setBuddy(self.txt_condition)
        sub_hbox.addWidget(label)
        sub_hbox.addWidget(self.txt_condition)
        left_vbox.addLayout(sub_hbox)
        # 単語単位
        chk = QtGui.QCheckBox(u"単語単位で探す(&W)")
        if self.finding_text and self.finding_text.is_whole_word:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_whole_word)
        left_vbox.addWidget(chk)
        # 大文字と小文字を区別する
        chk = QtGui.QCheckBox(u"大文字と小文字を区別する(&C)")
        if self.finding_text and self.finding_text.is_case_sensitive:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_case_sensitive)
        left_vbox.addWidget(chk)
        # 正規表現
        chk = QtGui.QCheckBox(u"正規表現で探す(&E)")
        if self.finding_text and self.finding_text.is_regular:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_regular)
        left_vbox.addWidget(chk)
        # 見つからないときにメッセージ表示
        chk = QtGui.QCheckBox(u"見つからないときにメッセージ表示(&M)")
        if self.finding_text and self.finding_text.is_show_message:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_show_message)
        left_vbox.addWidget(chk)
        # 検索ダイアログを自動的に閉じる
        chk = QtGui.QCheckBox(u"検索ダイアログを自動的に閉じる(&L)")
        if self.finding_text and self.finding_text.is_auto_close:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_auto_close)
        left_vbox.addWidget(chk)
        # 先頭（末尾）から再検索する
        chk = QtGui.QCheckBox(u"先頭（末尾）から再検索する(&Z)")
        if self.finding_text and self.finding_text.is_research:
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
        self.finding_text.is_whole_word = (state == QtCore.Qt.Checked)

    def set_case_sensitive(self, state):
        self.finding_text.is_case_sensitive = (state == QtCore.Qt.Checked)

    def set_regular(self, state):
        self.finding_text.is_regular = (state == QtCore.Qt.Checked)

    def set_show_message(self, state):
        self.finding_text.is_show_message = (state == QtCore.Qt.Checked)

    def set_auto_close(self, state):
        self.finding_text.is_auto_close = (state == QtCore.Qt.Checked)

    def set_research(self, state):
        self.finding_text.is_research = (state == QtCore.Qt.Checked)

    def find_next(self):
        self.finding_text.text = self.txt_condition.text()
        self.get_editor().finding_text = self.finding_text
        self.get_editor().find_text(False)
        if self.finding_text.is_auto_close:
            self.reject()

    def find_prev(self):
        self.finding_text.text = self.txt_condition.text()
        self.get_editor().finding_text = self.finding_text
        self.get_editor().find_text(True)
        if self.finding_text.is_auto_close:
            self.reject()


class CodeEditor(QtGui.QPlainTextEdit):

    CODEC_LIST = ['SJIS', 'UTF-8', 'UTF-16', 'UTF-32']
    LEFT_BRACKETS = ('(', '[', '{')
    RIGHT_BRACKETS = (')', ']', '}')
    BRACKETS = {'(': ')', '[': ']', '{': '}',
                ')': '(', ']': '[', '}': '{'}

    def __init__(self, parent=None, path=None, codec=None):
        super(CodeEditor, self).__init__(parent)
        self.path = path
        self.codec = codec
        self.bom = False
        self.finding_text = FindText()

        font = QtGui.QFont()
        font.setFamily(u'ＭＳ ゴシック')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(2)
        self.document().setDocumentMargin(1)
        self.setTabStopWidth(self.get_tab_space_width())
        self.setLineWrapMode(QtGui.QPlainTextEdit.NoWrap)

        self.line_number_area = LineNumberArea(self)
        # self.ruler_area = RulerArea(self)

        self.highlighter = SqlHighlighter(self.document())

        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.cursor_position_changed)

        self.update_line_number_area_width()
        self.highlight_current_line()

        css = '''
        QPlainTextEdit {
            background-color: rgb(250, 250, 250);
            border: none;
        }
        '''
        self.setStyleSheet(css)

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

    def get_main_window(self):
        return self.parentWidget().parentWidget().parentWidget()

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
            return None, None

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

        space = 10 + self.fontMetrics().width('9') * digits
        return space

    def keyPressEvent(self, event):
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            # Ctrl + Shift
            if event.key() == QtCore.Qt.Key_F:
                # Ctrl + Shift + F
                errors = self.reformat()
                if errors:
                    self.get_main_window().set_status_message(errors[0])
                else:
                    self.get_main_window().set_status_message('Success!', 3000)
            elif event.key() == QtCore.Qt.Key_Backtab:
                # Ctrl + Shift + Tab
                self.parentWidget().parentWidget().move_to_prev()
            else:
                super(CodeEditor, self).keyPressEvent(event)
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            # Ctrl
            if event.key() == QtCore.Qt.Key_Tab:
                # Ctrl + Tab
                self.parentWidget().parentWidget().move_to_next()
            else:
                super(CodeEditor, self).keyPressEvent(event)
        else:
            super(CodeEditor, self).keyPressEvent(event)

    def paintEvent(self, event):
        super(CodeEditor, self).paintEvent(event)

        # 縦線を表示する。
        if self.get_current_col_number() > 1:
            self.draw_cursor_line(QtCore.Qt.blue)
        self.draw_column_line(100, QtCore.Qt.lightGray)
        self.draw_eof_mark()
        self.draw_return_mark(event)
        self.draw_full_space(event)

    def resizeEvent(self, event):
        QtGui.QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        # self.ruler_area.setGeometry(QtCore.QRect(cr.left() + self.line_number_area_width(), cr.top(),
        #                                          cr.width() - self.line_number_area_width(), 20))

    def highlight_current_line(self):
        extra_selections = QtGui.QTextEdit.extraSelections(QtGui.QTextEdit())

        # 行を highlight
        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()

            line_color = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        # 括弧を highlight
        cursor = self.textCursor()
        cursor.movePosition(QtGui.QTextCursor.Right, QtGui.QTextCursor.KeepAnchor)
        text = cursor.selectedText()
        if unicode(text) not in CodeEditor.BRACKETS.values():
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.MoveAnchor)
            cursor.movePosition(QtGui.QTextCursor.Left, QtGui.QTextCursor.KeepAnchor)
            text = cursor.selectedText()
        if unicode(text) in CodeEditor.BRACKETS.values():
            word_color = QtGui.QColor(QtCore.Qt.red).lighter(160)
            current_word = QtGui.QTextEdit.ExtraSelection()
            current_word.format.setBackground(word_color)
            current_word.cursor = cursor
            paired_cursor = self.get_next_pair_cursor(text, cursor)
            if paired_cursor:
                paired_word = QtGui.QTextEdit.ExtraSelection()
                paired_word.format.setBackground(word_color)
                paired_word.cursor = paired_cursor
                extra_selections.append(current_word)
                extra_selections.append(paired_word)

        self.setExtraSelections(extra_selections)

    def update_line_number_area_width(self):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width()

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
        find_dialog = FindDialog(self, self.finding_text)
        find_dialog.show()

    def find_text(self, is_back=False):
        cursor = self.textCursor()
        if not self.finding_text:
            return
        reg = self.finding_text.get_find_reg()
        if not reg:
            return

        args = [reg, cursor]
        if is_back:
            args.append(QtGui.QTextDocument.FindBackward)
        cursor = self.document().find(*args)
        if cursor.position() >= 0:
            self.setTextCursor(cursor)

    def set_line_number(self):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if hasattr(self.get_main_window(), 'status_bar'):
            self.get_main_window().status_bar.set_line_number(self.get_current_row_number(),
                                                              self.get_current_col_number(),
                                                              self.textCursor().columnNumber() + 1)

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
        if hasattr(self.get_main_window(), 'status_bar'):
            if self.bom:
                self.get_main_window().status_bar.set_codec(self.codec + u" BOM付")
            else:
                self.get_main_window().status_bar.set_codec(self.codec)

    def reformat(self):
        """
        ソース整形
        """
        text = self.document().toPlainText()
        if not text:
            return
        # try:
        p = SqlParser()
        parser = p.build()
        lex = SqlLexer()
        lexer = lex.build()
        result = parser.parse(unicode(text), lexer=lexer)
        if result:
            text = result.to_sql()
            if not (p.errors + lex.errors):
                cursor = QtGui.QTextCursor(self.document())
                cursor.beginEditBlock()
                cursor.select(QtGui.QTextCursor.Document)
                cursor.removeSelectedText()
                cursor.insertText(text)
                cursor.endEditBlock()
        return p.errors + lex.errors
        # except Exception, ex:
        #     print ex
        #     return [ex.message]


class RulerArea(QtGui.QFrame):
    def __init__(self, parent):
        super(RulerArea, self).__init__(parent)
        self.editor = parent


class LineNumberArea(QtGui.QWidget):
    def __init__(self, parent):
        super(LineNumberArea, self).__init__(parent)
        self.editor = parent
        self.is_dragged = False
        self.select_start_line = -1
        self.select_end_line = -1

        css = '''
        LineNumberArea {
            font-family: "ＭＳ ゴシック";
            font-size: 12px;
            font-weight: 100;
            color: blue;
            border-right: 1px solid blue;
            background-color: red;
        }
        '''
        self.setStyleSheet(css)

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
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


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(850, 550)
    window.show()
    sys.exit(app.exec_())
