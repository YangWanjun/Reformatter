#coding: UTF-8
#!/usr/bin/env python

import common

from PyQt4 import QtCore, QtGui
from highlighter import SqlHighlighter


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.editor = None
        self.highlighter = None
        self.status_bar = None

        self.init_layout()

        self.setWindowIcon(QtGui.QIcon('logo.ico'))
        self.setCentralWidget(self.editor)
        self.setWindowTitle("Reformatter")

    def about(self):
        QtGui.QMessageBox.about(self, "About Syntax Highlighter",
                "<p>The <b>Syntax Highlighter</b> example shows how to "
                "perform simple syntax highlighting by subclassing the "
                "QSyntaxHighlighter class and describing highlighting "
                "rules using regular expressions.</p>")

    def init_layout(self):
        # エディター
        self.editor = CodeEditor(self)
        self.highlighter = SqlHighlighter(self.editor.document())
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
        for codec in sorted(QtCore.QTextCodec.availableCodecs()):
            action = QtGui.QAction(str(codec), codec_menu)
            self.connect(action, QtCore.SIGNAL('triggered()'), signal_mapper, QtCore.SLOT('map()'))
            signal_mapper.setMapping(action, str(codec))
            codec_menu.addAction(action)
        self.connect(signal_mapper, QtCore.SIGNAL('mapped(QString)'), self.menuItemClicked)
        file_menu.addSeparator()
        file_menu.addAction(u"終了(&X)", QtGui.qApp.quit, "Ctrl+Q")
        
        # 編集メニュー
        edit_menu = QtGui.QMenu(u"編集(&E)", self)
        self.menuBar().addMenu(edit_menu)
        
        edit_menu.addAction(u"右(末尾)の空白を削除", self.editor.delete_right_space, "ALT+R")

    def menuItemClicked(self, name):
        if name and self.editor.path:
            self.open_file(self.editor.path, name)

    def is_text_changed(self):
        return self.editor.document().isModified()

    def new_file(self):
        if self.is_text_changed():
            if QtGui.QMessageBox.question(self, u"確認", u"内容を破棄してもよろしいですか？", QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
                return

        self.editor.clear()

    def open_file(self, path=None, codec=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, u"開く", '', "Sql Files (*.sql);;All Files(*.*)")

        if path:
            codec = codec if codec else 'UTF-8'
            self.editor.path = path
            self.editor.codec = codec
            in_file = QtCore.QFile(path)
            if in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                byte_array = in_file.readAll()
                # text = str(text)
                text = QtCore.QTextCodec.codecForName(codec).toUnicode(byte_array)

                self.editor.setPlainText(text)

    def keyPressEvent(self, event):
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if event.key() == QtCore.Qt.Key_F:
                errors = self.highlighter.reformat()
                if errors:
                    self.set_status_message(errors[0])
                else:
                    self.set_status_message('Success!', 3000)

    def set_status_message(self, message, times=0):
        """
        ステータスバーにメッセージを表示する。
        """
        if self.status_bar:
            self.status_bar.showMessage(message, times)

    def closeEvent(self, event):
        if self.is_text_changed():
            if QtGui.QMessageBox.question(self, u"確認", u"内容を破棄してもよろしいですか？", QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel) == QtGui.QMessageBox.Cancel:
                event.ignore()
                return
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


class CodeEditor(QtGui.QPlainTextEdit):

    CODEC_LIST = ['UTF-8', 'UTF-16', 'UTF-32', 'SJIS', 'GB2312']

    def __init__(self, parent=None, path=None, codec=None):
        super(CodeEditor, self).__init__(parent)
        self.path = path
        self.codec = codec

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

        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.cursor_position_changed)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def delete_right_space(self):
        """
        行の右側（末尾）の空白を削除する。
        """
        cursor = self.textCursor()
        if cursor.hasSelection():
            print 'hasSelection'

    def get_tab_space_width(self):
        """
        タブの幅を取得する。
        """
        return self.get_char_width() * common.get_tab_space_count()

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

    def paintEvent(self, event):
        super(CodeEditor, self).paintEvent(event)

        # 縦線を表示する。
        if self.get_current_col_number() > 1:
            self.draw_cursor_line(QtCore.Qt.blue)
        self.draw_column_line(100, QtCore.Qt.lightGray)
        self.draw_eof_mark()
        self.draw_return_mark()
        self.draw_full_space()

    def resizeEvent(self, event):
        QtGui.QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))
        # self.ruler_area.setGeometry(QtCore.QRect(cr.left() + self.line_number_area_width(), cr.top(),
        #                                          cr.width() - self.line_number_area_width(), 20))

    def highlight_current_line(self):
        extra_selections = QtGui.QTextEdit.extraSelections(QtGui.QTextEdit())

        if not self.isReadOnly():
            selection = QtGui.QTextEdit.ExtraSelection()

            line_color = QtGui.QColor(QtCore.Qt.yellow).lighter(160)

            selection.format.setBackground(line_color)
            selection.format.setProperty(QtGui.QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)

        self.setExtraSelections(extra_selections)

    def update_line_number_area_width(self, i):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def get_char_width(self):
        font = self.currentCharFormat().font()
        return round(QtGui.QFontMetricsF(font).averageCharWidth())

    def get_current_row_number(self):
        return self.textCursor().blockNumber() + 1

    def get_current_col_number(self):
        r = self.cursorRect(self.textCursor())
        left_offset = r.left() - self.contentOffset().x() - self.document().documentMargin()
        return int(left_offset / self.get_char_width()) + 1

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

    def draw_return_mark(self):
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtGui.QColor(75, 172, 198))
        block = self.firstVisibleBlock()
        cur = self.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        position_eof = cur.position()

        while block.isValid():
            cur.setPosition(block.position())
            cur.movePosition(QtGui.QTextCursor.EndOfBlock)
            if cur.position() == position_eof:
                # 最後に改行がなく、EOF だった場合
                break
            r = self.cursorRect(cur)
            painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"↵")

            block = block.next()

    def draw_full_space(self):
        painter = QtGui.QPainter(self.viewport())
        painter.setPen(QtCore.Qt.lightGray)
        cur = self.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        reg = QtCore.QRegExp(ur'　|\t')
        cur = self.document().find(reg, cur, QtGui.QTextDocument.FindBackward)
        while cur.position() >= 0:
            text = cur.selectedText()
            cur.movePosition(QtGui.QTextCursor.Left)
            r = self.cursorRect(cur)
            if text == u'　':
                painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"□")
            elif text == '\t':
                painter.drawText(QtCore.QPointF(r.left(), r.bottom()), u"^")

            cur = self.document().find(reg, cur, QtGui.QTextDocument.FindBackward)

    def set_line_number(self):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if hasattr(self.parentWidget(), 'status_bar'):
            self.parentWidget().status_bar.set_line_number(self.get_current_row_number(),
                                                           self.get_current_col_number(),
                                                           self.textCursor().columnNumber() + 1)

    def setPlainText(self, text):
        super(CodeEditor, self).setPlainText(text)
        self.codec = self.codec if self.codec else 'UTF-8'
        if hasattr(self.parentWidget(), 'status_bar'):
            self.parentWidget().status_bar.set_codec(self.codec)


class RulerArea(QtGui.QFrame):
    def __init__(self, parent):
        super(RulerArea, self).__init__(parent)
        self.editor = parent


class LineNumberArea(QtGui.QFrame):
    def __init__(self, parent):
        super(LineNumberArea, self).__init__(parent)
        self.editor = parent

        css = '''
        QWidget {
            font-family: "ＭＳ ゴシック";
            font-size: 12px;
            font-weight: 100;
            color: blue;
            border-right: 1px solid blue;
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


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(850, 550)
    window.show()
    sys.exit(app.exec_())
