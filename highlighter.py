# coding: UTF-8
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from sqlparser import SqlLexer


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None, doc_type=None):
        super(Highlighter, self).__init__(parent)

        self.doc_type = doc_type
        self.highlighting_rules = []
        self.multi_line_comment_format = None
        self.comment_start_expression = None
        self.comment_end_expression = None
        self.text_highlight_format = None
        self.text_highlight_list = []

    def init_rules(self, keyword_patterns):
        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(QtCore.Qt.blue)
        # keyword_format.setFontWeight(QtGui.QFont.Bold)

        self.highlighting_rules = self.highlighting_rules + [(QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), keyword_format) for pattern in keyword_patterns]

        quotation_format = QtGui.QTextCharFormat()
        quotation_format.setForeground(QtCore.Qt.red)
        self.highlighting_rules.append((QtCore.QRegExp("\'[^']*\'"), quotation_format))

        single_line_comment_format = QtGui.QTextCharFormat()
        single_line_comment_format.setForeground(QtCore.Qt.darkGreen)
        self.highlighting_rules.append((QtCore.QRegExp("--[^\n]*"), single_line_comment_format))

        self.multi_line_comment_format = QtGui.QTextCharFormat()
        self.multi_line_comment_format.setForeground(QtCore.Qt.darkGreen)

        self.comment_start_expression = QtCore.QRegExp("/\\*")
        self.comment_end_expression = QtCore.QRegExp("\\*/")

        self.text_highlight_format = QtGui.QTextCharFormat()
        self.text_highlight_format.setBackground(QtGui.QBrush(QtCore.Qt.yellow))

    def highlightBlock(self, text):
        for pattern, formatter in self.highlighting_rules:
            expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, formatter)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)
        start_index = 0
        if self.previousBlockState() != 1:
            start_index = self.comment_start_expression.indexIn(text)

        while start_index >= 0:
            end_index = self.comment_end_expression.indexIn(text, start_index)

            if end_index == -1:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_index - start_index + self.comment_end_expression.matchedLength()

            self.setFormat(start_index, comment_length, self.multi_line_comment_format)
            start_index = self.comment_start_expression.indexIn(text, start_index + comment_length)

        for pattern in self.text_highlight_list:
            if isinstance(pattern, QtCore.QRegExp):
                expression = pattern
            else:
                expression = QtCore.QRegExp(pattern)
            index = expression.indexIn(text)
            while index >= 0:
                length = expression.matchedLength()
                self.setFormat(index, length, self.text_highlight_format)
                index = expression.indexIn(text, index + length)


class SqlHighlighter(Highlighter):
    def __init__(self, parent=None):
        Highlighter.__init__(self, parent, 'sql')
        
        keyword_patterns = [r'\b' + keyword + r'\b' for keyword in SqlLexer.reserved.values()]

        format = QtGui.QTextCharFormat()
        format.setForeground(QtGui.QColor('#FF00FF'))

        global_patterns = [r'@@' + _global + r'\b' for _global in SqlLexer.globals]
        for pattern in global_patterns:
           self.highlighting_rules.append((QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), format))

        aggregate_patterns = [r'\b' + _item + r'\b' for _item in SqlLexer.func_aggregate]
        for pattern in aggregate_patterns:
           self.highlighting_rules.append((QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), format))

        conversion_patterns = [r'\b' + _item + r'\b' for _item in SqlLexer.func_conversion]
        for pattern in conversion_patterns:
           self.highlighting_rules.append((QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), format))

        func_str_patterns = [r'\b' + _item + r'\b' for _item in MSSQL_FUNC_STRING]
        for pattern in func_str_patterns:
           self.highlighting_rules.append((QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), format))

        meta_data_patterns = [r'\b' + meta_data + r'\b' for meta_data in SqlLexer.meta_datas]
        for pattern in meta_data_patterns:
           self.highlighting_rules.append((QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), format))

        self.init_rules(keyword_patterns)


MSSQL_AGGREGATE = [
    'AVG',
    'MIN',
    'CHECKSUM_AGG',
    'SUM',
    'COUNT',
    'STDEV',
    'COUNT_BIG',
    'STDEVP',
    'GROUPING',
    'VAR',
    'GROUPING_ID',
    'VARP',
    'MAX',
]


MSSQL_FUNC_CONVERSION = [
    'CAST',
    'CONVERT',
]


MSSQL_FUNC_STRING = [
    'ASCII',
    'LTRIM',
    'SOUNDEX',
    'CHAR',
    'NCHAR',
    'SPACE',
    'CHARINDEX',
    'PATINDEX',
    'STR',
    'CONCAT',
    'QUOTENAME',
    'STRING_ESCAPE',
    'DIFFERENCE',
    'REPLACE',
    'STRING_SPLIT',
    'FORMAT',
    'REPLICATE',
    'STUFF',
    'LEFT',
    'REVERSE',
    'SUBSTRING',
    'LEN',
    'RIGHT',
    'UNICODE',
    'LOWER',
    'RTRIM',
    'UPPER',
]
