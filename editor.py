#coding: UTF-8
#!/usr/bin/env python

import os, re
import common, constants

from PyQt4 import QtCore, QtGui, QtSql
from highlighter import SqlHighlighter
from sqlparser import SqlLexer, SqlParser


class Editors(QtGui.QTabWidget):
    def __init__(self, parent, options):
        super(Editors, self).__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.options = options

        self.untitled_name_index = 0
        self.setTabBar(EditorTabBar())
        self.tabCloseRequested.connect(self.removeTab)
        self.currentChanged.connect(self.current_changed)

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

        editor = SqlEditor(self, path, options=self.options)
        self.addTab(editor, filename)
        self.setCurrentWidget(editor)
        if path:
            self.setTabToolTip(self.currentIndex(), path)
        editor.setWindowState(QtCore.Qt.WindowActive)
        editor.setFocus(QtCore.Qt.ActiveWindowFocusReason)
        return editor.code_editor

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
                editor = self.widget(i).code_editor
                if editor.path == path:
                    return editor
        return None

    def get_main_window(self):
        return self.parentWidget()

    def removeTab(self, index):
        super(Editors, self).removeTab(index)
        if self.count() == 0:
            self.add_editor(None)

    def current_changed(self, index):
        tab = self.currentWidget()
        if isinstance(tab, SqlEditor):
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
        }
        QTabBar:tab:selected {
            color: blue;
            border-color: blue;
            background-color: white;
            border-bottom-width: 0px;
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


class SqlEditor(QtGui.QWidget):
    def __init__(self, parent=None, path=None, codec=None, options=None):
        super(SqlEditor, self).__init__(parent)
        self.splitter = None
        self.code_editor = None
        self.table_view = SqlTableResult()
        self.query_model = None
        self.connection = None
        self.status_bar = None
        self.setContentsMargins(0,0,0,0)
        self.init_layout(path, codec)
        self.options = options

        css = '''
        QTableView {
            background-color: rgb(255, 251, 240);
            border: none;
        }
        QStatusBar {
            background-color: rgb(240, 240, 240);
            border-top: 1px solid lightgray;
        }
        '''
        self.setStyleSheet(css)

    def init_layout(self, path, codec):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(0)
        layout.setMargin(0)
        # エディター
        self.splitter = QtGui.QSplitter(QtCore.Qt.Vertical, self)
        self.code_editor = CodeEditor(self.splitter, path, codec, options=self.options)
        self.splitter.addWidget(self.code_editor)
        layout.addWidget(self.splitter)
        # ステータスバー
        self.status_bar = EditorStatusBar(self)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def execute_sql(self):
        sql = self.code_editor.toPlainText()
        if not self.connection.isOpen():
            self.connection.open()

        self.query_model = self.connection.query(sql)
        if self.query_model:
            if self.query_model.lastError().isValid():
                last_error = self.query_model.lastError()
                QtGui.QMessageBox.information(self, last_error.driverText(), last_error.databaseText())
            else:
                self.table_view.clearSpans()
                self.table_view.setModel(self.query_model)
                self.status_bar.showMessage(u'%s 件のレコードが取得されました。' % (self.query_model.rowCount(),))
                self.splitter.addWidget(self.table_view)


class SqlTableResult(QtGui.QTableView):
    def __init__(self, parent=None):
        super(SqlTableResult, self).__init__(parent)
        # 行の高さを設定
        self.verticalHeader().setDefaultSectionSize(22)
        # ヘッダーを設定
        self.setHorizontalHeader(SqlResultHeader())


class SqlResultHeader(QtGui.QHeaderView):
    def __init__(self, parent=None):
        super(SqlResultHeader, self).__init__(QtCore.Qt.Horizontal, parent)
        self.setClickable(True)

        css = '''
        QHeaderView {
            border: 1px solid lightgray;
            border-left-width: 0px;
            border-top-width: 0px;
            border-right-width: 0px;
            background-color: rgb(255, 251, 240);
        }
        QHeaderView::section {
            border: 1px solid gray;
        }
        '''
        self.setStyleSheet(css)

    def sizeHint(self):
        base_size = QtGui.QHeaderView.sizeHint(self)
        base_size.setHeight(44)
        return base_size

    def paintSection(self, painter, rect, logical_index):
        record = self.model().record()
        field = record.field(logical_index)
        name = field.name() if field.name() else u"(列 %s)" % (logical_index + 1,)
        type_length = u"%s(%s)" % (common.get_db_type(field.type()), field.length())
        # 列名のスタイル
        t_rect = QtCore.QRect(rect.x(), rect.y(), rect.width()-1, rect.height() / 2)
        gradient = QtGui.QLinearGradient(t_rect.topLeft(), t_rect.bottomLeft())
        gradient.setColorAt(0, QtCore.Qt.white)
        gradient.setColorAt(0.5, QtGui.QColor(246, 247, 249))
        gradient.setColorAt(1, QtCore.Qt.white)
        painter.fillRect(t_rect, QtGui.QBrush(gradient))
        painter.setPen(QtGui.QColor(216, 213, 204))
        painter.drawLine(t_rect.bottomLeft(), t_rect.bottomRight())
        painter.drawLine(rect.topRight(), rect.bottomRight())
        # 列型、長さなどのスタイル
        b_rect = QtCore.QRect(rect.x(), rect.y() + (rect.height() / 2), rect.width() - 1, rect.height() / 2)
        painter.fillRect(b_rect, QtGui.QBrush(QtGui.QColor(255, 251, 240)))
        painter.setPen(QtCore.Qt.black)
        painter.drawText(t_rect, QtCore.Qt.AlignCenter, name)
        painter.drawText(b_rect, QtCore.Qt.AlignCenter, type_length)


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
        self.finding = Finding(self)
        self.option = EditorOption()
        self.options = options
        self.bookmarks = []

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
        self.setContentsMargins(0,0,0,0)

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
            background-color: rgb(255, 251, 240);
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
        return self.get_tab_window().parentWidget()

    def get_tab_window(self):
        return self.parentWidget().parentWidget().parentWidget().parentWidget()

    def get_sql_editor(self):
        return self.parentWidget().parentWidget()

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
                self.get_tab_window().move_to_prev()
            else:
                super(CodeEditor, self).keyPressEvent(event)
        elif event.modifiers() == QtCore.Qt.ControlModifier:
            # Ctrl
            if event.key() == QtCore.Qt.Key_Tab:
                # Ctrl + Tab
                self.get_tab_window().move_to_next()
            else:
                super(CodeEditor, self).keyPressEvent(event)
        else:
            super(CodeEditor, self).keyPressEvent(event)

    def mousePressEvent(self, event):
        QtGui.QPlainTextEdit.mousePressEvent(self, event)
        btn = event.button()
        if event.modifiers() == QtCore.Qt.ControlModifier:
            if btn == QtCore.Qt.LeftButton:
                cursor = self.textCursor()
                cursor.select(QtGui.QTextCursor.WordUnderCursor)
                self.setTextCursor(cursor)

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
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        # self.ruler_area.setGeometry(QtCore.QRect(cr.left() + self.line_number_area_width(), cr.top(),
        #                                          cr.width() - self.line_number_area_width(), 20))

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
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

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
            status_bar.set_line_number(self.get_current_row_number(),
                                       self.get_current_col_number(),
                                       self.textCursor().columnNumber() + 1)

    def set_status_msg(self, msg):
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
        status_bar = self.get_status_bar()
        if status_bar:
            if self.bom:
                status_bar.set_codec(self.codec + u" BOM付")
            else:
                status_bar.set_codec(self.codec)

    def set_bookmark(self):
        cursor = self.textCursor()
        line = cursor.block().blockNumber()
        if line in self.bookmarks:
            self.bookmarks.remove(line)
        else:
            self.bookmarks.append(line)

    def next_bookmark(self):
        cursor = self.textCursor()
        block_number = cursor.block().blockNumber()
        self.finding.next_bookmark(block_number, self.bookmarks)

    def prev_bookmark(self):
        cursor = self.textCursor()
        block_number = cursor.block().blockNumber()
        self.finding.prev_bookmark(block_number, self.bookmarks)

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
        self.setStyleSheet(css)

    def paintEvent(self, event):
        super(EditorScrollBar, self).paintEvent(event)

        if self.orientation() == QtCore.Qt.Vertical and self.max_height and self.positions:
            painter = QtGui.QPainter(self)
            painter.setPen(QtGui.QColor(255, 150, 50))
            painter.setBrush(QtCore.Qt.yellow)
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
        return rect.height()

    def get_add_line_height(self):
        option = QtGui.QStyleOptionSlider()
        option.initFrom(self)
        rect = self.style().subControlRect(QtGui.QStyle.CC_ScrollBar, option, QtGui.QStyle.SC_ScrollBarAddLine, self)
        return rect.height()


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

    def sizeHint(self):
        return QtCore.QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setPen(self.palette().color(QtGui.QPalette.Window))
        painter.setBrush(self.palette().color(QtGui.QPalette.Window))
        painter.drawRect(0, 0, self.width(), self.height())
        painter.setPen(QtCore.Qt.blue)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        painter.setBrush(QtGui.QColor(0, 128, 192))

        block = self.editor.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top()
        bottom = top + self.editor.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                if self.editor.bookmarks and block_number in self.editor.bookmarks:
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
        self.txt_condition = QtGui.QLineEdit()
        if self.finding and self.finding.text:
            self.txt_condition.setText(self.finding.text)
            self.txt_condition.selectAll()
        label.setBuddy(self.txt_condition)
        sub_hbox.addWidget(label)
        sub_hbox.addWidget(self.txt_condition)
        left_vbox.addLayout(sub_hbox)
        left_vbox.addStretch()
        # 単語単位
        chk = QtGui.QCheckBox(u"単語単位で探す(&W)")
        if self.finding and self.finding.is_whole_word:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_whole_word)
        left_vbox.addWidget(chk)
        # 大文字と小文字を区別する
        chk = QtGui.QCheckBox(u"大文字と小文字を区別する(&C)")
        if self.finding and self.finding.is_case_sensitive:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_case_sensitive)
        left_vbox.addWidget(chk)
        # 正規表現
        chk = QtGui.QCheckBox(u"正規表現で探す(&E)")
        if self.finding and self.finding.is_regular:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_regular)
        left_vbox.addWidget(chk)
        # 見つからないときにメッセージ表示
        chk = QtGui.QCheckBox(u"見つからないときにメッセージ表示(&M)")
        if self.finding and self.finding.is_show_message:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_show_message)
        left_vbox.addWidget(chk)
        # 検索ダイアログを自動的に閉じる
        chk = QtGui.QCheckBox(u"検索ダイアログを自動的に閉じる(&L)")
        if self.finding and self.finding.is_auto_close:
            chk.setCheckState(QtCore.Qt.Checked)
        chk.stateChanged.connect(self.set_auto_close)
        left_vbox.addWidget(chk)
        # 先頭（末尾）から再検索する
        chk = QtGui.QCheckBox(u"先頭（末尾）から再検索する(&Z)")
        if self.finding and self.finding.is_research:
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
        self.finding.is_whole_word = (state == QtCore.Qt.Checked)

    def set_case_sensitive(self, state):
        self.finding.is_case_sensitive = (state == QtCore.Qt.Checked)

    def set_regular(self, state):
        self.finding.is_regular = (state == QtCore.Qt.Checked)

    def set_show_message(self, state):
        self.finding.is_show_message = (state == QtCore.Qt.Checked)

    def set_auto_close(self, state):
        self.finding.is_auto_close = (state == QtCore.Qt.Checked)

    def set_research(self, state):
        self.finding.is_research = (state == QtCore.Qt.Checked)

    def find_next(self):
        self.finding.text = self.txt_condition.text()
        self.get_editor().finding = self.finding
        self.get_editor().find_text(False)
        if self.finding.is_auto_close:
            self.reject()

    def find_prev(self):
        self.finding.text = self.txt_condition.text()
        self.get_editor().finding = self.finding
        self.get_editor().find_text(True)
        if self.finding.is_auto_close:
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


class SqlDatabaseDialog(QtGui.QDialog):

    TITLE = u"SqlServer接続"

    def __init__(self, parent=None):
        super(SqlDatabaseDialog, self).__init__(parent)
        self.txt_server_name = None
        self.txt_database_name = None
        self.txt_user = None
        self.txt_password = None
        self.connection = None

        self.setModal(True)
        self.init_layout()
        self.setFixedSize(320, 160)
        self.setWindowTitle(SqlDatabaseDialog.TITLE)

        css = '''
        QFormLayout {
            width: 160px;
            border: 1px solid red;
        }
        '''
        self.setStyleSheet(css)

    def init_layout(self):
        layout = QtGui.QVBoxLayout()
        layout.setSpacing(5)
        layout.setMargin(10)
        form = QtGui.QFormLayout()
        form.setMargin(0)
        self.txt_server_name = QtGui.QLineEdit("mfv9mapdb03")
        form.addRow(u"サーバー名：", self.txt_server_name)

        self.txt_database_name = QtGui.QLineEdit("GIS_YOUCHI_BEKKI")
        form.addRow(u"データベース名：", self.txt_database_name)

        self.txt_user = QtGui.QLineEdit("sa")
        form.addRow(u"ユーザ名：", self.txt_user)

        self.txt_password = QtGui.QLineEdit("Pasco111")
        self.txt_password.setEchoMode(QtGui.QLineEdit.Password)
        form.addRow(u"パスワード：", self.txt_password)

        bottom_hbox = QtGui.QHBoxLayout()
        bottom_hbox.addStretch()
        btn = QtGui.QPushButton(u"接続(&C)")
        btn.clicked.connect(self.connect_database)
        bottom_hbox.addWidget(btn)
        btn = QtGui.QPushButton(u"キャンセル(&X)")
        btn.clicked.connect(self.reject)
        bottom_hbox.addWidget(btn)
        bottom_hbox.addStretch()

        layout.addLayout(form)
        layout.addLayout(bottom_hbox)
        self.setLayout(layout)

    def connect_database(self):
        server_name = self.txt_server_name.text()
        database_name = self.txt_database_name.text()
        user_name = self.txt_user.text()
        password = self.txt_password.text()
        if server_name and database_name and user_name and password:
            connection = Connection(constants.DATABASE_SQL_SERVER, server_name, database_name, user_name, password)
            if connection.open():
                connection.close()
                self.connection = connection
                self.accept()
            else:
                error = connection.lastError()
                if error:
                    msg = error.text()
                else:
                    msg = u"データベールに接続できません！"
                QtGui.QMessageBox.information(self, SqlDatabaseDialog.TITLE, msg)
        else:
            QtGui.QMessageBox.information(self, SqlDatabaseDialog.TITLE, u"入力してない項目があります！")


class Finding:
    def __init__(self, editor):
        self.text = ''
        self.is_whole_word = False
        self.is_case_sensitive = False
        self.is_regular = False
        self.is_show_message = False
        self.is_auto_close = False
        self.is_research = False
        self.editor = editor

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

    def find_text(self, is_back=False):
        count = self.show_finded_text_pos()

        reg = self.get_find_reg()
        if not reg:
            return

        cursor = self.editor.textCursor()
        args = [reg, cursor]
        if is_back:
            args.append(QtGui.QTextDocument.FindBackward)
        cursor = self.editor.document().find(*args)
        self.editor.highlight_text(self.get_find_reg())
        if cursor.position() >= 0:
            self.editor.setTextCursor(cursor)
            self.editor.set_status_msg("")
        else:
            if self.is_research and count > 0:
                # 先頭から再検索
                cursor = self.editor.textCursor()
                if is_back:
                    cursor.movePosition(QtGui.QTextCursor.End, QtGui.QTextCursor.MoveAnchor)
                else:
                    cursor.movePosition(QtGui.QTextCursor.Start, QtGui.QTextCursor.MoveAnchor)
                self.editor.setTextCursor(cursor)
                self.find_text(is_back)
                msg = u"▲末尾" if is_back else u"▼先頭"
                msg += u"から再検索しました"
                self.editor.set_status_msg(msg)
            else:
                msg = u"△" if is_back else u"▽"
                msg += u"見つかりませんでした"
                self.editor.set_status_msg(msg)
                if self.is_show_message:
                    self.editor.show_message_box(msg, u"%sに文字列「%s」が見つかりませんでした！" % (u"後方(↑)" if is_back else u"前方(↓)", self.text))

    def show_finded_text_pos(self):
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

    def next_bookmark(self, block_number, bookmarks):
        if bookmarks:
            line_no = self.get_block_number(block_number, bookmarks, True)
            if line_no:
                self.editor.jump_to_line(line_no)

    def prev_bookmark(self, block_number, bookmarks):
        if bookmarks:
            line_no = self.get_block_number(block_number, bookmarks, False)
            if line_no:
                self.editor.jump_to_line(line_no)

    def get_block_number(self, block_number, bookmarks, is_next=True):
        lst = sorted(bookmarks) if is_next else sorted(bookmarks, reverse=True)
        for line_no in lst:
            if is_next:
                if line_no > block_number:
                    return line_no
            else:
                if line_no < block_number:
                    return line_no

        return None


class Connection:
    def __init__(self, driver_type, server_name, database_name, user_name, password):
        self.db = None
        self.driver_type = driver_type
        self.server_name = server_name
        self.database_name = database_name
        self.user_name = user_name
        self.password = password

        self.init_database()

    def init_database(self):
        conn_format = "DRIVER={{SQL Server}};Server={0};Database={1};Uid={2};Pwd={3};"
        connection_string = conn_format.format(self.server_name, self.database_name, self.user_name, self.password)
        db = QtSql.QSqlDatabase.database(self.get_connection_name(), False)
        if not db.isValid():
            self.db = QtSql.QSqlDatabase.addDatabase("QODBC", self.get_connection_name())
            self.db.setDatabaseName(connection_string)
        else:
            self.db = db

    def get_connection_name(self):
        return ur"{0}@{1}".format(self.database_name, self.server_name)

    def get_databases(self):
        sql = "select name from master.dbo.sysdatabases order by name"
        if not self.db.isOpen():
            self.db.open()
        query = QtSql.QSqlQuery(sql, self.db)
        databases = []
        while query.next():
            databases.append(query.value(0).toString())
        return databases

    def open(self):
        return self.db.open()

    def close(self):
        return self.db.close()

    def isOpen(self):
        return self.db.isOpen()

    def query(self, sql):
        if sql and self.db:
            query_model = QtSql.QSqlQueryModel()
            query_model.setQuery(sql, self.db)
            return query_model
        return None

    def lastError(self):
        return self.db.lastError()