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
import common
from ply import lex, yacc


class SqlLexer(object):

    reserved = {
        'ada'                          : 'ADA',
        'add'                          : 'ADD',
        'admin_l'                      : 'ADMIN_L',
        'after'                        : 'AFTER',
        'aggregate'                    : 'AGGREGATE',
        'all'                          : 'ALL',
        'alter'                        : 'ALTER',
        'ammsc'                        : 'AMMSC',
        'and'                          : 'AND',
        'any'                          : 'ANY',
        'approxnum'                    : 'APPROXNUM',
        'are'                          : 'ARE',
        'array'                        : 'ARRAY',
        'as'                           : 'AS',
        'asc'                          : 'ASC',
        'assembly_l'                   : 'ASSEMBLY_L',
        'attach'                       : 'ATTACH',
        'attribute'                    : 'ATTRIBUTE',
        'autoregister_l'               : 'AUTOREGISTER_L',
        'avg'                          : 'AVG',
        'backup'                       : 'BACKUP',
        'before'                       : 'BEFORE',
        'begin'                        : 'BEGIN',
        'begin_fn_x'                   : 'BEGIN_FN_X',
        'begin_u_x'                    : 'BEGIN_U_X',
        'between'                      : 'BETWEEN',
        'binary'                       : 'BINARY',
        'binarynum'                    : 'BINARYNUM',
        'by'                           : 'BY',
        'call'                         : 'CALL',
        'called'                       : 'CALLED',
        'cascade'                      : 'CASCADE',
        'case'                         : 'CASE',
        'cast'                         : 'CAST',
        'char'                         : 'CHAR',
        'character'                    : 'CHARACTER',
        'check'                        : 'CHECK',
        'checked'                      : 'CHECKED',
        'checkpoint'                   : 'CHECKPOINT',
        'close'                        : 'CLOSE',
        'clr'                          : 'CLR',
        'clustered'                    : 'CLUSTERED',
        'coalesce'                     : 'COALESCE',
        'cobol'                        : 'COBOL',
        'collate'                      : 'COLLATE',
        'column'                       : 'COLUMN',
        'commit'                       : 'COMMIT',
        'constraint'                   : 'CONSTRAINT',
        'constructor'                  : 'CONSTRUCTOR',
        'contains'                     : 'CONTAINS',
        'convert'                      : 'CONVERT',
        'corresponding'                : 'CORRESPONDING',
        'count'                        : 'COUNT',
        'create'                       : 'CREATE',
        'cross'                        : 'CROSS',
        'cube'                         : 'CUBE',
        'current'                      : 'CURRENT',
        'current_date'                 : 'CURRENT_DATE',
        'current_time'                 : 'CURRENT_TIME',
        'current_timestamp'            : 'CURRENT_TIMESTAMP',
        'cursor'                       : 'CURSOR',
        'data'                         : 'DATA',
        'date'                         : 'DATE',
        'datetime'                     : 'DATETIME',
        'decimal'                      : 'DECIMAL',
        'declare'                      : 'DECLARE',
        'default'                      : 'DEFAULT',
        'delete'                       : 'DELETE',
        'desc'                         : 'DESC',
        'deterministic'                : 'DETERMINISTIC',
        'disconnect'                   : 'DISCONNECT',
        'distinct'                     : 'DISTINCT',
        'do'                           : 'DO',
        'double'                       : 'DOUBLE',
        'double_colon'                 : 'DOUBLE_COLON',
        'drop'                         : 'DROP',
        'dtd'                          : 'DTD',
        'dynamic'                      : 'DYNAMIC',
        'else'                         : 'ELSE',
        'encoding'                     : 'ENCODING',
        'end'                          : 'END',
        'escape'                       : 'ESCAPE',
        'except'                       : 'EXCEPT',
        'exclusive'                    : 'EXCLUSIVE',
        'execute'                      : 'EXECUTE',
        'exists'                       : 'EXISTS',
        'external'                     : 'EXTERNAL',
        'extract'                      : 'EXTRACT',
        'fetch'                        : 'FETCH',
        'final_l'                      : 'FINAL_L',
        'float'                        : 'FLOAT',
        'for'                          : 'FOR',
        'foreach'                      : 'FOREACH',
        'foreign'                      : 'FOREIGN',
        'fortran'                      : 'FORTRAN',
        'found'                        : 'FOUND',
        'from'                         : 'FROM',
        'full'                         : 'FULL',
        'function'                     : 'FUNCTION',
        'general'                      : 'GENERAL',
        'generated'                    : 'GENERATED',
        'go'                           : 'GO',
        'goto'                         : 'GOTO',
        'grant'                        : 'GRANT',
        'group'                        : 'GROUP',
        'grouping'                     : 'GROUPING',
        'hash'                         : 'HASH',
        'having'                       : 'HAVING',
        'htmlstr'                      : 'HTMLSTR',
        'identified'                   : 'IDENTIFIED',
        'identity'                     : 'IDENTITY',
        'if'                           : 'IF',
        'in'                           : 'IN',
        'increment_l'                  : 'INCREMENT_L',
        'index'                        : 'INDEX',
        'indicator'                    : 'INDICATOR',
        'inner'                        : 'INNER',
        'inout_l'                      : 'INOUT_L',
        'input'                        : 'INPUT',
        'insert'                       : 'INSERT',
        'instance_l'                   : 'INSTANCE_L',
        'instead'                      : 'INSTEAD',
        'int'                          : 'INT',
        'integer'                      : 'INTEGER',
        'internal'                     : 'INTERNAL',
        'intersect'                    : 'INTERSECT',
        'interval'                     : 'INTERVAL',
        'into'                         : 'INTO',
        'in_l'                         : 'IN_L',
        'is'                           : 'IS',
        'java'                         : 'JAVA',
        'join'                         : 'JOIN',
        'key'                          : 'KEY',
        'keyset'                       : 'KEYSET',
        'kwd_tag'                      : 'KWD_TAG',
        'language'                     : 'LANGUAGE',
        'left'                         : 'LEFT',
        'library_l'                    : 'LIBRARY_L',
        'like'                         : 'LIKE',
        'logx'                         : 'LOGX',
        'long'                         : 'LONG',
        'loop'                         : 'LOOP',
        'max'                          : 'MAX',
        'method'                       : 'METHOD',
        'min'                          : 'MIN',
        'modifies'                     : 'MODIFIES',
        'modify'                       : 'MODIFY',
        'module'                       : 'MODULE',
        'mssql_xmlcol_intnum'          : 'MSSQL_XMLCOL_INTNUM',
        'mssql_xmlcol_name'            : 'MSSQL_XMLCOL_NAME',
        'mssql_xmlcol_name1'           : 'MSSQL_XMLCOL_NAME1',
        'mssql_xmlcol_nameyz'          : 'MSSQL_XMLCOL_NAMEYZ',
        'mssql_xmlcol_namez'           : 'MSSQL_XMLCOL_NAMEZ',
        'mumps'                        : 'MUMPS',
        'name_l'                       : 'NAME_L',
        'natural'                      : 'NATURAL',
        'nchar'                        : 'NCHAR',
        'new'                          : 'NEW',
        'next'                         : 'NEXT',
        'no'                           : 'NO',
        'nonincremental'               : 'NONINCREMENTAL',
        'not'                          : 'NOT',
        'null'                         : 'NULL',
        'nullif'                       : 'NULLIF',
        'nullx'                        : 'NULLX',
        'numeric'                      : 'NUMERIC',
        'nvarchar'                     : 'NVARCHAR',
        'object_id'                    : 'OBJECT_ID',
        'of'                           : 'OF',
        'off'                          : 'OFF',
        'old'                          : 'OLD',
        'on'                           : 'ON',
        'open'                         : 'OPEN',
        'option'                       : 'OPTION',
        'or'                           : 'OR',
        'order'                        : 'ORDER',
        'outer'                        : 'OUTER',
        'out_l'                        : 'OUT_L',
        'over'                         : 'OVER',
        'overriding'                   : 'OVERRIDING',
        'parameter'                    : 'PARAMETER',
        'pascal_l'                     : 'PASCAL_L',
        'password'                     : 'PASSWORD',
        'permission_set'               : 'PERMISSION_SET',
        'persistent'                   : 'PERSISTENT',
        'pli'                          : 'PLI',
        'precision'                    : 'PRECISION',
        'prefetch'                     : 'PREFETCH',
        'primary'                      : 'PRIMARY',
        'privileges'                   : 'PRIVILEGES',
        'procedure'                    : 'PROCEDURE',
        'public'                       : 'PUBLIC',
        'purge'                        : 'PURGE',
        'reads'                        : 'READS',
        'real'                         : 'REAL',
        'ref'                          : 'REF',
        'references'                   : 'REFERENCES',
        'referencing'                  : 'REFERENCING',
        'remote'                       : 'REMOTE',
        'rename'                       : 'RENAME',
        'replacing'                    : 'REPLACING',
        'replication'                  : 'REPLICATION',
        'resignal'                     : 'RESIGNAL',
        'restrict'                     : 'RESTRICT',
        'return'                       : 'RETURN',
        'returns'                      : 'RETURNS',
        'revoke'                       : 'REVOKE',
        'rexecute'                     : 'REXECUTE',
        'right'                        : 'RIGHT',
        'role_l'                       : 'ROLE_L',
        'rollback'                     : 'ROLLBACK',
        'rollup'                       : 'ROLLUP',
        'row_number'                   : 'ROW_NUMBER',
        'safe_l'                       : 'SAFE_L',
        'schema'                       : 'SCHEMA',
        'select'                       : 'SELECT',
        'self_l'                       : 'SELF_L',
        'set'                          : 'SET',
        'shutdown'                     : 'SHUTDOWN',
        'smallint'                     : 'SMALLINT',
        'snapshot'                     : 'SNAPSHOT',
        'soft'                         : 'SOFT',
        'some'                         : 'SOME',
        'source'                       : 'SOURCE',
        'specific'                     : 'SPECIFIC',
        'sqlexception'                 : 'SQLEXCEPTION',
        'sqlstate'                     : 'SQLSTATE',
        'sqlwarning'                   : 'SQLWARNING',
        'sql_l'                        : 'SQL_L',
        'sql_tsi'                      : 'SQL_TSI',
        'start_l'                      : 'START_L',
        'static_l'                     : 'STATIC_L',
        'string_concat_operator'       : 'STRING_CONCAT_OPERATOR',
        'style'                        : 'STYLE',
        'sum'                          : 'SUM',
        'sync'                         : 'SYNC',
        'system'                       : 'SYSTEM',
        'table'                        : 'TABLE',
        'temporary'                    : 'TEMPORARY',
        'text_l'                       : 'TEXT_L',
        'then'                         : 'THEN',
        'ties'                         : 'TIES',
        'time'                         : 'TIME',
        'timestamp'                    : 'TIMESTAMP',
        'timestamp_func'               : 'TIMESTAMP_FUNC',
        'to'                           : 'TO',
        'top'                          : 'TOP',
        'trigger'                      : 'TRIGGER',
        'type'                         : 'TYPE',
        'under'                        : 'UNDER',
        'union'                        : 'UNION',
        'unique'                       : 'UNIQUE',
        'unrestricted'                 : 'UNRESTRICTED',
        'update'                       : 'UPDATE',
        'use'                          : 'USE',
        'user'                         : 'USER',
        'using'                        : 'USING',
        'value'                        : 'VALUE',
        'values'                       : 'VALUES',
        'varbinary'                    : 'VARBINARY',
        'varchar'                      : 'VARCHAR',
        'variable'                     : 'VARIABLE',
        'view'                         : 'VIEW',
        'when'                         : 'WHEN',
        'whenever'                     : 'WHENEVER',
        'where'                        : 'WHERE',
        'while'                        : 'WHILE',
        'with'                         : 'WITH',
        'work'                         : 'WORK',
        'wstring'                      : 'WSTRING',
        'xml'                          : 'XML',
        '__soap_dime_enc'              : '__SOAP_DIME_ENC',
        '__soap_doc'                   : '__SOAP_DOC',
        '__soap_docw'                  : '__SOAP_DOCW',
        '__soap_enc_mime'              : '__SOAP_ENC_MIME',
        '__soap_fault'                 : '__SOAP_FAULT',
        '__soap_header'                : '__SOAP_HEADER',
        '__soap_http'                  : '__SOAP_HTTP',
        '__soap_name'                  : '__SOAP_NAME',
        '__soap_type'                  : '__SOAP_TYPE',
        '__soap_xml_type'              : '__SOAP_XML_TYPE',
    }

    tokens = ['AT',
              'BITAND',
              'BITNOT',
              'BITOR',
              'COLON',
              'COMMA',
              'DIVIDE',
              'EQ',
              'GE',
              'GT',
              'ID',
              'LBRACKET',
              'LE',
              'LPAREN',
              'LT',
              'MINUS',
              'NE',
              'NUMBER',
              'PERIOD',
              'PLUS',
              'QUESTION',
              'RBRACKET',
              'RPAREN',
              'SEMI',
              'STRING',
              'TIMES',
             ] + list(reserved.values())

    t_ignore  = ' \t'

    #literals = ['+', '-', '*', '/', '>', '>=', '<', '<=', '=', '!=']
    # Regular expression rules for simple tokens
    t_COLON       = r':'
    t_AT          = r'@'
    t_BITAND      = r'\&'
    t_BITNOT      = r'\~'
    t_BITOR       = r'\|'
    t_QUESTION    = r'\?'
    t_PERIOD      = r'\.'
    t_COMMA       = r'\,'
    t_SEMI        = r'\;'
    t_PLUS        = r'\+'
    t_MINUS       = r'-'
    t_TIMES       = r'\*'
    t_DIVIDE      = r'/'
    t_LPAREN      = r'\('
    t_RPAREN      = r'\)'
    t_LBRACKET    = r'\['
    t_RBRACKET    = r'\]'
    t_GT         = r'>'
    t_GE         = r'>='
    t_LT         = r'<'
    t_LE         = r'<='
    t_EQ      = r'\='
    t_NE         = r'!=|<>'
    #t_COMPARISON  = r'(>=|<=|!=|<>|>|<|=)'

    def __init__(self):
        self.errors = []

    def t_NUMBER(self, t):
        # TODO: see http://docs.python.org/reference/lexical_analysis.html
        # for what Python accepts, then use eval
        r'0x[0-9A-Fa-f]+|\d+'
        #t.value = int(t.value)
        return t

    def t_ID(self, t):
        r'[a-zA-Z_][a-zA-Z_0-9$]*'
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
        #t.value = eval(t.value)
        #t.value[1:-1]
        return t

    # Define a rule so we can track line numbers
    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(self, t):
        # raise TypeError("Unknown text '%s'" % (t.value,))
        message = u"キーワード '%s' 付近に不適切な構文があります。" % (t.value,)
        self.errors.append(message)
        t.lexer.skip(1)

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
    def __init__(self, name, p, sql):
        self.name = name
        self.children = self.get_children(p)
        self.sql = sql

    def get_children(self, p):
        if not p:
            return []
        if len(p) == 1:
            return []
        else:
            return [i for i in p[1:] if isinstance(i, Node)]

    def to_sql(self):
        name_list = self.get_children_name()
        # print ', '.join(list(set(name_list)))
        return self.sql

    def get_children_name(self):
        name_list = []
        name_list.append(self.name)
        for child in self.children:
            name_list.extend(child.get_children_name())
        return name_list

    def set_list_break(self, name):
        if len(self.children) <= 1:
            return self.sql
        else:
            return self.set_sub_list_break(name)

    def set_sub_list_break(self, name):
        sqls = []
        if self.name == name:
            return self.sql

        for child in self.children:
            sql = child.set_sub_list_break(name)
            if sql:
                sqls.append(sql)
        return '\n, '.join(sqls)


class SqlParser(object):

    tokens = SqlLexer.tokens

    def __init__(self):
        self.errors = []

    def p_sql_list(self, p):
        """
        sql_list : sql_list1
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s;' % (p[1].sql,)
        p[0] = Node('sql_list', p, sql)

    def p_sql_list1(self, p):
        """
        sql_list1 : sql
                  | sql_list1 SEMI
                  | sql_list1 SEMI sql
                  | sql_list1 go_statement
                  | sql_list1 go_statement sql_list1
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 3:
            if isinstance(p[2], Node):
                sql = '%s\n\n%s' % (p[1].sql, p[2].sql)
            else:
                sql = '%s;' % (p[1].sql,)
        else:
            if isinstance(p[2], Node):
                sql = '%s\n%s\n%s' % (p[1].sql, p[2].sql, p[3].sql)
            else:
                sql = '%s;\n\n%s' % (p[1].sql, p[3].sql)
        p[0] = Node('sql_list1', p, sql)

    def p_go_statement(self, p):
        """
        go_statement : GO NUMBER
                     | GO
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list) + '\n'
        p[0] = Node('go_statement', p, sql)

    def p_sql(self, p):
        """
        sql : schema_element_list
            | view_def
            | xml_view
            | create_xml_schema
            | alter_constraint
            | create_library
            | create_assembly
            | drop_library
            | drop_assembly
            | manipulative_statement
            | user_aggregate_declaration
            | routine_declaration
            | module_declaration
            | method_declaration
            | trigger_def
            | drop_trigger
            | drop_proc
        """
        sql = p[1].sql
        p[0] = Node('sql', p, sql)

    def p_schema_element_list(self, p):
        """
        schema_element_list : schema_element
                            | add_column
                            | schema_element_list schema_element
                            | schema_element_list add_column
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('schema_element_list', p, sql)

    def p_schema_element(self, p):
        """
        schema_element : base_table_def
                       | create_index_def
                       | drop_table
                       | drop_index
                       | table_rename
                       | privilege_def
                       | privilege_revoke
                       | create_user_statement
                       | delete_user_statement
                       | set_pass
                       | set_group_stmt
                       | add_group_stmt
                       | delete_group_stmt
                       | user_defined_type
                       | user_defined_type_drop
                       | user_defined_type_alter
        """
        sql = p[1].sql
        p[0] = Node('schema_element', p, sql)

    def p_base_table_def(self, p):
        """
        base_table_def : CREATE TABLE new_table_name LPAREN base_table_element_commalist RPAREN
        """
        sql = '%s %s %s\n(\n%s\n)' % (p[1], p[2], p[3].sql, p[5].sql)
        p[0] = Node('base_table_def', p, sql)

    def p_base_table_element_commalist(self, p):
        """
        base_table_element_commalist : base_table_element
                                     | base_table_element_commalist COMMA base_table_element
        """
        if len(p) == 2:
            sql = '    %s' % (p[1].sql,)
        else:
            sql = '%s,\n    %s' % (p[1].sql, p[3].sql)
        p[0] = Node('base_table_element_commalist', p, sql)

    def p_base_table_element(self, p):
        """
        base_table_element : column_def
                           | table_constraint_def
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('base_table_element', p, sql)

    def p_column_def(self, p):
        """
        column_def : column column_data_type column_def_opt_list
        """
        sql = '%s %s%s' % (p[1].sql, p[2].sql, ' ' + p[3].sql if p[3].sql else '')
        p[0] = Node('column_def', p, sql)

    def p_opt_referential_triggered_action(self, p):
        """
        opt_referential_triggered_action : referential_rule
                                         | referential_rule referential_rule
                                         |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('opt_referential_triggered_action', p, sql)

    def p_referential_rule(self, p):
        """
        referential_rule : ON UPDATE referential_action
                         | delete_referential_rule
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('referential_rule', p, sql)

    def p_delete_referential_rule(self, p):
        """
        delete_referential_rule : ON DELETE referential_action
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('delete_referential_rule', p, sql)

    def p_opt_on_delete_referential_rule(self, p):
        """
        opt_on_delete_referential_rule : 
                                       | delete_referential_rule
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_on_delete_referential_rule', p, sql)

    def p_referential_action(self, p):
        """
        referential_action : CASCADE
                           | SET NULLX
                           | SET DEFAULT
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('referential_action', p, sql)

    def p_references(self, p):
        """
        references : REFERENCES q_table_name opt_column_commalist opt_referential_triggered_action
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('references', p, sql)

    def p_column_def_opt_list(self, p):
        """
        column_def_opt_list : column_def_opt_list column_def_opt
                            |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('column_def_opt_list', p, sql)

    def p_identity_opt(self, p):
        """
        identity_opt : START_L WITH signed_literal
                     | INCREMENT_L BY NUMBER
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('identity_opt', p, sql)

    def p_identity_opt_list(self, p):
        """
        identity_opt_list : identity_opt
                          | identity_opt_list COMMA identity_opt
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('identity_opt_list', p, sql)

    def p_column_def_opt(self, p):
        """
        column_def_opt : NOT NULL
                       | NULL
                       | IDENTITY
                       | IDENTITY LPAREN identity_opt_list RPAREN
                       | PRIMARY KEY
                       | DEFAULT signed_literal
                       | COLLATE q_table_name
                       | references
                       | IDENTIFIED BY column
                       | CHECK LPAREN search_condition RPAREN
                       | WITH SCHEMA column_xml_schema_def
                       | UNIQUE
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('column_def_opt', p, sql)

    def p_column_xml_schema_def(self, p):
        """
        column_xml_schema_def : LPAREN STRING COMMA STRING RPAREN
                              | LPAREN STRING COMMA STRING COMMA STRING RPAREN
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('column_xml_schema_def', p, sql)

    def p_table_constraint_def(self, p):
        """
        table_constraint_def : UNDER q_table_name
                             | opt_constraint_name PRIMARY KEY LPAREN index_column_commalist RPAREN opt_index_option_list
                             | opt_constraint_name FOREIGN KEY LPAREN column_commalist RPAREN references
                             | opt_constraint_name CHECK LPAREN search_condition RPAREN
                             | opt_constraint_name UNIQUE LPAREN column_commalist RPAREN
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('table_constraint_def', p, sql)

    def p_opt_constraint_name(self, p):
        """
        opt_constraint_name : CONSTRAINT identifier
                            |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_constraint_name', p, sql)

    def p_column_commalist(self, p):
        """
        column_commalist : column
                         | column_commalist COMMA column
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s\n     , %s' % (p[1].sql, p[3].sql)
        p[0] = Node('column_commalist', p, sql)

    def p_index_column_commalist(self, p):
        """
        index_column_commalist : column opt_asc_desc
                               | index_column_commalist COMMA column opt_asc_desc
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('index_column_commalist', p, sql)

    def p_index_option(self, p):
        """
        index_option : CLUSTERED
                     | UNIQUE
                     | OBJECT_ID
        """
        sql = p[1]
        p[0] = Node('index_option', p, sql)

    def p_index_option_list(self, p):
        """
        index_option_list : index_option
                          | index_option_list index_option
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('index_option_list', p, sql)

    def p_opt_index_option_list(self, p):
        """
        opt_index_option_list : 
                              | index_option_list
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_index_option_list', p, sql)

    def p_create_index_def(self, p):
        """
        create_index_def : CREATE opt_index_option_list INDEX index ON new_table_name LPAREN index_column_commalist RPAREN
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_index_def', p, sql)

    def p_drop_index(self, p):
        """
        drop_index : DROP INDEX identifier opt_table
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_index', p, sql)

    def p_opt_table(self, p):
        """
        opt_table : 
                  | q_table_name
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_table', p, sql)

    def p_drop_table(self, p):
        """
        drop_table : DROP TABLE q_table_name
                   | DROP VIEW q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_table', p, sql)

    def p_opt_col_add_column(self, p):
        """
        opt_col_add_column : COLUMN
                           |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_col_add_column', p, sql)

    def p_add_col_column_def_list(self, p):
        """
        add_col_column_def_list : column_def
                                | add_col_column_def_list COMMA column_def
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('add_col_column_def_list', p, sql)

    def p_add_col_column_list(self, p):
        """
        add_col_column_list : column
                            | add_col_column_list COMMA column
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('add_col_column_list', p, sql)

    def p_add_column(self, p):
        """
        add_column : ALTER TABLE q_table_name ADD opt_col_add_column add_col_column_def_list
                   | ALTER TABLE q_table_name DROP opt_col_add_column add_col_column_list
                   | ALTER TABLE q_table_name MODIFY opt_col_add_column column_def
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('add_column', p, sql)

    def p_table_rename(self, p):
        """
        table_rename : ALTER TABLE q_table_name RENAME new_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('table_rename', p, sql)

    def p_constraint_op(self, p):
        """
        constraint_op : ADD
                      | DROP
                      | MODIFY
        """
        sql = p[1]
        p[0] = Node('constraint_op', p, sql)

    def p_opt_drop_behavior(self, p):
        """
        opt_drop_behavior : CASCADE
                          | RESTRICT
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_drop_behavior', p, sql)

    def p_opt_table_constraint_def(self, p):
        """
        opt_table_constraint_def : CONSTRAINT identifier opt_drop_behavior
                                 | table_constraint_def
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('opt_table_constraint_def', p, sql)

    def p_alter_constraint(self, p):
        """
        alter_constraint : ALTER TABLE q_table_name constraint_op opt_table_constraint_def
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('alter_constraint', p, sql)

    def p_create_xml_schema(self, p):
        """
        create_xml_schema : CREATE XML SCHEMA STRING
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_xml_schema', p, sql)

    def p_view_query_spec(self, p):
        """
        view_query_spec : query_exp
                        | query_no_from_spec
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('view_query_spec', p, sql)

    def p_view_def(self, p):
        """
        view_def : CREATE VIEW new_table_name opt_column_commalist AS view_query_spec opt_with_check_option
                 | CREATE PROCEDURE VIEW new_table_name AS q_table_name LPAREN column_commalist_or_empty RPAREN LPAREN proc_col_list RPAREN
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('view_def', p, sql)

    def p_opt_with_check_option(self, p):
        """
        opt_with_check_option : WITH CHECK OPTION
                              |
        """
        if len(p) == 1:
           sql = ''
        else:
           sql = ' '.join(p[1:])
        p[0] = Node('opt_with_check_option', p, sql)

    def p_opt_column_commalist(self, p):
        """
        opt_column_commalist : LPAREN column_commalist RPAREN
                             |
        """
        if len(p) == 1:
           sql = ''
        else:
           sql = '(%s)' % (p[2].sql,)
        p[0] = Node('opt_column_commalist', p, sql)

    def p_priv_opt_column_commalist(self, p):
        """
        priv_opt_column_commalist : LPAREN column_commalist RPAREN
                                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '\n     ( %s\n     )' % (p[2].sql,)
        p[0] = Node('priv_opt_column_commalist', p, sql)

    def p_privilege_def(self, p):
        """
        privilege_def : GRANT ALL PRIVILEGES TO grantee
                      | GRANT privileges ON table TO grantee_commalist opt_with_grant_option
                      | GRANT EXECUTE ON function_name TO grantee_commalist opt_with_grant_option
                      | GRANT REXECUTE ON STRING TO grantee_commalist
                      | GRANT UNDER ON q_old_type_name TO grantee_commalist opt_with_grant_option
                      | GRANT grantee_commalist TO grantee_commalist opt_with_admin_option
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('privilege_def', p, sql)

    def p_opt_with_admin_option(self, p):
        """
        opt_with_admin_option : WITH ADMIN_L OPTION
                              |
        """
        if len(p) == 1:
           sql = ''
        else:
           sql = ' '.join(p[1:])
        p[0] = Node('opt_with_admin_option', p, sql)

    def p_privilege_revoke(self, p):
        """
        privilege_revoke : REVOKE privileges ON table FROM grantee_commalist
                         | REVOKE EXECUTE ON function_name FROM grantee_commalist
                         | REVOKE UNDER ON q_old_type_name FROM grantee_commalist
                         | REVOKE REXECUTE ON STRING FROM grantee_commalist
                         | REVOKE grantee_commalist FROM grantee_commalist
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('privilege_revoke', p, sql)

    def p_opt_with_grant_option(self, p):
        """
        opt_with_grant_option : 
                              | WITH GRANT OPTION
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('opt_with_grant_option', p, sql)

    def p_privileges(self, p):
        """
        privileges : ALL PRIVILEGES
                   | ALL
                   | operation_commalist
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('privileges', p, sql)

    def p_operation_commalist(self, p):
        """
        operation_commalist : operation
                            | operation_commalist COMMA operation
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('operation_commalist', p, sql)

    def p_operation(self, p):
        """
        operation : SELECT priv_opt_column_commalist
                  | INSERT
                  | DELETE
                  | UPDATE priv_opt_column_commalist
                  | REFERENCES priv_opt_column_commalist
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('operation', p, sql)

    def p_grantee_commalist(self, p):
        """
        grantee_commalist : grantee
                          | grantee_commalist COMMA grantee
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('grantee_commalist', p, sql)

    def p_grantee(self, p):
        """
        grantee : PUBLIC
                | user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('grantee', p, sql)

    def p_set_pass(self, p):
        """
        set_pass : SET PASSWORD identifier identifier
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('set_pass', p, sql)

    def p_create_user_statement(self, p):
        """
        create_user_statement : CREATE USER user
                              | CREATE ROLE_L user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_user_statement', p, sql)

    def p_delete_user_statement(self, p):
        """
        delete_user_statement : DELETE USER user
                              | DELETE USER user CASCADE
                              | DROP USER user
                              | DROP USER user CASCADE
                              | DROP ROLE_L user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('delete_user_statement', p, sql)

    def p_set_group_stmt(self, p):
        """
        set_group_stmt : SET USER GROUP user user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('set_group_stmt', p, sql)

    def p_add_group_stmt(self, p):
        """
        add_group_stmt : ADD USER GROUP user user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('add_group_stmt', p, sql)

    def p_delete_group_stmt(self, p):
        """
        delete_group_stmt : DELETE USER GROUP user user
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('delete_group_stmt', p, sql)

    def p_opt_attach_primary_key(self, p):
        """
        opt_attach_primary_key : PRIMARY KEY LPAREN column_commalist RPAREN
                               |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s (%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('opt_attach_primary_key', p, sql)

    def p_attach_table(self, p):
        """
        attach_table : ATTACH TABLE attach_q_table_name opt_attach_primary_key opt_as FROM literal opt_login opt_not_select opt_remote_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('attach_table', p, sql)

    def p_opt_as(self, p):
        """
        opt_as : AS new_table_name
               |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_as', p, sql)

    def p_opt_login(self, p):
        """
        opt_login : USER scalar_exp PASSWORD scalar_exp
                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql)
        p[0] = Node('opt_login', p, sql)

    def p_opt_not_select(self, p):
        """
        opt_not_select : NOT SELECT
                       |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_not_select', p, sql)

    def p_opt_remote_name(self, p):
        """
        opt_remote_name : REMOTE AS scalar_exp
                        |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('opt_remote_name', p, sql)

    def p_cursor_type(self, p):
        """
        cursor_type : STATIC_L
                    | DYNAMIC
                    | KEYSET
        """
        sql = p[1]
        p[0] = Node('cursor_type', p, sql)

    def p_cursor_def(self, p):
        """
        cursor_def : DECLARE identifier CURSOR FOR query_exp
                   | DECLARE identifier cursor_type CURSOR FOR query_exp
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('cursor_def', p, sql)

    def p_opt_order_by_clause(self, p):
        """
        opt_order_by_clause : ORDER BY ordering_spec_commalist
                            |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql_ordering_spec_commalist = p[3].sql
            if sql_ordering_spec_commalist.find('\n') >= 0:
                sql_ordering_spec_commalist = common.set_indent(p[3].set_list_break('ordering_spec'), ' ' * 5)
            sql = '\n %s %s %s' % (p[1], p[2], sql_ordering_spec_commalist)
        p[0] = Node('opt_order_by_clause', p, sql)

    def p_ordering_spec_commalist(self, p):
        """
        ordering_spec_commalist : ordering_spec
                                | ordering_spec_commalist COMMA ordering_spec
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('ordering_spec_commalist', p, sql)

    def p_ordering_spec(self, p):
        """
        ordering_spec : scalar_exp opt_asc_desc
                      | mssql_xml_col opt_asc_desc
        """
        sql_opt_asc_desc = ' ' + p[2].sql if p[2].sql else ''
        sql = '%s%s' % (p[1].sql, sql_opt_asc_desc)
        p[0] = Node('ordering_spec', p, sql)

    def p_opt_asc_desc(self, p):
        """
        opt_asc_desc : ASC
                     | DESC
                     |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_asc_desc', p, sql)

    def p_create_snapshot_log(self, p):
        """
        create_snapshot_log : CREATE SNAPSHOT LOGX FOR q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_snapshot_log', p, sql)

    def p_drop_snapshot_log(self, p):
        """
        drop_snapshot_log : DROP SNAPSHOT LOGX FOR q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_snapshot_log', p, sql)

    def p_purge_snapshot_log(self, p):
        """
        purge_snapshot_log : PURGE SNAPSHOT LOGX FOR q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('purge_snapshot_log', p, sql)

    def p_opt_snapshot_string_literal(self, p):
        """
        opt_snapshot_string_literal : STRING
                                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_snapshot_string_literal', p, sql)

    def p_opt_snapshot_where_clause(self, p):
        """
        opt_snapshot_where_clause : WHERE STRING
                                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_snapshot_where_clause', p, sql)

    def p_create_snapshot(self, p):
        """
        create_snapshot : CREATE SNAPSHOT q_table_name FROM q_table_name opt_snapshot_string_literal opt_snapshot_where_clause
                        | CREATE NONINCREMENTAL SNAPSHOT q_table_name AS STRING
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_snapshot', p, sql)

    def p_opt_with_delete(self, p):
        """
        opt_with_delete : WITH DELETE
                        |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_with_delete', p, sql)

    def p_drop_snapshot(self, p):
        """
        drop_snapshot : DROP SNAPSHOT q_table_name opt_with_delete
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_snapshot', p, sql)

    def p_opt_nonincremental(self, p):
        """
        opt_nonincremental : AS NONINCREMENTAL
                           |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_nonincremental', p, sql)

    def p_refresh_snapshot(self, p):
        """
        refresh_snapshot : UPDATE SNAPSHOT q_table_name opt_nonincremental
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('refresh_snapshot', p, sql)

    def p_create_freetext_index(self, p):
        """
        create_freetext_index : CREATE TEXT_L opt_xml INDEX ON q_table_name LPAREN column RPAREN opt_with_key opt_deffer_generation opt_with opt_data_modification_action opt_lang opt_enc
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_freetext_index', p, sql)

    def p_opt_data_modification_action(self, p):
        """
        opt_data_modification_action : USING FUNCTION
                                     |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_data_modification_action', p, sql)

    def p_opt_column(self, p):
        """
        opt_column : LPAREN column RPAREN
                   |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('opt_column', p, sql)

    def p_create_freetext_trigger(self, p):
        """
        create_freetext_trigger : CREATE TEXT_L TRIGGER ON q_table_name opt_column
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('create_freetext_trigger', p, sql)

    def p_drop_freetext_trigger(self, p):
        """
        drop_freetext_trigger : DROP TEXT_L TRIGGER ON q_table_name opt_column
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_freetext_trigger', p, sql)

    def p_opt_xml(self, p):
        """
        opt_xml : XML
                |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_xml', p, sql)

    def p_opt_with_key(self, p):
        """
        opt_with_key : WITH KEY column
                     |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('opt_with_key', p, sql)

    def p_opt_with(self, p):
        """
        opt_with : CLUSTERED WITH LPAREN column_commalist RPAREN
                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s (%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('opt_with', p, sql)

    def p_opt_lang(self, p):
        """
        opt_lang : 
                 | LANGUAGE STRING
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_lang', p, sql)

    def p_opt_enc(self, p):
        """
        opt_enc : 
                | ENCODING STRING
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_enc', p, sql)

    def p_opt_deffer_generation(self, p):
        """
        opt_deffer_generation : 
                              | NOT INSERT
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_deffer_generation', p, sql)

    def p_manipulative_statement(self, p):
        """
        manipulative_statement : query_exp
                               | query_no_from_spec
                               | update_statement_positioned
                               | update_statement_searched
                               | insert_statement
                               | delete_statement_positioned
                               | delete_statement_searched
                               | call_statement
                               | static_method_invocation
                               | METHOD CALL static_method_invocation
                               | top_level_method_invocation
                               | set_statement
                               | drop_xml_view
                               | commit_statement
                               | rollback_statement
                               | admin_statement
                               | use_statement
                               | attach_table
                               | create_snapshot_log
                               | drop_snapshot_log
                               | purge_snapshot_log
                               | create_snapshot
                               | drop_snapshot
                               | refresh_snapshot
                               | create_freetext_index
                               | create_freetext_trigger
                               | drop_freetext_trigger
        """
        sql = p[1].sql
        p[0] = Node('manipulative_statement', p, sql)

    def p_use_statement(self, p):
        """
        use_statement : USE identifier
        """
        if len(p) == 3:
           sql = '%s %s' % (p[1], p[2].sql)
        else:
           sql = '%s %s;' % (p[1], p[2].sql)
        p[0] = Node('use_statement', p, sql)

    def p_close_statement(self, p):
        """
        close_statement : CLOSE cursor
        """
        sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('close_statement', p, sql)

    def p_commit_statement(self, p):
        """
        commit_statement : COMMIT WORK
        """
        sql = '%s %s' % (p[1], p[2])
        p[0] = Node('commit_statement', p, sql)

    def p_delete_statement_positioned(self, p):
        """
        delete_statement_positioned : DELETE FROM table WHERE CURRENT OF cursor
        """
        sql = '%s %s %s %s %s %s %s' % (p[1], p[2], p[3].sql, p[4], p[5], p[6], p[7].sql)
        p[0] = Node('delete_statement_positioned', p, sql)

    def p_delete_statement_searched(self, p):
        """
        delete_statement_searched : DELETE FROM table opt_where_clause
        """
        sql = '%s %s %s %s' % (p[1], p[2], p[3].sql, p[4].sql)
        p[0] = Node('delete_statement_searched', p, sql)

    def p_fetch_statement(self, p):
        """
        fetch_statement : FETCH NEXT FROM cursor INTO target_commalist
        """
        sql = ' '.join([i.sql if isinstance(i, Node) else i for i in p[1:]])
        p[0] = Node('fetch_statement', p, sql)

    def p_insert_mode(self, p):
        """
        insert_mode : INTO
                    | REPLACING
                    | SOFT
        """
        sql = p[1]
        p[0] = Node('insert_mode', p, sql)

    def p_insert_statement(self, p):
        """
        insert_statement : INSERT insert_mode table priv_opt_column_commalist values_or_query_spec
        """
        sql_priv_opt_column_commalist = ' ' + p[4].sql if p[4].sql else ''
        sql = '%s %s %s%s %s' % (p[1], p[2].sql, p[3].sql, sql_priv_opt_column_commalist, p[5].sql)
        p[0] = Node('insert_statement', p, sql)

    def p_values_or_query_spec(self, p):
        """
        values_or_query_spec : VALUES LPAREN insert_atom_commalist RPAREN
                             | query_spec
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '\n%s \n     ( %s\n     )' % (p[1], p[3].sql)
        p[0] = Node('values_or_query_spec', p, sql)

    def p_insert_atom_commalist(self, p):
        """
        insert_atom_commalist : insert_atom
                              | insert_atom_commalist COMMA insert_atom
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s\n     , %s' % (p[1].sql, p[3].sql)
        p[0] = Node('insert_atom_commalist', p, sql)

    def p_insert_atom(self, p):
        """
        insert_atom : scalar_exp
        """
        sql_insert_atom = p[1].sql
        if str(sql_insert_atom).find('\n') >= 0:
            sql_insert_atom = common.set_indent(sql_insert_atom, ' ' * 5)
        p[0] = Node('insert_atom', p, sql_insert_atom)

    def p_sql_option(self, p):
        """
        sql_option : ORDER
                   | HASH
                   | LOOP
                   | INDEX identifier
                   | INDEX PRIMARY KEY
                   | INDEX TEXT_L KEY
        """
        if len(p) == 2:
            sql = p[1]
        else:
            if isinstance(p[2], Node):
                sql = '%s %s' % (p[1], p[2].sql)
            else:
                sql = ' '.join(p[1:])
        p[0] = Node('sql_option', p, sql)

    def p_sql_opt_commalist(self, p):
        """
        sql_opt_commalist : sql_option
                          | sql_opt_commalist COMMA sql_option
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('sql_opt_commalist', p, sql)

    def p_opt_sql_opt(self, p):
        """
        opt_sql_opt : OPTION LPAREN sql_opt_commalist RPAREN
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s (%s)' % (p[1], p[3].sql)
        p[0] = Node('opt_sql_opt', p, sql)

    def p_opt_table_opt(self, p):
        """
        opt_table_opt : TABLE OPTION LPAREN sql_opt_commalist RPAREN
                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s (%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('opt_table_opt', p, sql)

    def p_cursor_option(self, p):
        """
        cursor_option : EXCLUSIVE
                      | PREFETCH NUMBER
        """
        sql = ' '.join(p[1:])
        p[0] = Node('cursor_option', p, sql)

    def p_cursor_options_commalist(self, p):
        """
        cursor_options_commalist : cursor_option
                                 | cursor_options_commalist COMMA cursor_option
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('cursor_options_commalist', p, sql)

    def p_opt_cursor_options_list(self, p):
        """
        opt_cursor_options_list : LPAREN cursor_options_commalist RPAREN
                                |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('opt_cursor_options_list', p, sql)

    def p_open_statement(self, p):
        """
        open_statement : OPEN cursor opt_cursor_options_list
        """
        sql = '%s %s%s' % (p[1], p[2].sql, ' ' + p[3].sql if p[3].sql else '')
        p[0] = Node('open_statement', p, sql)

    def p_rollback_statement(self, p):
        """
        rollback_statement : ROLLBACK WORK
        """
        sql = ' '.join(p[1:])
        p[0] = Node('rollback_statement', p, sql)

    def p_with_opt_cursor_options_list(self, p):
        """
        with_opt_cursor_options_list : WITH opt_cursor_options_list
                                     |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('with_opt_cursor_options_list', p, sql)

    def p_select_statement(self, p):
        """
        select_statement : SELECT opt_top selection INTO target_commalist table_exp with_opt_cursor_options_list
        """
        sql = '%s %s %s %s %s %s %s' % (p[1], p[2].sql, p[3].sql, p[4], p[5].sql, p[6].sql, p[7].sql)
        p[0] = Node('select_statement', p, sql)

    def p_opt_all_distinct(self, p):
        """
        opt_all_distinct : ALL
                         | DISTINCT
                         |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_all_distinct', p, sql)

    def p_opt_ties(self, p):
        """
        opt_ties : WITH TIES
                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1] + ' ' + p[2]
        p[0] = Node('opt_ties', p, sql)

    def p_opt_top(self, p):
        """
        opt_top : opt_all_distinct
                | opt_all_distinct TOP NUMBER opt_ties
                | opt_all_distinct TOP LPAREN scalar_exp RPAREN opt_ties
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 5:
            sql = '%s%s %s%s' % (p[1].sql + ' ' if p[1].sql else '', p[2], p[3], ' ' + p[4].sql if p[4].sql else '')
        else:
            sql = '%s%s (%s)%s' % (p[1].sql + ' ' if p[1].sql else '', p[2], p[4].sql, ' ' + p[6].sql if p[6].sql else '')
        p[0] = Node('opt_top', p, sql)

    def p_update_statement_positioned(self, p):
        """
        update_statement_positioned : UPDATE table SET assignment_commalist WHERE CURRENT OF cursor
        """
        sql = '%s %s %s %s %s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql, p[5], p[6], p[7], p[8].sql)
        p[0] = Node('update_statement_positioned', p, sql)

    def p_assignment_commalist(self, p):
        """
        assignment_commalist : assignment
                             | assignment_commalist COMMA assignment
                             |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s\n     , %s' % (p[1].sql, p[3].sql)
        p[0] = Node('assignment_commalist', p, sql)

    def p_assignment(self, p):
        """
        assignment : column comparison scalar_exp
        """
        sql_scalar_exp = p[3].sql
        if str(sql_scalar_exp).find('\n') >= 0:
            length = len(str(p[1].sql)) + len(p[2].sql) + 2 + 5
            sql_scalar_exp = common.set_indent(sql_scalar_exp, ' ' * length)
        sql = '%s %s %s' % (p[1].sql, p[2].sql, sql_scalar_exp)
        p[0] = Node('assignment', p, sql)

    def p_update_statement_searched(self, p):
        """
        update_statement_searched : UPDATE table SET assignment_commalist opt_where_clause
        """
        sql = '%s %s \n   %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql, p[5].sql)
        p[0] = Node('update_statement_searched', p, sql)

    def p_target_commalist(self, p):
        """
        target_commalist : target
                         | target_commalist COMMA target
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('target_commalist', p, sql)

    def p_target(self, p):
        """
        target : column_ref
               | parameter
               | member_observer
               | lvalue_array_ref
        """
        sql = p[1].sql
        p[0] = Node('target', p, sql)

    def p_opt_where_clause(self, p):
        """
        opt_where_clause : where_clause
                         |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_where_clause', p, sql)

    def p_query_exp(self, p):
        """
        query_exp : query_term
                  | non_final_union_exp UNION         opt_corresponding query_term
                  | non_final_union_exp UNION     ALL opt_corresponding query_term
                  | non_final_union_exp INTERSECT     opt_corresponding query_term
                  | non_final_union_exp INTERSECT ALL opt_corresponding query_term
                  | non_final_union_exp EXCEPT        opt_corresponding query_term
                  | non_final_union_exp EXCEPT    ALL opt_corresponding query_term
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 5:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        else:
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5].sql)
        p[0] = Node('query_exp', p, sql)

    def p_non_final_union_exp(self, p):
        """
        non_final_union_exp : non_final_query_term
                            | non_final_union_exp UNION         opt_corresponding non_final_query_term
                            | non_final_union_exp UNION     ALL opt_corresponding non_final_query_term
                            | non_final_union_exp INTERSECT     opt_corresponding non_final_query_term
                            | non_final_union_exp INTERSECT ALL opt_corresponding non_final_query_term
                            | non_final_union_exp EXCEPT        opt_corresponding non_final_query_term
                            | non_final_union_exp EXCEPT    ALL opt_corresponding non_final_query_term
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 5:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        else:
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5].sql)
        p[0] = Node('non_final_union_exp', p, sql)

    def p_non_final_query_term(self, p):
        """
        non_final_query_term : non_final_query_spec
        """
        sql = p[1].sql
        p[0] = Node('non_final_query_term', p, sql)

    def p_query_term(self, p):
        """
        query_term : query_spec
                   | LPAREN query_exp RPAREN opt_order_by_clause
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '(%s)%s' % (p[2].sql, ' ' + p[4].sql if p[4].sql else '')
        p[0] = Node('query_term', p, sql)

    def p_opt_corresponding(self, p):
        """
        opt_corresponding : CORRESPONDING BY LPAREN column_commalist RPAREN
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s (%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('opt_corresponding', p, sql)

    def p_non_final_query_spec(self, p):
        """
        non_final_query_spec : SELECT opt_top selection non_final_table_exp
        """
        sql = '%s %s %s %s' % (p[1], p[2].sql, p[3].sql, p[4].sql)
        p[0] = Node('non_final_query_spec', p, sql)

    def p_query_spec(self, p):
        """
        query_spec : SELECT opt_top selection table_exp
        """
        sql_opt_top = ' ' + p[2].sql if p[2].sql else ''
        sql_selection = "\n       " + common.set_indent(p[3].sql, '     ') if sql_opt_top else common.set_indent(p[3].sql, '     ')
        sql = '%s%s %s %s' % (p[1], sql_opt_top, sql_selection, p[4].sql)
        p[0] = Node('query_spec', p, sql)

    def p_query_no_from_spec(self, p):
        """
        query_no_from_spec : SELECT opt_top selection
        """
        sql_opt_top = ' ' + p[2].sql if p[2].sql else ''
        sql_selection = "\n       " + common.set_indent(p[3].sql, '     ') if sql_opt_top else common.set_indent(p[3].sql, '     ')
        sql = '%s%s %s' % (p[1], sql_opt_top,sql_selection)
        p[0] = Node('query_no_from_spec', p, sql)

    def p_selection(self, p):
        """
        selection : select_scalar_exp_commalist
        """
        sql = p[1].sql
        p[0] = Node('selection', p, sql)

    def p_non_final_table_exp(self, p):
        """
        non_final_table_exp : from_clause opt_where_clause opt_group_by_clause opt_having_clause
        """
        sql_opt_where_clause = ' ' + p[2].sql if p[2].sql else ''
        sql_opt_group_by_clause = ' ' + p[3].sql if p[3].sql else ''
        sql_opt_having_clause = ' ' + p[4].sql if p[4].sql else ''
        sql = '%s%s%s%s' % (p[1].sql, sql_opt_where_clause, sql_opt_group_by_clause, sql_opt_having_clause)
        p[0] = Node('non_final_table_exp', p, sql)

    def p_table_exp(self, p):
        """
        table_exp : from_clause opt_where_clause opt_group_by_clause opt_having_clause opt_order_by_clause opt_lock_mode opt_sql_opt
        """
        sql_opt_where_clause = ' ' + p[2].sql if p[2].sql else ''
        sql_opt_group_by_clause = ' ' + p[3].sql if p[3].sql else ''
        sql_opt_having_clause = ' ' + p[4].sql if p[4].sql else ''
        sql_opt_order_by_clause = ' ' + p[5].sql if p[5].sql else ''
        sql_opt_lock_mode = ' ' + p[6].sql if p[6].sql else ''
        sql_opt_sql_opt = ' ' + p[7].sql if p[7].sql else ''
        sql = '\n  %s%s%s%s%s%s%s' % (p[1].sql, sql_opt_where_clause, sql_opt_group_by_clause, sql_opt_having_clause, 
                                      sql_opt_order_by_clause, sql_opt_lock_mode, sql_opt_sql_opt)
        p[0] = Node('table_exp', p, sql)

    def p_from_clause(self, p):
        """
        from_clause : FROM table_ref_commalist
        """
        table_ref_commalist = common.set_indent(p[2].sql, ' ' * 5)
        sql = '%s %s' % (p[1], table_ref_commalist)
        p[0] = Node('from_clause', p, sql)

    def p_table_ref_commalist(self, p):
        """
        table_ref_commalist : table_ref
                            | table_ref_commalist COMMA table_ref
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s\n, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('table_ref_commalist', p, sql)

    def p_proc_col_list(self, p):
        """
        proc_col_list : column_def
                      | proc_col_list COMMA column_def
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('proc_col_list', p, sql)

    def p_opt_proc_col_list(self, p):
        """
        opt_proc_col_list : LPAREN proc_col_list RPAREN
        """
        sql = '(%s)' % (p[2].sql,)
        p[0] = Node('opt_proc_col_list', p, sql)

    def p_column_commalist_or_empty(self, p):
        """
        column_commalist_or_empty : column_commalist
                                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('column_commalist_or_empty', p, sql)

    def p_table_ref(self, p):
        """
        table_ref : table
                  | LPAREN query_exp RPAREN identifier
                  | LPAREN query_exp RPAREN AS identifier
                  | joined_table
                  | q_table_name LPAREN column_commalist_or_empty RPAREN opt_proc_col_list identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 5:
            query_exp = common.set_indent(p[2].sql, ' ' * 3)
            sql = '(%s\n  ) %s' % (query_exp, p[4].sql)
        elif len(p) == 6:
            query_exp = common.set_indent(p[2].sql, ' ' * 3)
            sql = '(%s\n  ) %s %s' % (query_exp, p[4], p[5].sql)
        else:
            sql = '%s (%s) %s %s' % (p[1].sql, p[3].sql, p[5].sql, p[6].sql)
        p[0] = Node('table_ref', p, sql)

    def p_table_ref_nj(self, p):
        """
        table_ref_nj : table
                     | subquery identifier
                     | subquery AS identifier
                     | LPAREN joined_table RPAREN
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 3:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        else:
            if isinstance(p[1], Node):
                sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
            else:
                sql = '(%s)' % (p[2].sql,)
        p[0] = Node('table_ref_nj', p, sql)

    def p_jtype(self, p):
        """
        jtype : LEFT opt_outer
              | RIGHT opt_outer
              | FULL opt_outer
              | INNER
              | CROSS
              |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1]
        else:
            sql = '%s%s' % (p[1], ' ' + p[2].sql if p[2].sql else '')
        p[0] = Node('jtype', p, sql)

    def p_opt_outer(self, p):
        """
        opt_outer : OUTER
                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_outer', p, sql)

    def p_join(self, p):
        """
        join : NATURAL jtype
             | jtype
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('join', p, sql)

    def p_joined_table(self, p):
        """
        joined_table : joined_table_1
                     | LPAREN joined_table_1 RPAREN
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '(%s)' % (p[2].sql,)
        p[0] = Node('joined_table', p, sql)

    def p_joined_table_1(self, p):
        """
        joined_table_1 : table_ref join JOIN table_ref_nj join_condition
        """
        sql_join = p[2].sql
        sql_JOIN = ' ' + p[3] if sql_join else p[3]
        sql_table_ref_nj = common.set_indent(p[4].sql, ' ' * (len(sql_join + sql_JOIN) + 1))
        idx_last_on = len(sql_join + sql_JOIN) + len(sql_table_ref_nj.split('\n')[-1])
        if sql_table_ref_nj.find('\n') >= 0:
            idx_last_on = len(sql_table_ref_nj.split('\n')[-1]) - 3
        sql_join_condition = common.set_indent(p[5].sql, ' ' * idx_last_on)
        sql = '%s\n  %s%s %s %s' % (p[1].sql, p[2].sql, sql_JOIN, sql_table_ref_nj, sql_join_condition)
        p[0] = Node('joined_table_1', p, sql)

    def p_join_condition(self, p):
        """
        join_condition : ON search_condition
                       | USING LPAREN column_commalist RPAREN
                       |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s (%s)' % (p[1], p[3].sql)
        p[0] = Node('join_condition', p, sql)

    def p_where_clause(self, p):
        """
        where_clause : WHERE search_condition
        """
        sql = '\n %s %s' % (p[1], p[2].sql,)
        p[0] = Node('where_clause', p, sql)

    def p_opt_group_by_clause(self, p):
        """
        opt_group_by_clause : GROUP BY ordering_spec_commalist
                            | GROUP BY ROLLUP LPAREN ordering_spec_commalist RPAREN
                            | GROUP BY CUBE LPAREN ordering_spec_commalist RPAREN
                            |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 4:
            sql_ordering_spec_commalist = p[3].sql
            if sql_ordering_spec_commalist.find('\n') >= 0:
                sql_ordering_spec_commalist = common.set_indent(p[3].set_list_break('ordering_spec'), ' ' * 5)
            sql = '\n %s %s %s' % (p[1], p[2], sql_ordering_spec_commalist)
        else:
            sql = '\n %s %s %s (%s)' % (p[1], p[2], p[3], p[5].sql)
        p[0] = Node('opt_group_by_clause', p, sql)

    def p_opt_having_clause(self, p):
        """
        opt_having_clause : HAVING search_condition
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_having_clause', p, sql)

    def p_opt_lock_mode(self, p):
        """
        opt_lock_mode : FOR UPDATE
                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('opt_lock_mode', p, sql)

    def p_search_condition(self, p):
        """
        search_condition : search_condition OR search_condition
                         | search_condition AND search_condition
                         | NOT search_condition
                         | LPAREN search_condition RPAREN
                         | predicate
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            if isinstance(p[1], Node):
                sql_and_or = ' ' + p[2] if len(p[2]) == 2 else p[2]
                sql = '%s\n   %s %s' % (p[1].sql, sql_and_or, p[3].sql)
            else:
                sql = '(%s)' % (p[2].sql,)
        p[0] = Node('search_condition', p, sql)

    def p_predicate(self, p):
        """
        predicate : comparison_predicate
                  | between_predicate
                  | like_predicate
                  | test_for_null
                  | in_predicate
                  | all_or_any_predicate
                  | existence_test
                  | scalar_exp_predicate
        """
        sql = p[1].sql
        p[0] = Node('predicate', p, sql)

    def p_scalar_exp_predicate(self, p):
        """
        scalar_exp_predicate : scalar_exp
        """
        sql = p[1].sql
        p[0] = Node('scalar_exp_predicate', p, sql)

    def p_comparison_predicate(self, p):
        """
        comparison_predicate : scalar_exp comparison scalar_exp
        """
        sql_scalar_exp1 = common.set_indent(p[1].sql, ' ' * 5)
        indent = len(unicode(sql_scalar_exp1).split('\n')[-1]) + 2 + len(p[2].sql) + 5
        sql_scalar_exp2 = common.set_indent(p[3].sql, ' ' * indent)
        sql = '%s %s %s' % (sql_scalar_exp1, p[2].sql, sql_scalar_exp2)
        p[0] = Node('comparison_predicate', p, sql)

    def p_between_predicate(self, p):
        """
        between_predicate : scalar_exp NOT BETWEEN scalar_exp AND scalar_exp
                          | scalar_exp BETWEEN scalar_exp AND scalar_exp
        """
        if len(p) == 7:
            sql = '%s %s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5], p[6].sql)
        else:
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4], p[5].sql)
        p[0] = Node('between_predicate', p, sql)

    def p_like_predicate(self, p):
        """
        like_predicate : scalar_exp NOT LIKE scalar_exp opt_escape
                       | scalar_exp LIKE scalar_exp opt_escape
        """
        if len(p) == 6:
            sql = '%s %s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql, p[5].sql)
        else:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        p[0] = Node('like_predicate', p, sql)

    def p_opt_escape(self, p):
        """
        opt_escape : ESCAPE atom
                   | BEGIN ESCAPE atom END
                   |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s %s %s %s' % (p[1], p[2], p[3].sql, p[4])
        p[0] = Node('opt_escape', p, sql)

    def p_test_for_null(self, p):
        """
        test_for_null : scalar_exp IS NOT NULL
                      | scalar_exp IS NULL
        """
        if len(p) == 5:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3], p[4])
        else:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3])
        p[0] = Node('test_for_null', p, sql)

    def p_in_predicate(self, p):
        """
        in_predicate : scalar_exp NOT IN subquery
                     | scalar_exp IN subquery
                     | scalar_exp NOT IN LPAREN scalar_exp_commalist RPAREN
                     | scalar_exp IN LPAREN scalar_exp_commalist RPAREN
        """
        if len(p) == 4:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        elif len(p) == 5:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3], p[4].sql)
        elif len(p) == 6:
            sql = '%s %s (%s)' % (p[1].sql, p[2], p[4].sql)
        else:
            sql = '%s %s %s (%s)' % (p[1].sql, p[2], p[3], p[5].sql)
        p[0] = Node('in_predicate', p, sql)

    def p_all_or_any_predicate(self, p):
        """
        all_or_any_predicate : scalar_exp comparison any_all_some subquery
        """
        sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3].sql, p[4].sql)
        p[0] = Node('all_or_any_predicate', p, sql)

    def p_any_all_some(self, p):
        """
        any_all_some : ANY
                     | ALL
                     | SOME
        """
        sql = p[1]
        p[0] = Node('any_all_some', p, sql)

    def p_existence_test(self, p):
        """
        existence_test : EXISTS subquery
        """
        sql_subquery = common.set_indent(p[2].sql, ' ' * 12)
        sql = '%s %s' % (p[1], sql_subquery)
        p[0] = Node('existence_test', p, sql)

    def p_scalar_subquery(self, p):
        """
        scalar_subquery : subquery
        """
        sql = p[1].sql
        p[0] = Node('scalar_subquery', p, sql)

    def p_subquery(self, p):
        """
        subquery : LPAREN SELECT opt_top selection table_exp RPAREN
        """
        sql_table_exp = common.set_indent(p[5].sql, ' ' * 3)
        sql = '(%s%s %s %s\n  )' % (p[2], ' ' + p[3].sql if p[3].sql else '', p[4].sql, sql_table_exp)
        p[0] = Node('subquery', p, sql)

    def p_scalar_exp(self, p):
        """
        scalar_exp : scalar_exp MINUS scalar_exp
                   | scalar_exp PLUS scalar_exp
                   | scalar_exp TIMES scalar_exp
                   | scalar_exp DIVIDE scalar_exp
                   | scalar_exp BITAND scalar_exp
                   | scalar_exp BITOR scalar_exp
                   | PLUS scalar_exp
                   | MINUS scalar_exp
                   | BITNOT scalar_exp
                   | assignment_statement
                   | string_concatenation_operator
                   | column_ref
                   | scalar_exp_no_col_ref
                   | obe_literal
                   | set_function_specification
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('scalar_exp', p, sql)

    def p_set_function_specification(self, p):
        """
        set_function_specification : COUNT LPAREN TIMES RPAREN
                                   | general_set_function
        """
        if len(p) == 5:
            sql = '%s(*)' % (p[1],)
        else:
            sql = p[1].sql
        p[0] = Node('set_function_specification', p, sql)

    def p_general_set_function(self, p):
        """
        general_set_function : AVG LPAREN opt_all_distinct scalar_exp RPAREN
                             | MAX LPAREN opt_all_distinct scalar_exp RPAREN
                             | MIN LPAREN opt_all_distinct scalar_exp RPAREN
                             | SUM LPAREN opt_all_distinct scalar_exp RPAREN
                             | COUNT LPAREN opt_all_distinct scalar_exp RPAREN
        """
        sql_opt_all_distinct = p[3].sql + ' ' if p[3].sql else ''
        sql = '%s(%s%s)' % (p[1], sql_opt_all_distinct, p[4].sql)
        p[0] = Node('general_set_function', p, sql)

    def p_scalar_exp_no_col_ref(self, p):
        """
        scalar_exp_no_col_ref : atom_no_obe
                              | aggregate_ref
                              | scalar_subquery
                              | LPAREN scalar_exp RPAREN
                              | LPAREN scalar_exp COMMA scalar_exp_commalist RPAREN
                              | function_call
                              | new_invocation
                              | cvt_exp
                              | cast_exp
                              | simple_case
                              | searched_case
                              | coalesce_exp
                              | nullif_exp
                              | array_ref
                              | static_method_invocation
                              | method_invocation
                              | member_observer
                              | row_number
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '(%s)' % (p[2].sql,)
        else:
            sql = '(%s, %s)' % (p[2].sql, p[4].sql)
        p[0] = Node('scalar_exp_no_col_ref', p, sql)

    def p_scalar_exp_no_col_ref_no_mem_obs_chain(self, p):
        """
        scalar_exp_no_col_ref_no_mem_obs_chain : atom_no_obe
                                               | aggregate_ref
                                               | scalar_subquery
                                               | LPAREN scalar_exp RPAREN
                                               | LPAREN scalar_exp COMMA scalar_exp_commalist RPAREN
                                               | function_call
                                               | new_invocation
                                               | cvt_exp
                                               | cast_exp
                                               | simple_case
                                               | searched_case
                                               | coalesce_exp
                                               | nullif_exp
                                               | array_ref
                                               | static_method_invocation
                                               | method_invocation
                                               | member_observer_no_id_chain
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '(%s)' % (p[2].sql,)
        else:
            sql = '(%s, %s)' % (p[2].sql, p[4].sql)
        p[0] = Node('scalar_exp_no_col_ref_no_mem_obs_chain', p, sql)

    def p_cvt_exp(self, p):
        """
        cvt_exp : CONVERT LPAREN data_type COMMA scalar_exp RPAREN
                | CONVERT LPAREN data_type COMMA scalar_exp COMMA NUMBER RPAREN
        """
        if len(p) == 7:
            sql = '%s(%s, %s)' % (p[1], p[3].sql, p[5].sql)
        else:
            sql = '%s(%s, %s, %s)' % (p[1], p[3].sql, p[5].sql, p[7])
        p[0] = Node('cvt_exp', p, sql)

    def p_opt_collate_exp(self, p):
        """
        opt_collate_exp : COLLATE q_table_name
                        |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_collate_exp', p, sql)

    def p_cast_exp(self, p):
        """
        cast_exp : CAST LPAREN scalar_exp AS data_type opt_collate_exp RPAREN
        """
        sql_opt_collate_exp = ' ' + p[6].sql if p[6].sql else ''
        sql = '%s(%s %s %s%s)' % (p[1], p[3].sql, p[4], p[5].sql, sql_opt_collate_exp)
        p[0] = Node('cast_exp', p, sql)

    def p_mssql_xml_col(self, p):
        """
        mssql_xml_col : MSSQL_XMLCOL_NAME1 MSSQL_XMLCOL_INTNUM MSSQL_XMLCOL_NAMEZ
                      | MSSQL_XMLCOL_NAME1 MSSQL_XMLCOL_INTNUM MSSQL_XMLCOL_NAMEYZ
                      | MSSQL_XMLCOL_NAME1 MSSQL_XMLCOL_INTNUM MSSQL_XMLCOL_NAME MSSQL_XMLCOL_NAMEZ
        """
        sql = ' '.join(p[1:])
        p[0] = Node('mssql_xml_col', p, sql)

    def p_as_expression(self, p):
        """
        as_expression : scalar_exp AS identifier data_type
                      | scalar_exp AS identifier
                      | scalar_exp identifier
                      | scalar_exp AS mssql_xml_col
        """
        if len(p) == 3:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        elif len(p) == 4:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        else:
            sql = '%s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql)
        p[0] = Node('as_expression', p, sql)

    def p_array_ref(self, p):
        """
        array_ref : scalar_exp_no_col_ref LBRACKET scalar_exp RBRACKET
                  | lvalue_array_ref
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s [%s]' % (p[1].sql, p[3].sql)
        p[0] = Node('array_ref', p, sql)

    def p_lvalue_array_ref(self, p):
        """
        lvalue_array_ref : column_ref LBRACKET scalar_exp RBRACKET
        """
        sql = '%s [%s]' % (p[1].sql, p[3].sql)
        p[0] = Node('lvalue_array_ref', p, sql)

    def p_opt_scalar_exp_commalist(self, p):
        """
        opt_scalar_exp_commalist : scalar_exp_commalist
                                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_scalar_exp_commalist', p, sql)

    def p_function_name(self, p):
        """
        function_name : identifier
                      | identifier PERIOD method_identifier
                      | identifier PERIOD identifier PERIOD method_identifier
                      | identifier PERIOD identifier PERIOD identifier PERIOD method_identifier
                      | identifier PERIOD PERIOD method_identifier
                      | identifier PERIOD PERIOD identifier PERIOD method_identifier
                      | LEFT
                      | RIGHT
                      | LOGX
        """
        if len(p) == 2:
            if isinstance(p[1], Node):
                sql = p[1].sql
            else:
                sql = p[1]
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        elif len(p) == 6:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        elif len(p) == 7:
            sql = '%s..%s.%s' % (p[1].sql, p[4].sql, p[6].sql)
        else:
            sql = '%s.%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql, p[7].sql)
        p[0] = Node('function_name', p, sql)

    def p_kwd_commalist(self, p):
        """
        kwd_commalist : identifier KWD_TAG scalar_exp
                      | kwd_commalist COMMA identifier KWD_TAG scalar_exp
        """
        if len(p) == 4:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        else:
            sql = '%s,%s %s %s' % (p[1].sql, p[3].sql, p[4], p[5].sql)
        p[0] = Node('kwd_commalist', p, sql)

    def p_as_commalist(self, p):
        """
        as_commalist : as_expression
                     | as_commalist COMMA as_expression
                     | as_commalist COMMA scalar_exp
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('as_commalist', p, sql)

    def p_opt_arg_commalist(self, p):
        """
        opt_arg_commalist : kwd_commalist
                          | scalar_exp_commalist
                          | scalar_exp_commalist COMMA kwd_commalist
                          | scalar_exp_commalist COMMA as_commalist
                          | as_commalist
                          |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('opt_arg_commalist', p, sql)

    def p_function_call(self, p):
        """
        function_call : function_name LPAREN opt_arg_commalist RPAREN
                      | TIMESTAMP_FUNC LPAREN SQL_TSI COMMA scalar_exp COMMA scalar_exp RPAREN
                      | BEGIN_FN_X identifier LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X LEFT LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X RIGHT LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X LOGX LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X identifier LPAREN scalar_exp IN_L scalar_exp RPAREN END
                      | BEGIN_FN_X USER LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X CHARACTER LPAREN opt_scalar_exp_commalist RPAREN END
                      | BEGIN_FN_X TIMESTAMP_FUNC LPAREN SQL_TSI COMMA scalar_exp COMMA scalar_exp RPAREN END
                      | CALL LPAREN scalar_exp RPAREN LPAREN opt_arg_commalist RPAREN
                      | CURRENT_DATE
                      | CURRENT_TIME
                      | CURRENT_TIME LPAREN scalar_exp RPAREN
                      | CURRENT_TIMESTAMP
                      | CURRENT_TIMESTAMP LPAREN scalar_exp RPAREN
                      | GROUPING LPAREN column_ref RPAREN
        """
        #sql = ' '.join([i.sql if isinstance(i, Node) else i for i in p[1:]])
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 4:
            sql = '%s %s %s' % (p[1], p[2].sql, p[3])
        elif len(p) == 5:
            if isinstance(p[1], Node):
                sql = '%s(%s)' % (p[1].sql, p[3].sql)
            else:
                sql = '%s(%s)' % (p[1], p[3].sql)
        elif len(p) == 7:
            if p[3] == '(':
                sql2 = p[2].sql if isinstance(p[2], Node) else p[2]
                sql = '%s %s(%s) %s' % (p[1], sql2, p[4].sql, p[6])
            else:
                sql = '%s(%s %s %s)' % (p[1], p[3], p[4], p[5].sql)
        elif len(p) == 8:
            sql = '%s(%s) (%s)' % (p[1], p[3].sql, p[6].sql)
        elif len(p) == 9:
            if p[2] == '(':
                sql = '%s(%s, %s, %s)' % (p[1], p[3], p[5].sql, p[7].sql)
            else:
                sql = ' '.join([i.sql if isinstance(i, Node) else i for i in p[1:]])
        else:
            sql = ' '.join([i.sql if isinstance(i, Node) else i for i in p[1:]])
        p[0] = Node('function_call', p, sql)

    def p_obe_literal(self, p):
        """
        obe_literal : BEGIN identifier atom END
                    | BEGIN_U_X STRING END
        """
        if len(p) == 4:
            sql = '%s %s %s' % (p[1], p[2], p[3])
        else:
            sql = '%s %s %s %s' % (p[1], p[2].sql, p[3].sql, p[4])
        p[0] = Node('obe_literal', p, sql)

    def p_scalar_exp_commalist(self, p):
        """
        scalar_exp_commalist : scalar_exp
                             | scalar_exp_commalist COMMA scalar_exp
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('scalar_exp_commalist', p, sql)

    def p_select_scalar_exp_commalist(self, p):
        """
        select_scalar_exp_commalist : scalar_exp
                                    | as_expression
                                    | select_scalar_exp_commalist COMMA scalar_exp
                                    | select_scalar_exp_commalist COMMA as_expression
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s\n, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('scalar_exp_commalist', p, sql)

    def p_atom_no_obe(self, p):
        """
        atom_no_obe : parameter_ref
                    | literal
                    | USER
        """
        if isinstance(p[1], Node):
            sql = p[1].sql
        else:
            sql = p[1]
        p[0] = Node('atom_no_obe', p, sql)

    def p_atom(self, p):
        """
        atom : atom_no_obe
             | obe_literal
        """
        sql = p[1].sql
        p[0] = Node('atom', p, sql)

    def p_simple_case(self, p):
        """
        simple_case : CASE scalar_exp simple_when_list END
        """
        sql_simple_when_list = common.set_indent(p[3].sql, '      ')
        sql = '%s %s %s\n  %s' % (p[1], p[2].sql, sql_simple_when_list, p[4])
        p[0] = Node('simple_case', p, sql)

    def p_searched_case(self, p):
        """
        searched_case : CASE searched_when_list END
        """
        sql_searched_when_list = common.set_indent(p[2].sql, '      ')
        sql = '%s %s\n  %s' % (p[1], sql_searched_when_list, p[3])
        p[0] = Node('searched_case', p, sql)

    def p_searched_when_list(self, p):
        """
        searched_when_list : searched_when
                           | searched_when_list searched_when
        """
        if len(p) == 2:
            sql = '\n' + p[1].sql
        else:
            sql = '%s\n%s' % (p[1].sql, p[2].sql)
        p[0] = Node('searched_when_list', p, sql)

    def p_simple_when_list(self, p):
        """
        simple_when_list : simple_when
                         | simple_when_list simple_when
        """
        if len(p) == 2:
            sql = '\n' + p[1].sql
        else:
            sql = '%s\n%s' % (p[1].sql, p[2].sql)
        p[0] = Node('simple_when_list', p, sql)

    def p_simple_when(self, p):
        """
        simple_when : WHEN scalar_exp THEN scalar_exp
                    | ELSE scalar_exp
        """
        if len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql)
        p[0] = Node('simple_when', p, sql)

    def p_searched_when(self, p):
        """
        searched_when : WHEN search_condition THEN scalar_exp
                      | ELSE scalar_exp
        """
        if len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql)
        p[0] = Node('searched_when', p, sql)

    def p_coalesce_exp(self, p):
        """
        coalesce_exp : COALESCE LPAREN scalar_exp_commalist RPAREN
        """
        sql_scalar_exp_commalist = p[3].sql
        rparen = ')'
        if sql_scalar_exp_commalist.find('\n') >= 0:
            sql_scalar_exp_commalist = ' ' + common.set_indent(p[3].set_list_break('scalar_exp'), ' ' * 10)
            rparen = '\n  )'
        sql = '%s(%s%s' % (p[1], sql_scalar_exp_commalist, rparen)
        p[0] = Node('coalesce_exp', p, sql)

    def p_nullif_exp(self, p):
        """
        nullif_exp : NULLIF LPAREN scalar_exp COMMA scalar_exp RPAREN
        """
        sql_scalar_exp_1 = p[3].sql
        sql_scalar_exp_2 = p[5].sql
        rparen = ')'
        sql_comma = ', '
        if str(sql_scalar_exp_1).find('\n') >= 0:
            sql_scalar_exp_1 = ' ' + common.set_indent(sql_scalar_exp_1, ' ' * 8)
            rparen = '\n  )'
            sql_comma = '\n        , '
        if str(sql_scalar_exp_2).find('\n') >= 0:
            sql_scalar_exp_2 = common.set_indent(sql_scalar_exp_2, ' ' * 8)
            rparen = '\n  )'
            sql_comma = '\n        , '
        sql = '%s(%s%s%s%s' % (p[1], sql_scalar_exp_1, sql_comma, sql_scalar_exp_2, rparen)
        p[0] = Node('nullif_exp', p, sql)

    def p_parameter_ref(self, p):
        """
        parameter_ref : parameter
                      | parameter parameter
                      | parameter INDICATOR parameter
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 3:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        else:
            sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('parameter_ref', p, sql)

    def p_aggregate_ref(self, p):
        """
        aggregate_ref : AGGREGATE function_name LPAREN opt_arg_commalist RPAREN
                      | AMMSC LPAREN DISTINCT scalar_exp RPAREN
                      | AMMSC LPAREN ALL scalar_exp RPAREN
                      | AMMSC LPAREN scalar_exp RPAREN
        """
        if len(p) == 5:
            sql = '%s (%s)' % (p[1], p[3].sql)
        elif len(p) == 6 and p[2] == '(':
            sql = '%s (%s %s)' % (p[1], p[3], p[4].sql)
        else:
            sql = '%s %s (%s)' % (p[1], p[2].sql, p[4].sql)
        p[0] = Node('aggregate_ref', p, sql)

    def p_literal(self, p):
        """
        literal : STRING
                | WSTRING
                | NUMBER
                | APPROXNUM
                | BINARYNUM
                | NULLX
        """
        sql = p[1]
        p[0] = Node('literal', p, sql)

    def p_signed_literal(self, p):
        """
        signed_literal : STRING
                       | WSTRING
                       | NUMBER
                       | MINUS NUMBER
                       | PLUS NUMBER
                       | APPROXNUM
                       | MINUS APPROXNUM
                       | PLUS APPROXNUM
                       | BINARYNUM
                       | NULLX
        """
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('signed_literal', p, sql)

    def p_q_table_name(self, p):
        """
        q_table_name : identifier
                     | identifier PERIOD identifier
                     | identifier PERIOD identifier PERIOD identifier
                     | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('q_table_name', p, sql)

    def p_attach_q_table_name(self, p):
        """
        attach_q_table_name : identifier
                            | identifier PERIOD identifier
                            | identifier PERIOD identifier PERIOD identifier
                            | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('attach_q_table_name', p, sql)

    def p_new_proc_or_bif_name(self, p):
        """
        new_proc_or_bif_name : identifier
                             | identifier PERIOD identifier
                             | identifier PERIOD identifier PERIOD identifier
                             | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('new_proc_or_bif_name', p, sql)

    def p_new_table_name(self, p):
        """
        new_table_name : identifier
                       | identifier PERIOD identifier
                       | identifier PERIOD identifier PERIOD identifier
                       | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('new_table_name', p, sql)

    def p_table(self, p):
        """
        table : q_table_name opt_table_opt
              | q_table_name AS identifier opt_table_opt
              | q_table_name identifier opt_table_opt
        """
        if len(p) == 3:
            sql = '%s%s' % (p[1].sql, ' ' + p[2].sql if p[2].sql else '')
        elif len(p) == 4:
            sql = '%s %s%s' % (p[1].sql, p[2].sql, ' ' + p[3].sql if p[3].sql else '')
        else:
            sql = '%s %s %s%s' % (p[1].sql, p[2], p[3].sql, ' ' + p[4].sql if p[4].sql else '')
        p[0] = Node('table', p, sql)

    def p_column_ref(self, p):
        """
        column_ref : identifier
                   | identifier PERIOD identifier
                   | identifier PERIOD identifier PERIOD identifier
                   | identifier PERIOD identifier PERIOD identifier PERIOD identifier
                   | identifier PERIOD PERIOD identifier PERIOD identifier
                   | TIMES
                   | identifier PERIOD TIMES
                   | identifier PERIOD identifier PERIOD TIMES
                   | identifier PERIOD identifier PERIOD identifier PERIOD TIMES
                   | identifier PERIOD PERIOD identifier PERIOD TIMES
        """
        if len(p) == 2:
            last_sql = p[1].sql if isinstance(p[1], Node) else p[1]
            sql = last_sql
        elif len(p) == 4:
            last_sql = p[3].sql if isinstance(p[3], Node) else p[3]
            sql = '%s.%s' % (p[1].sql, last_sql)
        elif len(p) == 6:
            last_sql = p[5].sql if isinstance(p[5], Node) else p[5]
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, last_sql)
        elif len(p) == 8:
            last_sql = p[7].sql if isinstance(p[7], Node) else p[7]
            sql = '%s.%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql, last_sql)
        else:
            last_sql = p[6].sql if isinstance(p[6], Node) else p[6]
            sql = '%s..%s.%s' % (p[1].sql, p[4].sql, last_sql)
        p[0] = Node('column_ref', p, sql)

    def p_base_data_type(self, p):
        """
        base_data_type : NUMERIC
                       | NUMERIC data_type_length1
                       | NUMERIC data_type_length2
                       | DECIMAL
                       | DECIMAL data_type_length1
                       | DECIMAL data_type_length2
                       | INTEGER
                       | INT
                       | SMALLINT
                       | FLOAT
                       | REAL
                       | DOUBLE PRECISION
                       | LONG VARBINARY
                       | VARBINARY
                       | VARBINARY data_type_length1
                       | BINARY data_type_length1
                       | TIMESTAMP
                       | DATETIME
                       | TIME
                       | DATE
                       | CHAR
                       | CHAR data_type_length1
                       | NCHAR
                       | NCHAR data_type_length1
                       | NVARCHAR
                       | NVARCHAR data_type_length1
                       | LBRACKET NUMERIC RBRACKET
                       | LBRACKET NUMERIC RBRACKET data_type_length1
                       | LBRACKET NUMERIC RBRACKET data_type_length2
                       | LBRACKET DECIMAL RBRACKET
                       | LBRACKET DECIMAL RBRACKET data_type_length1
                       | LBRACKET DECIMAL RBRACKET data_type_length2
                       | LBRACKET INTEGER RBRACKET
                       | LBRACKET INT RBRACKET
                       | LBRACKET SMALLINT RBRACKET
                       | LBRACKET FLOAT RBRACKET
                       | LBRACKET REAL RBRACKET
                       | LBRACKET LONG VARBINARY
                       | LBRACKET VARBINARY RBRACKET
                       | LBRACKET VARBINARY RBRACKET data_type_length1
                       | LBRACKET BINARY RBRACKET data_type_length1
                       | LBRACKET TIMESTAMP RBRACKET
                       | LBRACKET DATETIME RBRACKET
                       | LBRACKET TIME RBRACKET
                       | LBRACKET DATE RBRACKET
                       | LBRACKET CHAR RBRACKET
                       | LBRACKET CHAR RBRACKET data_type_length1
                       | LBRACKET NCHAR RBRACKET
                       | LBRACKET NCHAR RBRACKET data_type_length1
                       | LBRACKET NVARCHAR RBRACKET
                       | LBRACKET NVARCHAR RBRACKET data_type_length1
        """
        if len(p) == 2:
            sql = p[1]
        elif len(p) == 3:
            if isinstance(p[2], Node):
                sql = '%s%s' % (p[1], p[2].sql)
            else:
                sql = '%s %s' % (p[1], p[2])
        elif len(p) == 4:
            sql = '[%s]' % (p[2],)
        else:
            sql = '[%s]%s' % (p[2], p[4].sql)
        p[0] = Node('base_data_type', p, sql)

    def p_data_type(self, p):
        """
        data_type : base_data_type
                  | CHARACTER
                  | VARCHAR
                  | VARCHAR data_type_length1
                  | CHARACTER data_type_length1
        """
        if len(p) == 2:
            sql = p[1].sql if isinstance(p[1], Node) else p[1]
        else:
            sql = '%s%s' % (p[1], p[2].sql)
        p[0] = Node('data_type', p, sql)

    def p_data_type_length1(self, p):
        """
        data_type_length1 : LPAREN NUMBER RPAREN
                          | LPAREN MAX RPAREN
        """
        sql = '(%s)' % (p[2],)
        p[0] = Node('data_type_length1', p, sql)

    def p_data_type_length2(self, p):
        """
        data_type_length2 : LPAREN NUMBER COMMA NUMBER RPAREN
        """
        sql = '(%s, %s)' % (p[2], p[4])
        p[0] = Node('data_type_length2', p, sql)

    def p_array_modifier(self, p):
        """
        array_modifier : ARRAY
                       | ARRAY LBRACKET NUMBER RBRACKET
        """
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '%s[%s]' % (p[1], p[3])
        p[0] = Node('array_modifier', p, sql)

    def p_data_type_ref(self, p):
        """
        data_type_ref : data_type_ref array_modifier
                      | data_type
                      | q_type_name
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('data_type_ref', p, sql)

    def p_column_data_type(self, p):
        """
        column_data_type : base_data_type
                         | CHARACTER
                         | VARCHAR
                         | VARCHAR LPAREN NUMBER RPAREN
                         | CHARACTER LPAREN NUMBER RPAREN
                         | q_type_name
                         | LONG q_type_name
                         | LONG XML
        """
        if len(p) == 2:
            sql = p[1].sql if isinstance(p[1], Node) else p[1]
        elif len(p) == 3:
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = '%s(%s)' % (p[1], p[3])
        p[0] = Node('column_data_type', p, sql)

    def p_column(self, p):
        """
        column : identifier
               | identifier PERIOD identifier PERIOD identifier PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s.%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql, p[7].sql)
        p[0] = Node('column', p, sql)

    def p_index(self, p):
        """
        index : identifier
        """
        sql = p[1].sql
        p[0] = Node('index', p, sql)

    def p_cursor(self, p):
        """
        cursor : identifier
        """
        sql = p[1].sql
        p[0] = Node('cursor', p, sql)

    def p_parameter(self, p):
        """
        parameter : QUESTION
                  | COLON ID
                  | AT ID
        """
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '%s%s' % (p[1], p[2])
        p[0] = Node('parameter', p, sql)

    def p_identifier(self, p):
        """
        identifier : LBRACKET ID RBRACKET
                   | ID
        """
        if len(p) == 2:
            sql = p[1]
        else:
            sql = '[%s]' % (p[2],)
        p[0] = Node('identifier', None, sql)

    def p_user(self, p):
        """
        user : identifier
        """
        sql = p[1].sql
        p[0] = Node('user', p, sql)

    def p_opt_log(self, p):
        """
        opt_log : STRING
                |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_log', p, sql)

    def p_comma_opt_log(self, p):
        """
        comma_opt_log : COMMA STRING
                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = ', %s' % (p[2], )
        p[0] = Node('comma_opt_log', p, sql)

    def p_admin_statement(self, p):
        """
        admin_statement : SHUTDOWN opt_log
                        | CHECKPOINT opt_log
                        | CHECKPOINT STRING STRING
                        | BACKUP STRING
                        | CHECK
                        | SYNC REPLICATION opt_log comma_opt_log
                        | DISCONNECT REPLICATION opt_log
                        | LOGX ON
                        | LOGX OFF
        """
        sql = ' '.join([i.sql if isinstance(i, Node) else i for i in p[1:]])
        p[0] = Node('admin_statement', p, sql)

    def p_user_aggregate_declaration(self, p):
        """
        user_aggregate_declaration : CREATE AGGREGATE new_table_name rout_parameter_list opt_return FROM new_proc_or_bif_name COMMA new_proc_or_bif_name COMMA new_proc_or_bif_name user_aggregate_merge_opt
        """
        sql = '%s %s %s %s %s %s, %s, %s %s' % (p[1], p[2], p[3].sql, p[4].sql, p[5], p[6].sql, p[8].sql, p[10].sql, p[11].sql)
        p[0] = Node('user_aggregate_declaration', p, sql)

    def p_user_aggregate_merge_opt(self, p):
        """
        user_aggregate_merge_opt : COMMA new_proc_or_bif_name
                                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = ', %s' % (p[2].sql,)
        p[0] = Node('user_aggregate_merge_opt', p, sql)

    def p_routine_declaration(self, p):
        """
        routine_declaration : CREATE routine_head new_table_name rout_parameter_list opt_return rout_alt_type AS compound_statement
                            | CREATE routine_head new_table_name rout_parameter_list opt_return rout_alt_type compound_statement
                            | ATTACH routine_head attach_q_table_name rout_parameter_list opt_return rout_alt_type opt_as FROM literal
                            | CREATE routine_head new_table_name rout_parameter_list opt_return rout_alt_type LANGUAGE external_language_name EXTERNAL NAME_L STRING opt_type_option_list
        """
        if len(p) == 9:
            sql = '%s %s %s %s %s %s\n%s\n%s' % (p[1], p[2].sql, p[3].sql, p[4].sql, p[5].sql, p[6].sql, p[7], p[8].sql)
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('routine_declaration', p, sql)

    def p_module_body_part(self, p):
        """
        module_body_part : routine_head identifier rout_parameter_list opt_return rout_alt_type compound_statement
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('module_body_part', p, sql)

    def p_module_body(self, p):
        """
        module_body : module_body_part SEMI
                    | module_body module_body_part SEMI
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('module_body', p, sql)

    def p_module_declaration(self, p):
        """
        module_declaration : CREATE MODULE new_table_name BEGIN module_body END
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('module_declaration', p, sql)

    def p_routine_head(self, p):
        """
        routine_head : FUNCTION
                     | PROCEDURE
        """
        sql = p[1]
        p[0] = Node('routine_head', p, sql)

    def p_opt_return(self, p):
        """
        opt_return : RETURNS data_type_ref
                   |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '\n%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_return', p, sql)

    def p_rout_parameter_list(self, p):
        """
        rout_parameter_list : LPAREN RPAREN
                            | LPAREN parameter_commalist RPAREN
        """
        if len(p) == 3:
            sql = '()'
        else:
            sql = '(%s)' % (p[2].sql)
        p[0] = Node('rout_parameter_list', p, sql)

    def p_parameter_commalist(self, p):
        """
        parameter_commalist : rout_parameter
                            | parameter_commalist COMMA rout_parameter
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('parameter_commalist', p, sql)

    def p_rout_parameter(self, p):
        """
        rout_parameter : parameter_mode column_ref data_type_ref rout_alt_type
                       | parameter_mode column_ref data_type_ref DEFAULT signed_literal rout_alt_type
                       | parameter_mode column_ref data_type_ref EQ signed_literal rout_alt_type
                       | parameter_mode parameter data_type_ref rout_alt_type
                       | parameter_mode parameter data_type_ref DEFAULT signed_literal rout_alt_type
                       | parameter_mode parameter data_type_ref EQ signed_literal rout_alt_type
                       | column_ref data_type_ref rout_alt_type
                       | column_ref data_type_ref DEFAULT signed_literal rout_alt_type
                       | column_ref data_type_ref EQ signed_literal rout_alt_type
                       | parameter data_type_ref rout_alt_type
                       | parameter data_type_ref DEFAULT signed_literal rout_alt_type
                       | parameter data_type_ref EQ signed_literal rout_alt_type
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('rout_parameter', p, sql)

    def p_parameter_mode(self, p):
        """
        parameter_mode : IN_L
                       | OUT_L
                       | INOUT_L
        """
        sql = p[1]
        p[0] = Node('parameter_mode', p, sql)

    def p_opt_parameter_mode(self, p):
        """
        opt_parameter_mode : parameter_mode
                           |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_parameter_mode', p, sql)

    def p_opt_soap_enc_mode(self, p):
        """
        opt_soap_enc_mode : __SOAP_DIME_ENC IN_L
                          | __SOAP_DIME_ENC OUT_L
                          | __SOAP_DIME_ENC INOUT_L
                          | __SOAP_ENC_MIME IN_L
                          | __SOAP_ENC_MIME OUT_L
                          | __SOAP_ENC_MIME INOUT_L
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('opt_soap_enc_mode', p, sql)

    def p_soap_kwd(self, p):
        """
        soap_kwd : __SOAP_TYPE
                 | __SOAP_HEADER
                 | __SOAP_FAULT
                 | __SOAP_DOC
                 | __SOAP_XML_TYPE
                 | __SOAP_DOCW
                 | __SOAP_HTTP
        """
        sql = p[1]
        p[0] = Node('soap_kwd', p, sql)

    def p_rout_alt_type(self, p):
        """
        rout_alt_type : soap_kwd STRING opt_soap_enc_mode
                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('rout_alt_type', p, sql)

    def p_routine_statement(self, p):
        """
        routine_statement : select_statement
                          | update_statement_positioned
                          | update_statement_searched
                          | insert_statement
                          | delete_statement_positioned
                          | delete_statement_searched
                          | close_statement
                          | fetch_statement
                          | open_statement
                          | rollback_statement
                          | commit_statement
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('routine_statement', p, sql)

    def p_compound_statement(self, p):
        """
        compound_statement : BEGIN statement_list END
        """
        sql = '\n%s\n    %s\n%s' % (p[1], common.set_indent(p[2].sql, ' ' * 4), p[3])
        p[0] = Node('compound_statement', p, sql)

    def p_statement_list(self, p):
        """
        statement_list : statement_in_cs
                       | statement_list statement_in_cs
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = '\n'.join(s_list)
        p[0] = Node('statement_list', p, sql)

    def p_statement_in_cs(self, p):
        """
        statement_in_cs : local_declaration SEMI
                        | compound_statement
                        | statement_in_cs_oper
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s;' % (p[1].sql,)
        p[0] = Node('statement_in_cs', p, sql)

    def p_statement_in_cs_oper(self, p):
        """
        statement_in_cs_oper : routine_statement SEMI
                             | control_statement
                             | identifier COLON statement_in_cs
                             | HTMLSTR
                             | comparison scalar_exp HTMLSTR
                             | DIVIDE scalar_exp HTMLSTR
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('statement_in_cs_oper', p, sql)

    def p_statement(self, p):
        """
        statement : compound_statement
                  | routine_statement SEMI
                  | control_statement
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('statement', p, sql)

    def p_local_declaration(self, p):
        """
        local_declaration : cursor_def
                          | variable_declaration
                          | handler_declaration
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('local_declaration', p, sql)

    def p_variable_declaration(self, p):
        """
        variable_declaration : DECLARE variable_list data_type_ref
        """
        sql = '%s %s %s' % (p[1], p[2].sql, p[3].sql)
        p[0] = Node('variable_declaration', p, sql)

    def p_variable_list(self, p):
        """
        variable_list : identifier
                      | parameter
                      | variable_list COMMA identifier
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('variable_list', p, sql)

    def p_condition(self, p):
        """
        condition : NOT FOUND
                  | SQLSTATE STRING
                  | SQLSTATE VALUE STRING
                  | SQLEXCEPTION
                  | SQLWARNING
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('condition', p, sql)

    def p_handler_declaration(self, p):
        """
        handler_declaration : WHENEVER condition GOTO identifier
                            | WHENEVER condition GO TO identifier
                            | WHENEVER condition DEFAULT
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('handler_declaration', p, sql)

    def p_control_statement(self, p):
        """
        control_statement : call_statement SEMI
                          | static_method_invocation SEMI
                          | set_statement SEMI
                          | set_statement
                          | RESIGNAL SEMI
                          | RESIGNAL scalar_exp SEMI
                          | return_statement SEMI
                          | return_statement
                          | assignment_statement SEMI
                          | if_statement
                          | goto_statement SEMI
                          | for_statement
                          | while_statement
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('control_statement', p, sql)

    def p_assignment_statement(self, p):
        """
        assignment_statement : column_ref EQ scalar_exp
                             | parameter EQ scalar_exp
                             | column_ref LBRACKET scalar_exp RBRACKET EQ scalar_exp
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('assignment_statement', p, sql)

    def p_if_statement(self, p):
        """
        if_statement : IF search_condition statement opt_else
        """
        sql = '%s %s %s %s' % (p[1], p[2].sql, p[3].sql, p[4].sql)
        if p.stack[-1] and p.stack[-1].type != 'ELSE':
            sql = '\n' + sql
        p[0] = Node('if_statement', p, sql)

    def p_opt_else(self, p):
        """
        opt_else : ELSE statement
                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '\n%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_else', p, sql)

    def p_call_statement(self, p):
        """
        call_statement : CALL function_name LPAREN opt_arg_commalist RPAREN
                       | function_call
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('call_statement', p, sql)

    def p_set_statement(self, p):
        """
        set_statement : SET parameter EQ scalar_exp
                      | SET identifier ON
                      | SET identifier OFF
        """
        s_list = [str(i.sql) if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('set_statement', p, sql)

    def p_goto_statement(self, p):
        """
        goto_statement : GOTO identifier
                       | GO TO identifier
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('goto_statement', p, sql)

    def p_return_statement(self, p):
        """
        return_statement : RETURN scalar_exp
                         | RETURN
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('return_statement', p, '\n\n' + sql)

    def p_while_statement(self, p):
        """
        while_statement : WHILE search_condition statement
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('while_statement', p, sql)

    def p_for_init_statement(self, p):
        """
        for_init_statement : assignment_statement
                           | variable_declaration
                           | call_statement
                           | static_method_invocation
        """
        sql = p[1].sql
        p[0] = Node('for_init_statement', p, sql)

    def p_for_init_statement_list(self, p):
        """
        for_init_statement_list : for_init_statement
                                | for_init_statement_list COMMA for_init_statement
                                |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('for_init_statement_list', p, sql)

    def p_for_inc_statement(self, p):
        """
        for_inc_statement : assignment_statement
                          | call_statement
                          | static_method_invocation
        """
        sql = p[1].sql
        p[0] = Node('for_inc_statement', p, sql)

    def p_for_inc_statement_list(self, p):
        """
        for_inc_statement_list : for_inc_statement
                               | for_inc_statement_list COMMA for_inc_statement
                               |
        """
        if len(p) == 1:
            sql = ''
        elif len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('for_inc_statement_list', p, sql)

    def p_for_opt_search_cond(self, p):
        """
        for_opt_search_cond : search_condition
                            |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('for_opt_search_cond', p, sql)

    def p_for_statement(self, p):
        """
        for_statement : FOR query_exp DO statement
                      | FOR LPAREN for_init_statement_list SEMI for_opt_search_cond SEMI for_inc_statement_list RPAREN statement
                      | FOREACH LPAREN data_type_ref identifier IN_L scalar_exp RPAREN DO statement
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('for_statement', p, sql)

    def p_trigger_def(self, p):
        """
        trigger_def : CREATE TRIGGER identifier action_time event ON q_table_name opt_order opt_old_ref trig_action
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('trigger_def', p, sql)

    def p_opt_order(self, p):
        """
        opt_order : ORDER NUMBER
                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_order', p, sql)

    def p_trig_action(self, p):
        """
        trig_action : compound_statement
        """
        sql = p[1].sql
        p[0] = Node('trig_action', p, sql)

    def p_action_time(self, p):
        """
        action_time : BEFORE
                    | AFTER
                    | INSTEAD OF
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('action_time', p, sql)

    def p_event(self, p):
        """
        event : INSERT
              | UPDATE opt_column_commalist
              | DELETE
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('event', p, sql)

    def p_opt_old_ref(self, p):
        """
        opt_old_ref : REFERENCING old_commalist
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_old_ref', p, sql)

    def p_old_commalist(self, p):
        """
        old_commalist : old_alias
                      | old_commalist COMMA old_alias
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('old_commalist', p, sql)

    def p_old_alias(self, p):
        """
        old_alias : OLD AS identifier
                  | NEW AS identifier
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('old_alias', p, sql)

    def p_drop_trigger(self, p):
        """
        drop_trigger : DROP TRIGGER q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_trigger', p, sql)

    def p_drop_proc(self, p):
        """
        drop_proc : DROP AGGREGATE q_table_name
                  | DROP routine_head q_table_name
                  | DROP MODULE q_table_name
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('drop_proc', p, sql)

    def p_opt_element(self, p):
        """
        opt_element : AS identifier
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_element', p, sql)

    def p_xml_col(self, p):
        """
        xml_col : column_ref
                | scalar_exp AS identifier
                | scalar_exp IN_L identifier
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('xml_col', p, sql)

    def p_xml_col_list(self, p):
        """
        xml_col_list : xml_col
                     | xml_col_list COMMA xml_col
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('xml_col_list', p, sql)

    def p_opt_xml_col_list(self, p):
        """
        opt_xml_col_list : LPAREN xml_col_list RPAREN
        """
        sql = '(%s)' % (p[2].sql,)
        p[0] = Node('opt_xml_col_list', p, sql)

    def p_opt_pk(self, p):
        """
        opt_pk : PRIMARY KEY LPAREN column_commalist RPAREN
               |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s (%s)' % (p[1], p[2], p[4].sql)
        p[0] = Node('opt_pk', p, sql)

    def p_opt_join(self, p):
        """
        opt_join : ON LPAREN search_condition RPAREN
                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s (%s)' % (p[1], p[3].sql)
        p[0] = Node('opt_join', p, sql)

    def p_xml_join_elt(self, p):
        """
        xml_join_elt : q_table_name identifier opt_element opt_xml_col_list opt_join opt_pk opt_xml_child
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('xml_join_elt', p, sql)

    def p_opt_xml_child(self, p):
        """
        opt_xml_child : BEGIN xml_join_list END
                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s %s' % (p[1], p[2].sql, p[3])
        p[0] = Node('opt_xml_child', p, sql)

    def p_top_xml_child(self, p):
        """
        top_xml_child : query_spec
                      | BEGIN xml_join_list END
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('top_xml_child', p, sql)

    def p_xml_join_list(self, p):
        """
        xml_join_list : xml_join_elt
                      | xml_join_list COMMA xml_join_elt
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('xml_join_list', p, sql)

    def p_opt_persist(self, p):
        """
        opt_persist : PERSISTENT
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('opt_persist', p, sql)

    def p_opt_interval(self, p):
        """
        opt_interval : INTERVAL NUMBER
                     |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_interval', p, sql)

    def p_opt_metas(self, p):
        """
        opt_metas : DTD INTERNAL
                  | DTD EXTERNAL
                  | DTD STRING
                  | SCHEMA EXTERNAL
                  | SCHEMA STRING
                  |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_metas', p, sql)

    def p_opt_publish(self, p):
        """
        opt_publish : PUBLIC STRING identifier STRING opt_persist opt_interval opt_metas
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('opt_publish', p, sql)

    def p_xml_view(self, p):
        """
        xml_view : CREATE XML VIEW new_table_name AS top_xml_child opt_publish
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('xml_view', p, sql)

    def p_drop_xml_view(self, p):
        """
        drop_xml_view : DROP XML VIEW q_table_name
        """
        sql = '%s %s %s %s' % (p[1], p[2], p[3], p[4].sql)
        p[0] = Node('drop_xml_view', p, sql)

    def p_string_concatenation_operator(self, p):
        """
        string_concatenation_operator : scalar_exp STRING_CONCAT_OPERATOR scalar_exp
        """
        sql = '%s %s %s' % (p[1].sql, p[2], p[3].sql)
        p[0] = Node('string_concatenation_operator', p, sql)

    def p_q_type_name(self, p):
        """
        q_type_name : identifier
                    | identifier PERIOD identifier
                    | identifier PERIOD identifier PERIOD identifier
                    | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('q_type_name', p, sql)

    def p_q_old_type_name(self, p):
        """
        q_old_type_name : identifier
                        | identifier PERIOD identifier
                        | identifier PERIOD identifier PERIOD identifier
                        | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('q_old_type_name', p, sql)

    def p_new_type_name(self, p):
        """
        new_type_name : identifier
                      | identifier PERIOD identifier
                      | identifier PERIOD identifier PERIOD identifier
                      | identifier PERIOD PERIOD identifier
        """
        if len(p) == 2:
            sql = p[1].sql
        elif len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 5:
            sql = '%s..%s' % (p[1].sql, p[4].sql)
        else:
            sql = '%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql)
        p[0] = Node('new_type_name', p, sql)

    def p_user_defined_type(self, p):
        """
        user_defined_type : CREATE TYPE new_type_name opt_subtype_clause opt_external_and_language_clause opt_as_type_representation opt_type_option_list opt_method_specification_list
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('user_defined_type', p, sql)

    def p_user_defined_type_drop(self, p):
        """
        user_defined_type_drop : DROP TYPE q_old_type_name opt_drop_behavior
        """
        sql = '%s %s %s %s' % (p[1], p[2], p[3].sql, p[4].sql)
        p[0] = Node('user_defined_type_drop', p, sql)

    def p_opt_external_and_language_clause(self, p):
        """
        opt_external_and_language_clause : LANGUAGE language_name EXTERNAL NAME_L STRING
                                         | EXTERNAL NAME_L STRING LANGUAGE language_name
                                         | LANGUAGE language_name
                                         |
        """
        if len(p) == 1:
            sql = ''
        else:
            s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
            sql = ' '.join(s_list)
        p[0] = Node('opt_external_and_language_clause', p, sql)

    def p_opt_subtype_clause(self, p):
        """
        opt_subtype_clause : UNDER q_type_name
                           |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_subtype_clause', p, sql)

    def p_opt_as_type_representation(self, p):
        """
        opt_as_type_representation : AS type_representation
                                   |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_as_type_representation', p, sql)

    def p_type_representation(self, p):
        """
        type_representation : LPAREN type_member_list RPAREN
        """
        sql = '(%s)' % (p[2].sql,)
        p[0] = Node('type_representation', p, sql)

    def p_type_member_list(self, p):
        """
        type_member_list : type_member
                         | type_member_list COMMA type_member
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s, %s' % (p[1].sql, p[3].sql)
        p[0] = Node('type_member_list', p, sql)

    def p_opt_external_clause(self, p):
        """
        opt_external_clause : EXTERNAL NAME_L STRING
                            | EXTERNAL NAME_L STRING EXTERNAL TYPE STRING
                            | EXTERNAL TYPE STRING
                            |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('opt_external_clause', p, sql)

    def p_opt_soap_clause(self, p):
        """
        opt_soap_clause : __SOAP_NAME STRING
                        | __SOAP_TYPE STRING
                        | __SOAP_TYPE STRING __SOAP_NAME STRING
                        | __SOAP_NAME STRING __SOAP_TYPE STRING
                        |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('opt_soap_clause', p, sql)

    def p_opt_external_type(self, p):
        """
        opt_external_type : EXTERNAL TYPE STRING
                          |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_external_type', p, sql)

    def p_type_member(self, p):
        """
        type_member : identifier data_type_ref opt_reference_scope_check opt_default_clause opt_collate_exp opt_external_clause opt_soap_clause
        """
        s_list = [i.sql for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('type_member', p, sql)

    def p_opt_reference_scope_check(self, p):
        """
        opt_reference_scope_check : REFERENCES ARE CHECKED opt_on_delete_referential_rule
                                  | REFERENCES ARE NOT CHECKED
                                  |
        """
        if len(p) == 1:
            sql = ''
        elif isinstance(p[4], Node):
            sql = '%s %s %s %s' % (p[1], p[2], p[3], p[4].sql)
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('opt_reference_scope_check', p, sql)

    def p_opt_default_clause(self, p):
        """
        opt_default_clause : DEFAULT signed_literal
                           |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_default_clause', p, sql)

    def p_opt_type_option_list(self, p):
        """
        opt_type_option_list : type_option_list
                             |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_type_option_list', p, sql)

    def p_type_option_list(self, p):
        """
        type_option_list : type_option
                         | type_option_list type_option
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('type_option_list', p, sql)

    def p_type_option(self, p):
        """
        type_option : FINAL_L
                    | NOT FINAL_L
                    | REF USING data_type_ref
                    | REF FROM LPAREN column_commalist RPAREN
                    | REF IS SYSTEM GENERATED
                    | CAST LPAREN SOURCE AS REF RPAREN WITH identifier
                    | CAST LPAREN REF AS SOURCE RPAREN WITH identifier
                    | SELF_L AS REF
                    | TEMPORARY
                    | UNRESTRICTED
                    | __SOAP_TYPE STRING
        """
        if len(p) == 4 and isinstance(p[3], Node):
            sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        elif len(p) == 6 and isinstance(p[4], Node):
            sql = '%s %s(%s)' % (p[1], p[2], p[4].sql)
        elif len(p) == 9:
            sql = '%s(%s %s %s) %s %s' % (p[1], p[3], p[4], p[5], p[7], p[8].sql)
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('type_option', p, sql)

    def p_opt_method_specification_list(self, p):
        """
        opt_method_specification_list : method_specification_list
                                      |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_method_specification_list', p, sql)

    def p_method_specification_list(self, p):
        """
        method_specification_list : method_specification
                                  | method_specification_list COMMA method_specification
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        p[0] = Node('method_specification_list', p, sql)

    def p_method_type(self, p):
        """
        method_type : STATIC_L
                    | INSTANCE_L
                    |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1]
        p[0] = Node('method_type', p, sql)

    def p_decl_parameter_list(self, p):
        """
        decl_parameter_list : LPAREN RPAREN
                            | LPAREN decl_parameter_commalist RPAREN
        """
        if len(p) == 3:
            sql = '()'
        else:
            sql = '(%s)' % (p[2].sql, )
        p[0] = Node('decl_parameter_list', p, sql)

    def p_decl_parameter_commalist(self, p):
        """
        decl_parameter_commalist : decl_parameter
                                 | decl_parameter_commalist COMMA decl_parameter
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        p[0] = Node('decl_parameter_commalist', p, sql)

    def p_decl_parameter(self, p):
        """
        decl_parameter : opt_parameter_mode column_ref data_type_ref opt_external_type
        """
        sql = '%s %s %s %s' % (p[1].sql, p[2].sql, p[3].sql, p[4].sql)
        p[0] = Node('decl_parameter', p, sql)

    def p_partial_method_specification(self, p):
        """
        partial_method_specification : method_type METHOD method_identifier decl_parameter_list RETURNS data_type_ref opt_specific_method_name
                                     | CONSTRUCTOR METHOD method_identifier decl_parameter_list opt_specific_method_name
        """
        if len(p) == 6:
            sql = '%s %s %s %s %s' % (p[1], p[2], p[3].sql, p[4].sql, p[5].sql)
        else:
            sql = '%s %s %s %s %s %s %s' % (p[1].sql, p[2], p[3].sql, p[4].sql, p[5], p[6].sql, p[7].sql)
        p[0] = Node('partial_method_specification', p, sql)

    def p_method_specification(self, p):
        """
        method_specification : partial_method_specification opt_method_characteristics
                             | OVERRIDING partial_method_specification
        """
        s_list = [i.sql if isinstance(i, Node) else i for i in p[1:]]
        sql = ' '.join(s_list)
        p[0] = Node('method_specification', p, sql)

    def p_opt_specific_method_name(self, p):
        """
        opt_specific_method_name : SPECIFIC new_table_name
                                 |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_specific_method_name', p, sql)

    def p_opt_method_characteristics(self, p):
        """
        opt_method_characteristics : method_characteristics
                                   |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = p[1].sql
        p[0] = Node('opt_method_characteristics', p, sql)

    def p_method_characteristics(self, p):
        """
        method_characteristics : method_characteristic
                               | method_characteristics method_characteristic
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s %s' % (p[1].sql, p[2].sql)
        p[0] = Node('method_characteristics', p, sql)

    def p_method_characteristic(self, p):
        """
        method_characteristic : LANGUAGE language_name
                              | PARAMETER STYLE SQL_L
                              | PARAMETER STYLE GENERAL
                              | DETERMINISTIC
                              | NOT DETERMINISTIC
                              | NO SQL_L
                              | CONTAINS SQL_L
                              | READS SQL_L DATA
                              | MODIFIES SQL_L DATA
                              | RETURNS NULLX ON NULLX INPUT
                              | CALLED ON NULLX INPUT
                              | EXTERNAL NAME_L STRING
                              | EXTERNAL VARIABLE NAME_L STRING
                              | EXTERNAL TYPE STRING
        """
        if len(p) == 3 and isinstance(p[2], Node):
            sql = '%s %s' % (p[1], p[2].sql)
        else:
            sql = ' '.join(p[1:])
        p[0] = Node('method_characteristic', p, sql)

    def p_external_language_name(self, p):
        """
        external_language_name : ADA
                               | COBOL
                               | FORTRAN
                               | MUMPS
                               | PASCAL_L
                               | PLI
                               | JAVA
                               | CLR
        """
        sql = p[1]
        p[0] = Node('external_language_name', p, sql)

    def p_language_name(self, p):
        """
        language_name : external_language_name
                      | SQL_L
        """
        if isinstance(p[1], Node):
            sql = p[1].sql
        else:
            sql = p[1]
        p[0] = Node('language_name', p, sql)

    def p_opt_constructor_return(self, p):
        """
        opt_constructor_return : RETURNS new_type_name
                               |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2].sql)
        p[0] = Node('opt_constructor_return', p, sql)

    def p_method_declaration(self, p):
        """
        method_declaration : CREATE method_type METHOD method_identifier rout_parameter_list opt_return rout_alt_type FOR q_type_name compound_statement
                           | CREATE CONSTRUCTOR METHOD q_table_name rout_parameter_list opt_constructor_return FOR q_type_name compound_statement
        """
        if len(p) == 10:
            sql = '%s %s %s %s %s %s %s %s' % (p[1], p[2], p[3], p[4].sql, p[5].sql, p[6].sql, p[7], p[8].sql, p[9].sql)
        else:
            sql = '%s %s %s %s %s %s %s %s' % (p[1], p[2].sql, p[3], p[4].sql, p[5].sql, p[6].sql, p[7].sql, p[8], p[9].sql, p[10].sql)
        p[0] = Node('method_declaration', p, sql)

    def p_static_method_invocation(self, p):
        """
        static_method_invocation : q_type_name DOUBLE_COLON method_identifier LPAREN opt_arg_commalist RPAREN
        """
        sql = '%s %s %s(%s)' % (p[1].sql, p[2], p[3].sql, p[5].sql)
        p[0] = Node('static_method_invocation', p, sql)

    def p_identifier_chain(self, p):
        """
        identifier_chain : identifier PERIOD identifier PERIOD identifier PERIOD method_identifier
                         | identifier PERIOD PERIOD identifier PERIOD method_identifier
                         | identifier PERIOD identifier_chain
        """
        if len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 7:
            sql = '%s..%s.%s' % (p[1].sql, p[4].sql, p[6].sql)
        else:
            sql = '%s.%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql, p[7].sql)
        p[0] = Node('identifier_chain', p, sql)

    def p_identifier_chain_method(self, p):
        """
        identifier_chain_method : identifier PERIOD identifier PERIOD identifier PERIOD identifier PERIOD method_identifier
                                | identifier PERIOD PERIOD identifier PERIOD identifier PERIOD method_identifier
                                | identifier PERIOD identifier_chain_method
        """
        if len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        elif len(p) == 9:
            sql = '%s..%s.%s.%s' % (p[1].sql, p[4].sql, p[6].sql, p[8].sql)
        else:
            sql = '%s.%s.%s.%s.%s' % (p[1].sql, p[3].sql, p[5].sql, p[7].sql, p[9].sql)
        p[0] = Node('identifier_chain_method', p, sql)

    def p_method_invocation(self, p):
        """
        method_invocation : scalar_exp_no_col_ref_no_mem_obs_chain PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
                          | identifier_chain_method LPAREN opt_arg_commalist RPAREN
                          | LPAREN scalar_exp_no_col_ref AS q_type_name RPAREN PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
                          | LPAREN column_ref AS q_type_name RPAREN PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
        """
        if len(p) == 5:
            sql = '%s(%s)' % (p[1].sql, p[3].sql)
        elif len(p) == 7:
            sql = '%s.%s (%s)' % (p[1].sql, p[3].sql, p[5].sql)
        else:
            sql = '(%s %s %s).%s(%s)' % (p[2].sql, p[3], p[4].sql, p[7].sql, p[9].sql)
        p[0] = Node('method_invocation', p, sql)

    def p_top_level_method_invocation(self, p):
        """
        top_level_method_invocation : METHOD CALL scalar_exp_no_col_ref_no_mem_obs_chain PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
                                    | METHOD CALL identifier_chain_method LPAREN opt_arg_commalist RPAREN
                                    | METHOD CALL LPAREN scalar_exp_no_col_ref AS q_type_name RPAREN PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
                                    | METHOD CALL LPAREN column_ref AS q_type_name RPAREN PERIOD method_identifier LPAREN opt_arg_commalist RPAREN
        """
        if len(p) == 7:
            sql = '%s %s %s(%s)' % (p[1], p[2], p[3].sql, p[5].sql)
        elif len(p) == 9:
            sql = '%s %s %s.%s(%s)' % (p[1], p[2], p[3].sql, p[5].sql, p[7].sql)
        else:
            sql = '%s %s (%s %s %s).%s (%s)' % (p[1], p[2], p[4].sql, p[5], p[6].sql, p[9].sql, p[11].sql)
        p[0] = Node('top_level_method_invocation', p, sql)

    def p_member_observer(self, p):
        """
        member_observer : member_observer_no_id_chain
                        | identifier PERIOD identifier_chain
        """
        if len(p) == 2:
            sql = p[1].sql
        else:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        p[0] = Node('member_observer', p, sql)

    def p_row_number(self, p):
        """
        row_number : ROW_NUMBER LPAREN RPAREN OVER LPAREN ORDER BY ordering_spec_commalist RPAREN
        """
        sql = '%s() %s(%s %s %s)' % (p[1], p[4], p[6], p[7], p[8].sql)
        p[0] = Node('row_number', p, sql)

    def p_member_observer_no_id_chain(self, p):
        """
        member_observer_no_id_chain : scalar_exp_no_col_ref_no_mem_obs_chain PERIOD method_identifier
                                    | LPAREN scalar_exp_no_col_ref AS q_type_name RPAREN PERIOD method_identifier
                                    | LPAREN column_ref AS q_type_name RPAREN PERIOD method_identifier
        """
        if len(p) == 4:
            sql = '%s.%s' % (p[1].sql, p[3].sql)
        else:
            sql = '(%s %s %s).%s' % (p[2].sql, p[3], p[4].sql, p[7].sql)
        p[0] = Node('member_observer_no_id_chain', p, sql)

    def p_method_identifier(self, p):
        """
        method_identifier : identifier
                          | EXTRACT
        """
        if isinstance(p[1], Node):
            sql = p[1].sql
        else:
            sql = p[1]
        p[0] = Node('method_identifier', p, sql)

    def p_new_invocation(self, p):
        """
        new_invocation : NEW q_type_name LPAREN opt_arg_commalist RPAREN
        """
        sql = '%s %s (%s)' % (p[1], p[2].sql, p[4].sql)
        p[0] = Node('new_invocation', p, sql)

    def p_user_defined_type_alter(self, p):
        """
        user_defined_type_alter : ALTER TYPE q_type_name alter_type_action
        """
        sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('user_defined_type_alter', p, sql)

    def p_alter_type_action(self, p):
        """
        alter_type_action : ADD ATTRIBUTE type_member
                          | DROP ATTRIBUTE identifier opt_drop_behavior
                          | ADD method_specification
                          | DROP partial_method_specification opt_drop_behavior
        """
        if p[1].upper() == "ADD":
            if len(p) == 3:
                sql = '%s %s' % (p[1], p[2].sql)
            else:
                sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        else:
            if len(p) == 4:
                sql = '%s %s %s' % (p[1], p[2].sql, p[3].sql)
            else:
                sql = '%s %s %s %s' % (p[1], p[2], p[3].sql, p[4].sql)
        p[0] = Node('alter_type_action', p, sql)

    def p_opt_with_permission_set(self, p):
        """
        opt_with_permission_set : WITH PERMISSION_SET comparison SAFE_L
                                | WITH PERMISSION_SET comparison UNRESTRICTED
                                |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s %s %s' % (p[1], p[2], p[3].sql, p[4])
        p[0] = Node('opt_with_permission_set', p, sql)

    def p_opt_with_autoregister(self, p):
        """
        opt_with_autoregister : WITH AUTOREGISTER_L
                              |
        """
        if len(p) == 1:
            sql = ''
        else:
            sql = '%s %s' % (p[1], p[2])
        p[0] = Node('opt_with_autoregister', p, sql)

    def p_create_library(self, p):
        """
        create_library : CREATE LIBRARY_L q_table_name AS scalar_exp opt_with_permission_set opt_with_autoregister
        """
        sql = '%s %s %s %s %s %s %s' % (p[1], p[2], p[3].sql, p[4], p[5].sql, p[6].sql, p[7].sql)
        p[0] = Node('create_library', p, sql)

    def p_create_assembly(self, p):
        """
        create_assembly : CREATE ASSEMBLY_L q_table_name FROM scalar_exp opt_with_permission_set opt_with_autoregister
        """
        sql = '%s %s %s %s %s %s %s' % (p[1], p[2], p[3].sql, p[4], p[5].sql, p[6].sql, p[7].sql)
        p[0] = Node('create_assembly', p, sql)

    def p_drop_library(self, p):
        """
        drop_library : DROP LIBRARY_L q_table_name
        """
        sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('drop_library', p, sql)

    def p_drop_assembly(self, p):
        """
        drop_assembly : DROP ASSEMBLY_L q_table_name
        """
        sql = '%s %s %s' % (p[1], p[2], p[3].sql)
        p[0] = Node('drop_assembly', p, sql)

    def p_comparison(self, p):
        """
        comparison : GE
                   | LE
                   | NE
                   | GT
                   | LT
                   | EQ
        """
        sql = p[1]
        p[0] = Node('comparison', p, sql)

    def find_column(self, input, lexpos):
        last_cr = input.rfind('\n', 0, lexpos)
        if last_cr < 0:
            last_cr = 0
        column = lexpos - last_cr
        return column

    def p_error(self, p):
        if p:
            column = self.find_column(p.lexer.lexdata, p.lexpos)
            message = u"Error: '%s' 付近に不適切な構文があります。%d 行, %d 文字!" % (p.value, p.lineno, column)
        else:
            message = u"不適切な構文があります。"
        self.errors.append(message)

    def build(self, **kwargs):
        self.parser = yacc.yacc(module=self, **kwargs)
        return self.parser

    def test(self, p, mode):
        if mode == "1":
            import os
            path = os.path.dirname(os.path.abspath(__file__))
            for root, dirs, files in os.walk(os.path.join(path, 'test')):
                for f in files:
                    if f[-4:] == '.sql':
                        text = open(os.path.join(root, f), 'r').read()
                        lexer = SqlLexer().build()
                        result = self.parser.parse(text, lexer=lexer)
                        if result:
                            print "----------------------------------------------------------------"
                            print result.to_sql()
                        else:
                            print '============  ERROR  ============='
                            print 'file: ' + os.path.join(root, f)
                            print text
                            print '\n'.join(p.errors)
                            return
        else:
            while True:
                text = raw_input("sql> ").strip()
                if text.lower() in ("quit", "exit"):
                    break
                if text:
                    del p.errors[:]
                    lexer = SqlLexer().build()
                    result = self.parser.parse(text, lexer=lexer)
                    if result:
                        print result.to_sql()
                    else:
                        print 'Parsing Error!'
                        print '\n'.join(p.errors)


def unittest_lexer():
    l = SqlLexer()
    l.build()
    l.test()


def unittest_parser(mode):
    p = SqlParser()
    p.build()
    p.test(p, mode)

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) == 2 else None 
    #unittest_lexer(mode)
    unittest_parser(mode)
