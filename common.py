# coding: utf-8


def get_tab_space_count():
    return 4


def set_indent(sql, indent):
    if indent and sql.find('\n') >= 0:
        sqls = []
        for sub_sql in sql.split('\n'):
            if sqls:
                sqls.append('\n%s%s' % (indent, sub_sql))
            else:
                sqls.append(sub_sql)
        return ''.join(sqls)
    else:
        return sql

