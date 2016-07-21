# coding: UTF-8
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from highlighter import SqlHighlighter


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.editor = None
        self.highlighter = None
        self.status_bar = None

        self.init_layout()
        
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
        # メニュー
        file_menu = QtGui.QMenu(u"ファイル(&F)", self)
        self.menuBar().addMenu(file_menu)

        file_menu.addAction(u"新規(&N)", self.new_file, "Ctrl+N")
        file_menu.addAction(u"開く(&O)", self.open_file, "Ctrl+O")
        file_menu.addAction(u"終了(&X)", QtGui.qApp.quit, "Ctrl+Q")

    def new_file(self):
        self.editor.clear()

    def open_file(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, u"開く", '', "Sql Files (*.sql);;All Files(*.*)")

        if path:
            in_file = QtCore.QFile(path)
            if in_file.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):
                text = in_file.readAll()
                text = str(text)

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


class StatusBar(QtGui.QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        
        css = '''
        QLabel {
            font-family: Courier;
            font-size: 10;
            border: 1px inset gray;
            qproperty-alignment: 'AlignVCenter | AlignHCenter';
            qproperty-wordWrap: true;
        }
        '''
        self.setStyleSheet(css)

        self.lbl_line_no = None
        self.init_layout()

    def init_layout(self):
        # 行番号、列番号を表示する。
        self.lbl_line_no = QtGui.QLabel()
        self.lbl_line_no.setFixedWidth(180)
        self.lbl_line_no.setText(u"%s 行 %s 列 %s 文字" % (1, 1, 1))
        self.addPermanentWidget(self.lbl_line_no)

    def set_line_number(self, line, col, length):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if self.lbl_line_no:
            self.lbl_line_no.setText(u"%s 行 %s 列 %s 文字" % (line, col, length))


class CodeEditor(QtGui.QPlainTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)

        font = QtGui.QFont()
        font.setFamily(u'ＭＳ ゴシック')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setCursorWidth(2)

        self.line_number_area = LineNumberArea(self)

        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.cursor_position_changed)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

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

        space = 8 + self.fontMetrics().width('9') * digits
        return space

    def line_number_area_paint_event(self, event):
        painter = QtGui.QPainter(self.line_number_area)

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.drawText(0, top, self.line_number_area.width() - 5, self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

    def paintEvent(self, event):
        super(CodeEditor, self).paintEvent(event)

        # 縦線を表示する。
        if self.get_current_col_number() > 1:
            self.draw_column_line(self.get_current_col_number() - 1, QtCore.Qt.blue)
        self.draw_column_line(100, QtCore.Qt.lightGray)
        self.draw_eof_mark()
        self.draw_return_mark()

    def resizeEvent(self, event):
        QtGui.QPlainTextEdit.resizeEvent(self, event)

        cr = self.contentsRect()
        self.line_number_area.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

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

    def get_current_row_number(self):
        return self.textCursor().blockNumber() + 1

    def get_current_col_number(self):
        text = self.textCursor().block().text().left(self.textCursor().columnNumber())
        return len(text.toLocal8Bit()) + 1

    def draw_column_line(self, col, color):
        font = self.currentCharFormat().font()
        left = round(QtGui.QFontMetricsF(font).averageCharWidth() * col)
        left += self.contentOffset().x() + self.document().documentMargin()

        painter = QtGui.QPainter(self.viewport())
        painter.setPen(color)
        painter.drawLine(left, 0, left, self.height())
        self.viewport().update()

    def draw_eof_mark(self):
        cur = self.textCursor()
        cur.movePosition(QtGui.QTextCursor.End)
        r = self.cursorRect(cur)
        painter = QtGui.QPainter(self.viewport())
        painter.setBrush(QtCore.Qt.black)
        painter.drawRect(QtCore.QRectF(r.left(), r.top(), self.fontMetrics().width('[EOF]'), r.height()))
        painter.setPen(QtCore.Qt.white)
        painter.drawText(QtCore.QPointF(r.left(), r.bottom()), "[EOF]")

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

    def set_line_number(self):
        """
        ステータスバーの行番号と列番号を設定する。
        """
        if hasattr(self.parentWidget(), 'status_bar'):
            self.parentWidget().status_bar.set_line_number(self.get_current_row_number(),
                                                           self.get_current_col_number(),
                                                           self.textCursor().columnNumber() + 1)


class LineNumberArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LineNumberArea, self).__init__(parent)

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
        return QtCore.QSize(self.parentWidget().line_number_area_width(), 0)

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.drawLine(self.width() - 1, 0, self.width() - 1, self.height())
        self.parentWidget().line_number_area_paint_event(event)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(850, 550)
    window.show()
    sys.exit(app.exec_())
