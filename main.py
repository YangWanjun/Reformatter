# coding: UTF-8
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from highlighter import SqlHighlighter


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.editor = None
        self.highlighter = None

        self.init_editor()
        
        self.statusBar = StatusBar()
        self.setStatusBar(self.statusBar)
        self.setCentralWidget(self.editor)
        self.setWindowTitle("Reformatter")

    def about(self):
        QtGui.QMessageBox.about(self, "About Syntax Highlighter",
                "<p>The <b>Syntax Highlighter</b> example shows how to "
                "perform simple syntax highlighting by subclassing the "
                "QSyntaxHighlighter class and describing highlighting "
                "rules using regular expressions.</p>")

    def init_editor(self):
        font = QtGui.QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)

        self.editor = CodeEditor()
        self.editor.setFont(font)
        self.highlighter = SqlHighlighter(self.editor.document())

    def keyPressEvent(self, event):
        if event.modifiers() == (QtCore.Qt.ControlModifier | QtCore.Qt.ShiftModifier):
            if event.key() == QtCore.Qt.Key_F:
                self.highlighter.reformat()


class StatusBar(QtGui.QStatusBar):
    def __init__(self, parent=None):
        super(StatusBar, self).__init__(parent)
        
        css = '''
        QLabel {
            font-family: Courier;
            font-size: 10;
            color: blue;
            border: 1px solid gray;
            qproperty-alignment: 'AlignVCenter | AlignHCenter';
            qproperty-wordWrap: true;
        }
        '''
        self.setStyleSheet(css)

        self.init_layout()

    def init_layout(self):
        # 行番号、列番号を表示する。
        label = QtGui.QLabel()
        label.setFixedWidth(140)
        label.setText(u"%s 行 %s 列" % (0, 0))
        self.addPermanentWidget(label)


class CodeEditor(QtGui.QPlainTextEdit):
    def __init__(self, parent=None):
        super(CodeEditor, self).__init__(parent)

        self.line_number_area = LineNumberArea(self)

        self.connect(self, QtCore.SIGNAL('blockCountChanged(int)'), self.update_line_number_area_width)
        self.connect(self, QtCore.SIGNAL('updateRequest(QRect,int)'), self.update_line_number_area)
        self.connect(self, QtCore.SIGNAL('cursorPositionChanged()'), self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_width(self):
        digits = 1
        max_count = max(1, self.blockCount())
        while max_count >= 10:
            max_count /= 10
            digits += 1
        if digits < 3:
            digits = 3

        space = 6 + self.fontMetrics().width('9') * digits
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
                painter.drawText(0, top, self.line_number_area.width() - 2, self.fontMetrics().height(),
                                 QtCore.Qt.AlignRight, number)

            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1

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


class LineNumberArea(QtGui.QWidget):
    def __init__(self, parent=None):
        super(LineNumberArea, self).__init__(parent)

        css = '''
        QWidget {
            font-family: Courier;
            font-size: 10;
            color: blue;
        }
        '''
        self.setStyleSheet(css)

    def sizeHint(self):
        return QtCore.QSize(self.parentWidget().line_number_area_width(), 0)

    def paintEvent(self, event):
        self.parentWidget().line_number_area_paint_event(event)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.resize(640, 512)
    window.show()
    sys.exit(app.exec_())
