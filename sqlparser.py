# coding: UTF-8
"""
See links for example yacc SQL grammars:
http://yaxx.googlecode.com/svn/trunk/sql/sql2.y
# TODO: support select fname + ' ' + lname from people
see grammar above
# TODO: break sqlparser into its own file, have it instantiate AstNodes via
a factory, so a client of sqlparser can customize (derive from AstNode) and
have custom actions
"""
from ply import lex, yacc


class SqlLexer(object):

    reserved = {
        'absolute'         : 'ABSOLUTE',
        'action'           : 'ACTION',
        'add'              : 'ADD',
        'all'              : 'ALL',
        'allocate'         : 'ALLOCATE',
        'alter'            : 'ALTER',
        'and'              : 'AND',
        'any'              : 'ANY',
        'are'              : 'ARE',
        'as'               : 'AS',
        'asc'              : 'ASC',
        'assertion'        : 'ASSERTION',
        'at'               : 'AT',
        'authorization'    : 'AUTHORIZATION',
        'avg'              : 'AVG',
        'begin'            : 'BEGIN',
        'between'          : 'BETWEEN',
        'bit'              : 'BIT',
        'bit_length'       : 'BIT_LENGTH',
        'both'             : 'BOTH',
        'by'               : 'BY',
        'cascade'          : 'CASCADE',
        'cascaded'         : 'CASCADED',
        'case'             : 'CASE',
        'cast'             : 'CAST',
        'catalog'          : 'CATALOG',
        'char'             : 'CHAR',
        'character'        : 'CHARACTER',
        'character_length' : 'CHARACTER_LENGTH',
        'char_length'      : 'CHAR_LENGTH',
        'check'            : 'CHECK',
        'close'            : 'CLOSE',
        'coalesce'         : 'COALESCE',
        'collate'          : 'COLLATE',
        'collation'        : 'COLLATION',
        'column'           : 'COLUMN',
        'commit'           : 'COMMIT',
        'connect'          : 'CONNECT',
        'connection'       : 'CONNECTION',
        'constraint'       : 'CONSTRAINT',
        'constraints'      : 'CONSTRAINTS',
        'continue'         : 'CONTINUE',
        'convert'          : 'CONVERT',
        'corresponding'    : 'CORRESPONDING',
        'count'            : 'COUNT',
        'create'           : 'CREATE',
        'cross'            : 'CROSS',
        'current'          : 'CURRENT',
        'current_date'     : 'CURRENT_DATE',
        'current_time'     : 'CURRENT_TIME',
        'current_timestamp' : 'CURRENT_TIMESTAMP',
        'current_user'     : 'CURRENT_USER',
        'cursor'           : 'CURSOR',
        'date'             : 'DATE',
        'day'              : 'DAY',
        'deallocate'       : 'DEALLOCATE',
        'dec'              : 'DEC',
        'decimal'          : 'DECIMAL',
        'declare'          : 'DECLARE',
        'default'          : 'DEFAULT',
        'deferrable'       : 'DEFERRABLE',
        'deferred'         : 'DEFERRED',
        'delete'           : 'DELETE',
        'desc'             : 'DESC',
        'describe'         : 'DESCRIBE',
        'descriptor'       : 'DESCRIPTOR',
        'diagnostics'      : 'DIAGNOSTICS',
        'disconnect'       : 'DISCONNECT',
        'distinct'         : 'DISTINCT',
        'domain'           : 'DOMAIN',
        'double'           : 'DOUBLE',
        'drop'             : 'DROP',
        'else'             : 'ELSE',
        'end'              : 'END',
        'escape'           : 'ESCAPE',
        'except'           : 'EXCEPT',
        'exception'        : 'EXCEPTION',
        'exec'             : 'EXEC',
        'execute'          : 'EXECUTE',
        'exists'           : 'EXISTS',
        'external'         : 'EXTERNAL',
        'extract'          : 'EXTRACT',
        'false'            : 'FALSE',
        'fetch'            : 'FETCH',
        'first'            : 'FIRST',
        'float'            : 'FLOAT',
        'for'              : 'FOR',
        'foreign'          : 'FOREIGN',
        'found'            : 'FOUND',
        'from'             : 'FROM',
        'full'             : 'FULL',
        'get'              : 'GET',
        'global'           : 'GLOBAL',
        'go'               : 'GO',
        'goto'             : 'GOTO',
        'grant'            : 'GRANT',
        'group'            : 'GROUP',
        'having'           : 'HAVING',
        'hour'             : 'HOUR',
        'identity'         : 'IDENTITY',
        'immediate'        : 'IMMEDIATE',
        'in'               : 'IN',
        'indicator'        : 'INDICATOR',
        'initially'        : 'INITIALLY',
        'inner'            : 'INNER',
        'input'            : 'INPUT',
        'insensitive'      : 'INSENSITIVE',
        'insert'           : 'INSERT',
        'int'              : 'INT',
        'integer'          : 'INTEGER',
        'intersect'        : 'INTERSECT',
        'interval'         : 'INTERVAL',
        'into'             : 'INTO',
        'is'               : 'IS',
        'isolation'        : 'ISOLATION',
        'join'             : 'JOIN',
        'key'              : 'KEY',
        'language'         : 'LANGUAGE',
        'last'             : 'LAST',
        'leading'          : 'LEADING',
        'left'             : 'LEFT',
        'level'            : 'LEVEL',
        'like'             : 'LIKE',
        'local'            : 'LOCAL',
        'lower'            : 'LOWER',
        'match'            : 'MATCH',
        'max'              : 'MAX',
        'min'              : 'MIN',
        'minute'           : 'MINUTE',
        'module'           : 'MODULE',
        'month'            : 'MONTH',
        'names'            : 'NAMES',
        'national'         : 'NATIONAL',
        'natural'          : 'NATURAL',
        'nchar'            : 'NCHAR',
        'next'             : 'NEXT',
        'no'               : 'NO',
        'not'              : 'NOT',
        'null'             : 'NULL',
        'nullif'           : 'NULLIF',
        'numeric'          : 'NUMERIC',
        'octet_length'     : 'OCTET_LENGTH',
        'of'               : 'OF',
        'on'               : 'ON',
        'only'             : 'ONLY',
        'open'             : 'OPEN',
        'option'           : 'OPTION',
        'or'               : 'OR',
        'order'            : 'ORDER',
        'outer'            : 'OUTER',
        'output'           : 'OUTPUT',
        'overlaps'         : 'OVERLAPS',
        'pad'              : 'PAD',
        'partial'          : 'PARTIAL',
        'position'         : 'POSITION',
        'precision'        : 'PRECISION',
        'prepare'          : 'PREPARE',
        'preserve'         : 'PRESERVE',
        'primary'          : 'PRIMARY',
        'prior'            : 'PRIOR',
        'privileges'       : 'PRIVILEGES',
        'procedure'        : 'PROCEDURE',
        'public'           : 'PUBLIC',
        'read'             : 'READ',
        'real'             : 'REAL',
        'references'       : 'REFERENCES',
        'relative'         : 'RELATIVE',
        'restrict'         : 'RESTRICT',
        'revoke'           : 'REVOKE',
        'right'            : 'RIGHT',
        'rollback'         : 'ROLLBACK',
        'rows'             : 'ROWS',
        'schema'           : 'SCHEMA',
        'scroll'           : 'SCROLL',
        'second'           : 'SECOND',
        'section'          : 'SECTION',
        'select'           : 'SELECT',
        'session'          : 'SESSION',
        'session_user'     : 'SESSION_USER',
        'set'              : 'SET',
        'size'             : 'SIZE',
        'smallint'         : 'SMALLINT',
        'some'             : 'SOME',
        'space'            : 'SPACE',
        'sql'              : 'SQL',
        'sqlcode'          : 'SQLCODE',
        'sqlerror'         : 'SQLERROR',
        'sqlstate'         : 'SQLSTATE',
        'substring'        : 'SUBSTRING',
        'sum'              : 'SUM',
        'system_user'      : 'SYSTEM_USER',
        'table'            : 'TABLE',
        'temporary'        : 'TEMPORARY',
        'then'             : 'THEN',
        'time'             : 'TIME',
        'timestamp'        : 'TIMESTAMP',
        'timezone_hour'    : 'TIMEZONE_HOUR',
        'timezone_minute'  : 'TIMEZONE_MINUTE',
        'to'               : 'TO',
        'top'              : 'TOP',
        'trailing'         : 'TRAILING',
        'transaction'      : 'TRANSACTION',
        'translate'        : 'TRANSLATE',
        'translation'      : 'TRANSLATION',
        'trim'             : 'TRIM',
        'true'             : 'TRUE',
        'union'            : 'UNION',
        'unique'           : 'UNIQUE',
        'unknown'          : 'UNKNOWN',
        'update'           : 'UPDATE',
        'upper'            : 'UPPER',
        'usage'            : 'USAGE',
        'user'             : 'USER',
        'using'            : 'USING',
        'value'            : 'VALUE',
        'values'           : 'VALUES',
        'varchar'          : 'VARCHAR',
        'varying'          : 'VARYING',
        'view'             : 'VIEW',
        'when'             : 'WHEN',
        'whenever'         : 'WHENEVER',
        'where'            : 'WHERE',
        'with'             : 'WITH',
        'work'             : 'WORK',
        'write'            : 'WRITE',
        'year'             : 'YEAR',
        'zone'             : 'ZONE',
    }

    tokens = ['NUMBER',
              'ID',         'COLON',
              'STRING',     'PERIOD',
              'COMMA',      'SEMI',
              'PLUS',       'MINUS',
              'TIMES',      'DIVIDE',
              'LPAREN',     'RPAREN',
              'GT',         'GE',
              'LT',         'LE',
              'EQ',         'NE',
              'LBRACKET',   'RBRACKET'
              ] + list(reserved.values())

    def t_NUMBER(self, t):
        # TODO: see http://docs.python.org/reference/lexical_analysis.html
        # for what Python accepts, then use eval
        r'\d+'
        t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9]*'
        t.type = SqlLexer.reserved.get(t.value.lower(),'ID')    # Check for reserved words
        # redis is case sensitive in hash keys but we want the sql to be case insensitive,
        # so we lowercase identifiers
        if t.type != 'ID':
            t.value = t.value.upper()
        return t

    def t_COMMENT(self, t):
        r'(/\*(.|\n)*?\*/)|(\-\-.*)'
        pass

    def t_STRING(self, t):
        # TODO: unicode...
        # Note: this regex is from pyparsing,
        # see http://stackoverflow.com/questions/2143235/how-to-write-a-regular-expression-to-match-a-string-literal-where-the-escape-is
        # TODO: may be better to refer to http://docs.python.org/reference/lexical_analysis.html
        '(?:"(?:[^"\\n\\r\\\\]|(?:"")|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*")|(?:\'(?:[^\'\\n\\r\\\\]|(?:\'\')|(?:\\\\x[0-9a-fA-F]+)|(?:\\\\.))*\')'
        t.value = eval(t.value)
        #t.value[1:-1]
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    t_ignore  = ' \t'

    #literals = ['+', '-', '*', '/', '>', '>=', '<', '<=', '=', '!=']
    # Regular expression rules for simple tokens
    t_COLON   = r'@'
    t_PERIOD  = r'\.'
    t_COMMA   = r'\,'
    t_SEMI    = r';'
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_GT      = r'>'
    t_GE      = r'>='
    t_LT      = r'<'
    t_LE      = r'<='
    t_EQ      = r'='
    t_NE      = r'!=|<>'

    def t_error(self, t):
        raise TypeError("Unknown text '%s'" % (t.value,))

    def build(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)
        return self.lexer

    def test(self):
        while True:
            text = raw_input("sql> ").strip()
            if text.lower() == "quit":
                break
            self.lexer.input(text)
            while True:
                tok = self.lexer.token()
                if not tok:
                    break
                print tok


# TODO: consider using a more formal AST representation
class Node(object):
    def __init__(self, name, children=None, sql=None):
        self.name = name
        if isinstance(children, tuple) or isinstance(children, list):
            self.children = children
        elif children:
            self.children = [children]
        else:
            self.children = []
        self.sql = sql

    def to_sql(self):
        return self.sql

    def set_indent(self, indent):
        if indent and self.sql.find('\n') > 0:
            sqls = []
            for sql in self.sql.split('\n'):
                if sqls:
                    sqls.append('\n%s%s' % (indent, sql))
                else:
                    sqls.append(sql)
            return ''.join(sqls)
        else:
            return self.sql


class SqlParser(object):

    tokens = SqlLexer.tokens

    def __init__(self):
        self.errors = []

    def p_query_specification(self, p):
        """
        query_specification : SELECT set_quantifier opt_top select_list table_expression
        """
        set_quantifier = ' ' + p[2].sql if p[2].sql else ''
        opt_top = p[3].sql
        if opt_top:
            set_quantifier += ' ' + opt_top
        sql_select_list = p[4].set_indent('     ')
        select_list = '\n       ' + sql_select_list if set_quantifier else sql_select_list
        sql = '%s%s %s %s' % (p[1],
                              set_quantifier,
                              select_list, p[5].sql)
        children = [p[2], p[4], p[5]]
        p[0] = Node('query_specification', children, sql)

    def p_set_quantifier(self, p):
        """
        set_quantifier : DISTINCT
                       | ALL
                       |
        """
        children = None
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('set_quantifier', children, sql)

    def p_opt_top(self, p):
        """
        opt_top : TOP NUMBER
                |
        """
        children = None
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_top', children, sql)

    def p_select_list(self, p):
        """
        select_list : TIMES
                    | select_sublist
                    | select_list COMMA select_sublist
        """
        if p[1] == '*':
            children = None
            sql = p[1]
        elif len(p) == 4:
            children = [p[1], p[3]]
            sql = '%s\n, %s' % (p[1].sql, p[3].sql)
        else:
            children = p[1]
            sql = p[1].sql
        p[0] = Node('select_list', children, sql)

    def p_select_sublist(self, p):
        """
        select_sublist : derived_column
                       | qualifier PERIOD TIMES
        """
        children = p[1]
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s.%s' % (p[1].sql, p[3])
        p[0] = Node('select_sublist', children, sql)

    def p_derived_column(self, p):
        """
        derived_column : value_expression as_clause
        """
        children = [p[1], p[2]]
        value_expression = p[1].sql
        as_clause = ' ' + p[2].sql if p[2].sql else ''
        sql = '%s%s' % (value_expression, as_clause)
        p[0] = Node('derived_column', children, sql)

    def p_value_expression(self, p):
        """
        value_expression : numeric_value_expression
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('value_expression', children, sql)

    def p_value_expression_repeat(self, p):
        """
        value_expression_repeat : value_expression
                                | value_expression_repeat COMMA value_expression
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('value_expression_repeat', children, sql)

    def p_numeric_value_expression(self, p):
        """
        numeric_value_expression : term
                                 | numeric_value_expression PLUS term
                                 | numeric_value_expression MINUS term
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('numeric_value_expression', children, sql)

    def p_term(self, p):
        """
        term : factor
             | term TIMES factor
             | term DIVIDE factor
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('term', children, sql)

    def p_factor(self, p):
        """
        factor : PLUS numeric_primary
               | MINUS numeric_primary
               | numeric_primary
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('factor', children, sql)

    def p_numeric_primary(self, p):
        """
        numeric_primary : value_expression_primary
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('numeric_primary', children, sql)

    def p_value_expression_primary(self, p):
        """
        value_expression_primary : unsigned_value_specification
                                 | column_reference
                                 | set_function_specification
                                 | scalar_subquery
                                 | case_expression
                                 | LPAREN value_expression RPAREN
                                 | cast_specification
        """
        if len(p) == 4:
            sql = '(%s)' % (p[2].sql,)
            children = p[2]
        else:
            children = p[1]
            sql = p[1].sql
        p[0] = Node('value_expression_primary', children, sql)

    def p_scalar_subquery(self, p):
        """
        scalar_subquery : subquery
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('scalar_subquery', children, sql)

    def p_subquery(self, p):
        """
        subquery : LPAREN query_expression RPAREN
        """
        children = p[2]
        sql_query_expression = p[2].set_indent('   ')
        sql = '(%s\n  )' % (sql_query_expression,)
        p[0] = Node('subquery', children, sql)

    def p_query_expression(self, p):
        """
        query_expression : non_join_query_expression
                         | joined_table
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('query_expression', children, sql)

    def p_non_join_query_expression(self, p):
        """
        non_join_query_expression : non_join_query_term
                                  | query_expression UNION ALL corresponding_spec query_term
                                  | query_expression UNION corresponding_spec query_term
                                  | query_expression EXCEPT ALL corresponding_spec query_term
                                  | query_expression EXCEPT corresponding_spec query_term
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        elif len(p) == 5:
            children = [p[1], p[3], p[4]]
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        else:
            children = [p[1], p[4], p[5]]
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5].sql)
        p[0] = Node('non_join_query_expression', children, sql)

    def p_non_join_query_term(self,p):
        """
        non_join_query_term : non_join_query_primary
                            | query_term INTERSECT ALL corresponding_spec query_primary
                            | query_term INTERSECT corresponding_spec query_primary
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        elif len(p) == 5:
            children = [p[1], p[3], p[4]]
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        else:
            children = [p[1], p[4], p[5]]
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5].sql)
        p[0] = Node('non_join_query_term', children, sql)

    def p_non_join_query_primary(self, p):
        """
        non_join_query_primary : simple_table
                               | LPAREN non_join_query_expression RPAREN
        """
        if len(p):
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('non_join_query_primary', children, sql)

    def p_simple_table(self, p):
        """
        simple_table : query_specification
                     | table_value_constructor
                     | explicit_table
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('simple_table', children, sql)

    def p_table_value_constructor(self, p):
        """
        table_value_constructor : VALUES table_value_constructor_list
        """
        children = p[2]
        sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('table_value_constructor', children, sql)

    def p_table_value_constructor_list(self, p):
        """
        table_value_constructor_list : row_value_constructor
                                     | table_value_constructor_list COMMA row_value_constructor
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('table_value_constructor_list', children, sql)

    def p_explicit_table(self, p):
        """
        explicit_table : TABLE table_name
        """
        children = p[2]
        sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('explicit_table', children, sql)

    def p_query_primary(self, p):
        """
        query_primary : non_join_query_primary
                      | joined_table
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('query_primary', children, sql)

    def p_corresponding_spec(self, p):
        """
        corresponding_spec : CORRESPONDING BY LPAREN corresponding_column_list RPAREN
                           | CORRESPONDING
        """
        if len(p) == 2:
            children = None
            sql = p[1]
        else:
            children = p[4]
            sql = '%s %s(%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('corresponding_spec', children, sql)

    def p_corresponding_column_list(self, p):
        """
        corresponding_column_list : column_name_list
        """
        children = p[1]
        sql = p[1]
        p[0] = Node('corresponding_column_list', children, sql)

    def p_query_term(self, p):
        """
        query_term : non_join_query_term
                   | joined_table
        """
        sql = p[1].sql
        p[0] = Node('query_term', None, sql)

    def p_cast_specification(self, p):
        """
        cast_specification : CAST LPAREN cast_operand AS cast_target RPAREN
        """
        children = [p[3], p[5]]
        sql = '%s(%s %s %s)' % (p[1], p[3].sql, p[4], p[5].sql)
        p[0] = Node('cast_specification', children, sql)

    def p_cast_operand(self, p):
        """
        cast_operand : value_expression
                     | NULL
        """
        if isinstance(p[1], Node):
            children = p[1]
            sql = p[1].sql
        else:
            children = None
            sql = p[1]
        p[0] = Node('cast_operand', children, sql)

    def p_cast_target(self, p):
        """
        cast_target : data_type
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('cast_target', children, sql)

    def p_data_type(self, p):
        """
        data_type : character_string_type
                  | national_character_string_type
                  | bit_string_type
                  | numeric_type
                  | datetime_type
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('data_type', children, sql)

    def p_character_string_type(self, p):
        """
        character_string_type : CHARACTER LPAREN NUMBER RPAREN
                              | CHARACTER
                              | CHAR LPAREN NUMBER RPAREN
                              | CHAR
                              | CHARACTER VARYING LPAREN NUMBER RPAREN
                              | CHARACTER VARYING
                              | CHAR VARYING LPAREN NUMBER RPAREN
                              | CHAR VARYING
                              | VARCHAR LPAREN NUMBER RPAREN
                              | VARCHAR
        """
        children = None
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2])
        elif len(p) == 5:
            sql = '%s(%s)' % (p[1], p[3])
        else:
            sql = '%s %s(%s)' % (p[1], p[2], p[4])
        p[0] = Node('character_string_type', children, sql)

    def p_national_character_string_type(self, p):
        """
        national_character_string_type : NATIONAL CHARACTER LPAREN NUMBER RPAREN
                                       | NATIONAL CHARACTER
                                       | NATIONAL CHAR LPAREN NUMBER RPAREN
                                       | NATIONAL CHAR
                                       | NCHAR LPAREN NUMBER RPAREN
                                       | NCHAR
                                       | NATIONAL CHARACTER VARYING LPAREN NUMBER RPAREN
                                       | NATIONAL CHARACTER VARYING
                                       | NATIONAL CHAR VARYING LPAREN NUMBER RPAREN
                                       | NATIONAL CHAR VARYING
                                       | NCHAR VARYING LPAREN NUMBER RPAREN
                                       | NCHAR VARYING
        """
        children = None
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2])
        elif len(p) == 4:
            sql = '%s %s %s' % (p[1], p[2], p[3])
        elif len(p) == 5:
            sql = '%s(%s)' % (p[1], p[3])
        elif len(p) == 6:
            sql = '%s %s(%s)' % (p[1], p[2], p[4])
        else:
            sql = '%s %s %s(%s)' % (p[1], p[2], p[3], p[5])
        p[0] = Node('national_character_string_type', children, sql)

    def p_bit_string_type(self, p):
        """
        bit_string_type : BIT LPAREN NUMBER RPAREN
                        | BIT
                        | BIT VARYING LPAREN NUMBER RPAREN
                        | BIT VARYING
        """
        children = None
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2])
        elif len(p) == 5:
            sql = '%s(%s)' % (p[1], p[3])
        else:
            sql = '%s %s(%s)' % (p[1], p[2], p[4])
        p[0] = Node('bit_string_type', children, sql)

    def p_numeric_type(self, p):
        """
        numeric_type : exact_numeric_type
                     | approximate_numeric_type
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('numeric_type', children, sql)

    def p_exact_numeric_type(self, p):
        """
        exact_numeric_type : NUMERIC LPAREN NUMBER COMMA NUMBER RPAREN
                           | DECIMAL LPAREN NUMBER COMMA NUMBER RPAREN
                           | DEC LPAREN NUMBER COMMA NUMBER RPAREN
                           | NUMERIC LPAREN NUMBER RPAREN
                           | DECIMAL LPAREN NUMBER RPAREN
                           | DEC LPAREN NUMBER RPAREN
                           | NUMERIC
                           | DECIMAL
                           | DEC
                           | INTEGER
                           | INT
                           | SMALLINT
        """
        children = None
        if len(p) == 7:
            sql = '%s(%s, %s)' % (p[1], p[3], p[5])
        elif len(p) == 5:
            sql = '%s(%s)' % (p[1], p[3])
        else:
            sql = p[1]
        p[0] = Node('exact_numeric_type', children, sql)

    def p_approximate_numeric_type(self, p):
        """
        approximate_numeric_type : FLOAT LPAREN NUMBER RPAREN
                                 | FLOAT
                                 | REAL
                                 | DOUBLE PRECISION
        """
        children = None
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2])
        else:
            sql = '%s(%s)' % (p[1], p[3])
        p[0] = Node('approximate_numeric_type', children, sql)

    def p_datetime_type(self, p):
        """
        datetime_type : DATE
                      | TIME LPAREN NUMBER RPAREN
                      | TIME
                      | TIMESTAMP
        """
        children = None
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '%s(%s)' % (p[1], p[3])
        p[0] = Node('datetime_type', children, sql)

    def p_case_expression(self, p):
        """
        case_expression : case_abbreviation
                        | case_specification
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('case_expression', children, sql)

    def p_case_abbreviation(self, p):
        """
        case_abbreviation : NULLIF LPAREN value_expression COMMA value_expression RPAREN
                          | COALESCE LPAREN value_expression_repeat RPAREN
        """
        if len(p) == 7:
            children = [p[3], p[5]]
            sql = '%s(%s, %s)' % (p[1], p[3].sql, p[5].sql)
        else:
            children = p[3]
            sql = '%s(%s)' % (p[1], p[3].sql)
        p[0] = Node('case_abbreviation', children, sql)

    def p_case_specification(self, p):
        """
        case_specification : simple_case
                           | searched_case
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('case_specification', children, sql)

    def p_simple_case(self, p):
        """
        simple_case : CASE case_operand simple_when_clause_repeat else_clause END
        """
        children = [p[2], p[3], p[4]]
        else_clause = '\n      ' + p[4].sql if p[4].sql else ''
        sql = '%s %s\n      %s %s\n  %s' % (p[1], p[2].sql, p[3].sql, else_clause, p[5])
        p[0] = Node('simple_case', children, sql)

    def p_case_operand(self, p):
        """
        case_operand : value_expression
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('case_operand', children, sql)

    def p_simple_when_clause_repeat(self, p):
        """
        simple_when_clause_repeat : simple_when_clause
                                  | simple_when_clause_repeat simple_when_clause
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[2]]
            sql = "%s\n      %s" % (p[1].sql, p[2].sql)
        p[0] = Node('simple_when_clause_repeat', children, sql)

    def p_simple_when_clause(self, p):
        """
        simple_when_clause : WHEN when_operand THEN result
        """
        children = [p[2], p[4]]
        sql = '%s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql)
        p[0] = Node('simple_when_clause', children, sql)

    def p_when_operand(self, p):
        """
        when_operand : value_expression
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('when_operand', children, sql)

    def p_result(self, p):
        """
        result : result_expression
               | NULL
        """
        if isinstance(p[1], Node):
            children = p[1]
            sql = p[1].sql
        else:
            children = None
            sql = p[1]
        p[0] = Node('result', children, sql)

    def p_result_expression(self, p):
        """
        result_expression : value_expression
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('result_expression', children, sql)

    def p_else_clause(self, p):
        """
        else_clause : ELSE result
                    |
        """
        if len(p) == 1:
            children = None
            sql = ''
        else:
            children = p[2]
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('else_clause', children, sql)

    def p_searched_case(self, p):
        """
        searched_case : CASE simple_when_clause_repeat else_clause END
        """
        children = [p[2], p[3]]
        else_clause = '\n      ' + p[3].sql if p[3].sql else ''
        sql = '%s\n      %s %s\n  %s' % (p[1], p[2].sql, else_clause, p[4])
        p[0] = Node('searched_case', children, sql)

    def p_unsigned_value_specification(self, p):
        """
        unsigned_value_specification : unsigned_literal
                                     | general_value_specification
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('unsigned_value_specification', children, sql)

    def p_column_reference(self, p):
        """
        column_reference : qualifier PERIOD column_name
                         | column_name
        """
        if len(p) == 2:
            children = None
            sql = p[1].sql
        else:
            children = p[1]
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        p[0] = Node('column_reference', children, sql)

    def p_set_function_specification(self, p):
        """
        set_function_specification : COUNT LPAREN TIMES RPAREN
                                   | general_set_function
        """
        if len(p) == 5:
            children = None
            sql = '%s(*)' % (p[1],)
        else:
            children = p[1]
            sql = p[1].sql
        p[0] = Node('set_function_specification', children, sql)

    def p_general_set_function(self, p):
        """
        general_set_function : AVG LPAREN set_quantifier value_expression RPAREN
                             | MAX LPAREN set_quantifier value_expression RPAREN
                             | MIN LPAREN set_quantifier value_expression RPAREN
                             | SUM LPAREN set_quantifier value_expression RPAREN
                             | COUNT LPAREN set_quantifier value_expression RPAREN
        """
        children = [p[3], p[4]]
        set_quantifier = p[3].sql + ' ' if p[3].sql else ''
        sql = '%s(%s%s)' % (p[1], set_quantifier, p[4].sql)
        p[0] = Node('general_set_function', children, sql)

    def p_qualifier(self, p):
        """
        qualifier : ID
        """
        children = None
        sql = p[1]
        p[0] = Node('qualifier', children, sql)

    def p_unsigned_literal(self, p):
        """
        unsigned_literal : unsigned_numeric_literal
                         | general_literal
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('unsigned_literal', children, sql)

    def p_general_value_specification(self, p):
        """
        general_value_specification : parameter_specification
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('general_value_specification', children, sql)

    def p_parameter_specification(self, p):
        """
        parameter_specification : COLON ID
        """
        children = None
        sql = '%s%s' % (p[1], p[2])
        p[0] = Node('parameter_specification', children, sql)

    def p_unsigned_numeric_literal(self, p):
        """
        unsigned_numeric_literal : exact_numeric_literal
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('unsigned_numeric_literal', children, sql)

    def p_exact_numeric_literal(self, p):
        """
        exact_numeric_literal : unsigned_integer_with_period_option
                              | PERIOD NUMBER
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = None
            sql = '%s%s' % (p[1], p[2])
        p[0] = Node('exact_numeric_literal', children, sql)

    def p_unsigned_integer_with_period_option(self, p):
        """
        unsigned_integer_with_period_option : NUMBER
                                            | NUMBER PERIOD
                                            | NUMBER PERIOD NUMBER
        """
        children = None
        if len(p) == 2:
            sql = str(p[1])
        elif len(p) == 3:
            sql = '%s.' % (p[1],)
        else:
            sql = '%s.%s' % (p[1], p[3])
        p[0] = Node('unsigned_integer_with_period_option', children, sql)

    def p_general_literal(self, p):
        """
        general_literal : character_string_literal
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('general_literal', children, sql)

    def p_character_string_literal(self, p):
        """
        character_string_literal : STRING
        """
        children = None
        sql = "'%s'" % (p[1],)
        p[0] = Node('character_string_literal', children, sql)

    def p_as_clause(self, p):
        """
        as_clause : AS ID
                  | ID
                  |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1]
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('as_clause', None, sql)

    def p_table_expression(self, p):
        """
        table_expression : from_clause where_clause group_by_clause having_clause
        """
        children = [p[1], p[2], p[3], p[4]]
        sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3].sql, p[4].sql)
        p[0] = Node('table_expression', children, sql)

    def p_from_clause(self, p):
        """
        from_clause : FROM table_reference_repeat
        """
        children = p[2]
        sql = '\n  %s %s' % (p[1], p[2].sql)
        p[0] = Node('from_clause', children, sql)

    def p_where_clause(self, p):
        """
        where_clause : WHERE search_condition
                     |
        """
        if len(p) == 1:
            sql = ''
            children = None
        else:
            children = p[2]
            sql = '\n %s %s' % (p[1], p[2].sql)
        p[0] = Node('where_clause', children, sql)

    def p_group_by_clause(self, p):
        """
        group_by_clause : GROUP BY grouping_column_reference_list
                        |
        """
        if len(p) == 1:
            children = None
            sql = ''
        else:
            children = p[3]
            sql = '\n %s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('group_by_clause', children, sql)

    def p_having_clause(self, p):
        """
        having_clause : HAVING search_condition
                      |
        """
        if len(p) == 1:
            children = None
            sql = ''
        else:
            children = p[2]
            sql = '\n%s %s' % (p[1], p[2].sql)
        p[0] = Node('having_clause', children, sql)

    def p_grouping_column_reference_list(self, p):
        """
        grouping_column_reference_list : grouping_column_reference
                                       | grouping_column_reference_list COMMA grouping_column_reference
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('grouping_column_reference_list', children, sql)

    def p_grouping_column_reference(self, p):
        """
        grouping_column_reference : column_reference collate_clause
                                  | column_reference
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[2]]
            sql = '%s  %s' % (p[1].sql, p[2].sql)
        p[0] = Node('grouping_column_reference', children, sql)

    def p_collate_clause(self, p):
        """
        collate_clause : COLLATE collation_name
        """
        children = p[2]
        sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('collate_clause', children, sql)

    def p_collation_name(self, p):
        """
        collation_name : qualified_name
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('collation_name', children, sql)

    def p_table_reference_repeat(self, p):
        """
        table_reference_repeat : table_reference
                               | table_reference_repeat COMMA table_reference
        """
        if len(p) == 2:
            sql = p[1].sql
            children = p[1]
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('table_reference_repeat', children, sql)

    def p_table_reference(self, p):
        """
        table_reference : table_name correlation_specification
                        | derived_table correlation_specification
                        | table_name
                        | joined_table
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[2]]
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('table_reference', children, sql)

    def p_joined_table(self, p):
        """
        joined_table : cross_join
                     | qualified_join
                     | LPAREN joined_table RPAREN
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('joined_table', children, sql)

    def p_cross_join(self, p):
        """
        cross_join : table_reference CROSS JOIN table_reference
        """
        children = [p[1], p[4]]
        sql = '%s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql)
        p[0] = Node('cross_join', children, sql)

    def p_qualified_join(self, p):
        """
        qualified_join : table_reference join_type JOIN table_reference join_specification
        """
        children = [p[1], p[2], p[4], p[5]]
        sql = '%s %s %s %s %s' % (p[1].sql, p[2].sql, p[3], p[4].sql, p[5].sql)
        p[0] = Node('qualified_join', children, sql)

    def p_join_type(self, p):
        """
        join_type : INNER
                  | outer_join_type OUTER
                  | outer_join_type
                  | UNION
                  |
        """
        children = None
        if len(p) == 1:
            sql = '\n '
        elif len(p) == 2:
            if isinstance(p[1], Node):
                sql = p[1].sql
                children = p[1]
            else:
                sql = '\n ' + p[1]
        else:
            children = p[1]
            sql = '%s %s' % (p[1].sql, p[2])
        p[0] = Node('join_type', children, sql)

    def p_outer_join_type(self, p):
        """
        outer_join_type : LEFT
                        | RIGHT
                        | FULL
        """
        sql = '\n' + ' ' * (6 - len(p[1])) + p[1]
        p[0] = Node('outer_join_type', None, sql)

    def p_join_specification(self, p):
        """
        join_specification : join_condition
                           | named_columns_join
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('join_specification', children, sql)

    def p_join_condition(self, p):
        """
        join_condition : ON search_condition
        """
        children = p[2]
        sql = '%s %s' % (p[1], p[2].sql,)
        p[0] = Node('join_condition', children, sql)

    def p_named_columns_join(self, p):
        """
        named_columns_join : USING LPAREN join_column_list RPAREN
        """
        children = p[3]
        sql = '%s(%s)' % (p[1], p[3].sql)
        p[0] = Node('named_columns_join', children, sql)

    def p_join_column_list(self, p):
        """
        join_column_list : column_name_list
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('join_column_list', children, sql)

    def p_search_condition(self, p):
        """
        search_condition : boolean_term
                         | search_condition OR boolean_term
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s\n    %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('search_condition', children, sql)

    def p_boolean_term(self, p):
        """
        boolean_term : boolean_factor
                     | boolean_term AND boolean_factor
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s\n   %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('boolean_term', children, sql)

    def p_boolean_factor(self, p):
        """
        boolean_factor : NOT boolean_test
                       | boolean_test
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('boolean_factor', children, sql)

    def p_boolean_test(self, p):
        """
        boolean_test : boolean_primary
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('boolean_test', children, sql)

    def p_boolean_primary(self, p):
        """
        boolean_primary : predicate
                        | LPAREN search_condition RPAREN
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('boolean_primary', children, sql)

    def p_predicate(self, p):
        """
        predicate : comparison_predicate
                  | between_predicate
                  | in_predicate
                  | like_predicate
                  | null_predicate
                  | quantified_comparison_predicate
                  | exists_predicate
                  | match_predicate
                  | overlaps_predicate
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('predicate', children, sql)

    def p_comparison_predicate(self, p):
        """
        comparison_predicate : row_value_constructor comp_op row_value_constructor
        """
        children = [p[1], p[2], p[3]]
        sql_right = p[3].set_indent(' ' * (len(p[1].sql) + 8))
        sql = '%s %s %s' % (p[1].sql, p[2].sql, sql_right)
        p[0] = Node('comparison_predicate', children, sql)

    def p_between_predicate(self, p):
        """
        between_predicate : row_value_constructor opt_not BETWEEN row_value_constructor AND row_value_constructor
        """
        children = [p[1], p[2], p[4], p[6]]
        sql = '%s %s %s %s %s %s' % (p[1].sql, p[2].sql, p[3], p[4].sql, p[5], p[6].sql)
        p[0] = Node('between_predicate', children, sql)

    def p_in_predicate(self, p):
        """
        in_predicate : row_value_constructor opt_not IN in_predicate_value
        """
        children = [p[1], p[2], p[4]]
        sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3], p[4].sql)
        p[0] = Node('row_value_constructor', children, sql)

    def p_like_predicate(self, p):
        """
        like_predicate : match_value opt_not LIKE pattern ESCAPE escape_character
                       | match_value opt_not LIKE pattern
        """
        if len(p) == 5:
            children = [p[1], p[2], p[4]]
            sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3], p[4].sql)
        else:
            children = [p[1], p[2], p[4], p[6]]
            sql = '%s %s %s %s %s %s' % (p[1].sql, p[2].sql, p[3], p[4].sql, p[5], p[6].sql)
        p[0] = Node('like_predicate', children, sql)

    def p_null_predicate(self, p):
        """
        null_predicate : IS NOT NULL
                       | IS NULL
        """
        if len(p) == 4:
            sql = '%s %s %s' % (p[1], p[2], p[3])
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('null_predicate', None, sql)

    def p_quantified_comparison_predicate(self, p):
        """
        quantified_comparison_predicate : row_value_constructor comp_op quantifier table_subquery
        """
        children = [p[1], p[2], p[3], p[4]]
        sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3].sql, p[4].sql)
        p[0] = Node('quantified_comparison_predicate', children, sql)

    def p_exists_predicate(self, p):
        """
        exists_predicate : EXISTS table_subquery
        """
        children = p[2]
        sql_table_subquery = p[2].set_indent(' ' * 12)
        sql = '%s %s' % (p[1], sql_table_subquery)
        p[0] = Node('exists_predicate', children, sql)

    def p_match_predicate(self, p):
        """
        match_predicate : row_value_constructor MATCH opt_unique PARTIAL table_subquery
                        | row_value_constructor MATCH opt_unique FULL table_subquery
                        | row_value_constructor MATCH opt_unique table_subquery
        """
        if len(p) == 5:
            children = [p[1], p[3], p[4]]
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        else:
            children = [p[1], p[3], p[5]]
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4], p[5].sql)
        p[0] = Node('match_predicate', children, sql)

    def p_overlaps_predicate(self, p):
        """
        overlaps_predicate : row_value_constructor OVERLAPS row_value_constructor
        """
        children = [p[1], p[3]]
        sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('overlaps_predicate', children, sql)

    def p_opt_unique(self, p):
        """
        opt_unique : UNIQUE
                   |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_unique', None, sql)

    def p_quantifier(self, p):
        """
        quantifier : ALL
                   | SOME
                   | ANY
        """
        sql = p[1]
        p[0] = Node('match_value', None, sql)

    def p_match_value(self, p):
        """
        match_value : value_expression_primary
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('match_value', children, sql)

    def p_pattern(self, p):
        """
        pattern : value_expression_primary
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('pattern', children, sql)

    def p_escape_character(self, p):
        """
        escape_character : value_expression_primary
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('escape_character', children, sql)

    def p_opt_not(self, p):
        """
        opt_not : NOT
                |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_not', None, sql)

    def p_in_predicate_value(self, p):
        """
        in_predicate_value : table_subquery
                           | LPAREN in_value_list RPAREN
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('in_predicate_value', children, sql)

    def p_table_subquery(self, p):
        """
        table_subquery : subquery
        """
        sql = p[1].sql
        p[0] = Node('table_subquery', None, sql)

    def p_in_value_list(self, p):
        """
        in_value_list : value_expression
                      | in_value_list COMMA value_expression
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('in_predicate_value', children, sql)

    def p_comp_op(self, p):
        """
        comp_op : EQ
                | NE
                | LT
                | GT
                | LE
                | GE
        """
        sql = p[1]
        p[0] = Node('comp_op', None, sql)

    def p_row_value_constructor(self, p):
        """
        row_value_constructor : row_value_constructor_element
                              | LPAREN row_value_constructor_list RPAREN
                              | row_subquery
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('row_value_constructor', children, sql)

    def p_row_subquery(self, p):
        """
        row_subquery : subquery
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('row_subquery', children, sql)

    def p_row_value_constructor_list(self, p):
        """
        row_value_constructor_list : row_value_constructor_element
                                   | row_value_constructor_list COMMA row_value_constructor_element
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('row_value_constructor_list', children, sql)

    def p_row_value_constructor_element(self, p):
        """
        row_value_constructor_element : value_expression
                                      | null_specification
                                      | default_specification
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('row_value_constructor_element', children, sql)

    def p_null_specification(self, p):
        """
        null_specification : NULL
        """
        sql = p[1]
        p[0] = Node('null_specification', None, sql)

    def p_default_specification(self, p):
        """
        default_specification : DEFAULT
        """
        sql = p[1]
        p[0] = Node('default_specification', None, sql)

    def p_derived_table(self, p):
        """
        derived_table : subquery
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('derived_table', children, sql)

    def p_table_name(self, p):
        """
        table_name : LBRACKET qualified_name RBRACKET
                   | qualified_name
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = p[2]
            sql = '[%s]' % (p[2].sql,)
        p[0] = Node('table_name', children, sql)

    def p_qualified_name(self, p):
        """
        qualified_name : qualified_identifier
        """
        children = p[1]
        sql = p[1].sql
        p[0] = Node('qualified_name', children, sql)

    def p_qualified_identifier(self, p):
        """
        qualified_identifier : ID
        """
        sql = p[1]
        p[0] = Node('qualified_identifier', None, sql)

    def p_correlation_specification(self, p):
        """
        correlation_specification : AS correlation_name LPAREN derived_column_list RPAREN
                                  | correlation_name LPAREN derived_column_list RPAREN
                                  | AS correlation_name
                                  | correlation_name
        """
        if len(p) == 6:
            children = [p[2], p[4]]
            sql = '%s %s(%s)' % (p[1], p[2].sql, p[4].sql)
        elif len(p) == 5:
            children = [p[1], p[3]]
            sql = '%s(%s)' % (p[1].sql, p[3].sql)
        elif len(p) == 3:
            children = p[2]
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            children = p[1]
            sql = p[1].sql
        p[0] = Node('correlation_specification', children, sql)

    def p_correlation_name(self, p):
        """
        correlation_name : ID
        """
        sql = p[1]
        p[0] = Node('correlation_name', None, sql)

    def p_derived_column_list(self, p):
        """
        derived_column_list : column_name_list
        """
        children = p[1]
        sql = p[1]
        p[0] = Node('derived_column_list', children, sql)

    def p_column_name_list(self, p):
        """
        column_name_list : column_name
                         | column_name_list COMMA column_name
        """
        if len(p) == 2:
            children = p[1]
            sql = p[1].sql
        else:
            children = [p[1], p[3]]
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('column_name_list', children, sql)

    def p_column_name(self, p):
        """
        column_name : LBRACKET ID RBRACKET
                    | ID
        """
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '[%s]' % (p[2],)
        p[0] = Node('column_name', None, sql)

    def p_error(self, p):
        message = u"Error: '%s' 付近に不適切な構文があります。! %d 行, %d 列!" % (p.value, p.lineno, p.lexpos)
        self.errors.append(message)

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser

    def test(self):
        lexer = SqlLexer().build()
        print "=========================================="
        print self.parser.parse("Select distinct * from a WHere a1=b1 AND"
                                " (a2=b2 or a3=c3) and a4=b4", lexer=lexer).to_sql()
        print "=========================================="
        print self.parser.parse("select 1 a,'Abc123' as b,c,(1+2*3/4) d,"
                                "(select distinct count(*), sub_col1, (select sub_sub_col1, sub_sub_col2 "
                                "from sub_sub_table where sub_sub_col1=sub_sub_col2 and d=c) As sub_col2 "
                                "from sub_table where sub_col1=sub_col2 and c1=c2 and "
                                "exists(select 1 from b where b1=b2 and c!=3 and b<>4)) sub_sel,"
                                "case a when '1' then a1 when '2' then a2 when '3' then a3 end b,"
                                "case  when '1' then a1 when '2' then a2 else a9 end as ax "
                                "from a WHere a1=b1 AND (a2=b2 or a3=c3) "
                                "and a4=(select max(a) from b where b=c and a=b and "
                                "exists(select 1 from b where b1=b2 and c!=3 and b<>4)) "
                                "and exists(select 1 from b where b1=b2 and c!=3 and b<>4)", lexer=lexer).to_sql()
        print "=========================================="
        print self.parser.parse("select a, cast(123 as char) as b1  -- comment\n"
                                ", cast(123 as character) as b2"
                                ", cast(123 as character(10)) as b3"
                                ", cast(123 as char(20)) as b4"
                                ", cast(123 as character varying) as b5"
                                ", cast(123 as character varying (100)) as b6"
                                ", cast(123 as char varying) as b7"
                                ", cast(123 as char varying   (10)) as b7"
                                ", cast(123 as varchar(10)) as b8"
                                ", cast(123 as varchar) as b9"
                                ", cast(123 as national character(10)) as c1"
                                ", cast(123 as national character) as c2"
                                ", cast(123 as national char(10)) as c3"
                                ", cast(123 as national char) as c4"
                                ", cast(123 as nchar(10)) as c5"
                                ", cast(123 as nchar) as c6"
                                ", cast(123 as national character varying (10)) as c7"
                                ", cast(123		 as national character varying) as c8"
                                ", cast(123 as	 national char varying (10)) as c9"
                                ", cast(123 \nas national char varying) as c10"
                                ", cast(123 as nchar varying(10)) as c11"
                                ", cast(123 as nchar varying   ) as c12"
                                ", cast(123 as bit) as d1"
                                ", cast(123 as bit(0)) as d2"
                                ", cast(123 as bit varying) as d3"
                                ", cast(123 as bit varying(10)) as d4"
                                ", cast('123' as numeric(4,1)) as e1"
                                ", cast('123' as decimal(4,1)) as e2"
                                ", cast('123' as dec(4,1)) as e3"
                                ", cast('123' as numeric(5)) as e4"
                                ", cast('123' as decimal(5)) as e5"
                                ", cast('123' as dec(5)) as e6"
                                ", cast('123' as numeric) as e7"
                                ", cast('123' as decimal) as e8"
                                ", cast('123' as dec) as e9"
                                ", cast('123' as integer) as e10"
                                ", cast('123' as int) as e11"
                                ", cast('123' as smallint) as e12"
                                ", cast('123' as float (5)) as f1"
                                ", cast('123' as float) as f2"
                                ", cast('123' as real) as f3"
                                ", cast('123' as double precision) as f4"
                                ", cast('2016-07-15 10:32:01' as time (5)) as g1"
                                ", cast('2016-07-15 10:32:01' as date) as g2"
                                ", cast('2016-07-15 10:32:01' as time) as g3"
                                ", cast('2016-07-15 10:32:01' as timestamp) as g4"
                                "		 from          tbl as a "
                                "left outer join tbl2 b on a.col1 = b.col1 and a.col2=b.col2 right"
                                " join tbl3 c on a.col1=c.col1 and a.col2=c.col2 "
                                " inner join tbl4 as d on a.col1=d.col1 and a.col2=d.cols2 "
                                "join tbl5 e on a.col1=e.col1 and a.col2=e.col2", lexer=lexer).to_sql()
        # while True:
        #     text = raw_input("sql> ").strip()
        #     if text.lower() == "quit":
        #         break
        #     if text:
        #         result = self.parser.parse(text, lexer=lexer)
        #         #print "parse result -> %s" % result
        #         if result:
        #             print result.to_sql()


def unittest_lexer():
    l = SqlLexer()
    l.build()
    l.test()


def unittest_parser():
    p = SqlParser()
    p.build()
    p.test()

if __name__ == "__main__":
    #unittest_lexer()
    unittest_parser()
