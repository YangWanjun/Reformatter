# coding: UTF-8
#!/usr/bin/env python

from PyQt4 import QtCore, QtGui
from sqlparser import SqlLexer, SqlParser


class Highlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent=None, doc_type=None):
        super(Highlighter, self).__init__(parent)

        self.doc_type = doc_type
        self.highlighting_rules = None
        self.multi_line_comment_format = None
        self.comment_start_expression = None
        self.comment_end_expression = None

    def init_rules(self, keyword_patterns):
        keyword_format = QtGui.QTextCharFormat()
        keyword_format.setForeground(QtCore.Qt.blue)
        # keyword_format.setFontWeight(QtGui.QFont.Bold)

        self.highlighting_rules = [(QtCore.QRegExp(pattern, QtCore.Qt.CaseInsensitive), keyword_format)
                                   for pattern in keyword_patterns]

        single_line_comment_format = QtGui.QTextCharFormat()
        single_line_comment_format.setForeground(QtCore.Qt.darkGreen)
        self.highlighting_rules.append((QtCore.QRegExp("--[^\n]*"), single_line_comment_format))

        self.multi_line_comment_format = QtGui.QTextCharFormat()
        self.multi_line_comment_format.setForeground(QtCore.Qt.darkGreen)

        quotation_format = QtGui.QTextCharFormat()
        quotation_format.setForeground(QtCore.Qt.red)
        self.highlighting_rules.append((QtCore.QRegExp("\'[^']*\'"), quotation_format))

        self.comment_start_expression = QtCore.QRegExp("/\\*")
        self.comment_end_expression = QtCore.QRegExp("\\*/")

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

    def reformat(self):
        """
        ソース整形
        """
        text = self.document().toPlainText()
        if not self.doc_type and not text:
            return
        # try:
        p = SqlParser()
        parser = p.build()
        lex = SqlLexer()
        lexer = lex.build()
        result = parser.parse(unicode(text), lexer=lexer)
        if result:
            text = result.to_sql()
        self.document().setPlainText(text)
        return p.errors + lex.errors
        # except Exception, ex:
        #     print ex
        #     return [ex.message]


class SqlHighlighter(Highlighter):
    def __init__(self, parent=None):
        Highlighter.__init__(self, parent, 'sql')
        
        keyword_patterns = [
            r'\bABSOLUTE\b', r'\bACTION\b', r'\bADD\b', r'\bALL\b', r'\bALLOCATE\b', r'\bALTER\b',
            r'\bAND\b', r'\bANY\b', r'\bARE\b', r'\bAS\b', r'\bASC\b', r'\bASSERTION\b', r'\bAT\b',
            r'\bAUTHORIZATION\b', r'\bAVG\b', r'\bBEGIN\b', r'\bBETWEEN\b', r'\bBIT\b', r'\bBIT_LENGTH\b',
            r'\bBOTH\b', r'\bBY\b', r'\bCASCADE\b', r'\bCASCADED\b', r'\bCASE\b', r'\bCAST\b',
            r'\bCATALOG\b', r'\bCHAR\b', r'\bCHARACTER\b', r'\bCHARACTER_LENGTH\b', r'\bCHAR_LENGTH\b',
            r'\bCHECK\b', r'\bCLOSE\b', r'\bCOALESCE\b', r'\bCOLLATE\b', r'\bCOLLATION\b', r'\bCOLUMN\b',
            r'\bCOMMIT\b', r'\bCONNECT\b', r'\bCONNECTION\b', r'\bCONSTRAINT\b', r'\bCONSTRAINTS\b',
            r'\bCONTINUE\b', r'\bCONVERT\b', r'\bCORRESPONDING\b', r'\bCOUNT\b', r'\bCREATE\b',
            r'\bCROSS\b', r'\bCURRENT\b', r'\bCURRENT_DATE\b', r'\bCURRENT_TIME\b',
            r'\bCURRENT_TIMESTAMP\b', r'\bCURRENT_USER\b', r'\bCURSOR\b', r'\bDATE\b', r'\bDAY\b',
            r'\bDEALLOCATE\b', r'\bDEC\b', r'\bDECIMAL\b', r'\bDECLARE\b', r'\bDEFAULT\b',
            r'\bDEFERRABLE\b', r'\bDEFERRED\b', r'\bDELETE\b', r'\bDESC\b', r'\bDESCRIBE\b',
            r'\bDESCRIPTOR\b', r'\bDIAGNOSTICS\b', r'\bDISCONNECT\b', r'\bDISTINCT\b', r'\bDOMAIN\b',
            r'\bDOUBLE\b', r'\bDROP\b', r'\bELSE\b', r'\bEND\b', r'\bESCAPE\b', r'\bEXCEPT\b',
            r'\bEXCEPTION\b', r'\bEXEC\b', r'\bEXECUTE\b', r'\bEXISTS\b', r'\bEXTERNAL\b', r'\bEXTRACT\b',
            r'\bFALSE\b', r'\bFETCH\b', r'\bFIRST\b', r'\bFLOAT\b', r'\bFOR\b', r'\bFOREIGN\b',
            r'\bFOUND\b', r'\bFROM\b', r'\bFULL\b', r'\bGET\b', r'\bGLOBAL\b', r'\bGO\b', r'\bGOTO\b',
            r'\bGRANT\b', r'\bGROUP\b', r'\bHAVING\b', r'\bHOUR\b', r'\bIDENTITY\b', r'\bIMMEDIATE\b',
            r'\bIN\b', r'\bINDICATOR\b', r'\bINITIALLY\b', r'\bINNER\b', r'\bINPUT\b', r'\bINSENSITIVE\b',
            r'\bINSERT\b', r'\bINT\b', r'\bINTEGER\b', r'\bINTERSECT\b', r'\bINTERVAL\b', r'\bINTO\b',
            r'\bIS\b', r'\bISOLATION\b', r'\bJOIN\b', r'\bKEY\b', r'\bLANGUAGE\b', r'\bLAST\b',
            r'\bLEADING\b', r'\bLEFT\b', r'\bLEVEL\b', r'\bLIKE\b', r'\bLOCAL\b', r'\bLOWER\b',
            r'\bMATCH\b', r'\bMAX\b', r'\bMIN\b', r'\bMINUTE\b', r'\bMODULE\b', r'\bMONTH\b',
            r'\bNAMES\b', r'\bNATIONAL\b', r'\bNATURAL\b', r'\bNCHAR\b', r'\bNEXT\b', r'\bNO\b',
            r'\bNOT\b', r'\bNULL\b', r'\bNULLIF\b', r'\bNUMERIC\b', r'\bOCTET_LENGTH\b', r'\bOF\b',
            r'\bON\b', r'\bONLY\b', r'\bOPEN\b', r'\bOPTION\b', r'\bOR\b', r'\bORDER\b', r'\bOUTER\b',
            r'\bOUTPUT\b', r'\bOVERLAPS\b', r'\bPAD\b', r'\bPARTIAL\b', r'\bPOSITION\b', r'\bPRECISION\b',
            r'\bPREPARE\b', r'\bPRESERVE\b', r'\bPRIMARY\b', r'\bPRIOR\b', r'\bPRIVILEGES\b',
            r'\bPROCEDURE\b', r'\bPUBLIC\b', r'\bREAD\b', r'\bREAL\b', r'\bREFERENCES\b', r'\bRELATIVE\b',
            r'\bRESTRICT\b', r'\bREVOKE\b', r'\bRIGHT\b', r'\bROLLBACK\b', r'\bROWS\b', r'\bSCHEMA\b',
            r'\bSCROLL\b', r'\bSECOND\b', r'\bSECTION\b', r'\bSELECT\b', r'\bSESSION\b',
            r'\bSESSION_USER\b', r'\bSET\b', r'\bSIZE\b', r'\bSMALLINT\b', r'\bSOME\b', r'\bSPACE\b',
            r'\bSQL\b', r'\bSQLCODE\b', r'\bSQLERROR\b', r'\bSQLSTATE\b', r'\bSUBSTRING\b', r'\bSUM\b',
            r'\bSYSTEM_USER\b', r'\bTABLE\b', r'\bTEMPORARY\b', r'\bTHEN\b', r'\bTIME\b',
            r'\bTIMESTAMP\b', r'\bTIMEZONE_HOUR\b', r'\bTIMEZONE_MINUTE\b', r'\bTO\b', r'\bTOP\b', r'\bTRAILING\b',
            r'\bTRANSACTION\b', r'\bTRANSLATE\b', r'\bTRANSLATION\b', r'\bTRIM\b', r'\bTRUE\b',
            r'\bUNION\b', r'\bUNIQUE\b', r'\bUNKNOWN\b', r'\bUPDATE\b', r'\bUPPER\b', r'\bUSAGE\b',
            r'\bUSER\b', r'\bUSING\b', r'\bVALUE\b', r'\bVALUES\b', r'\bVARCHAR\b', r'\bVARYING\b',
            r'\bVIEW\b', r'\bWHEN\b', r'\bWHENEVER\b', r'\bWHERE\b', r'\bWITH\b', r'\bWORK\b',
            r'\bWRITE\b', r'\bYEAR\b', r'\bZONE\b'
        ]

        self.init_rules(keyword_patterns)
