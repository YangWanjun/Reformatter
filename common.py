# coding: utf-8

import os

from PyQt4.QtCore import QVariant


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


def get_root_path():
    return os.path.abspath(os.path.dirname(__file__))


def get_db_type(t):
    qt_type_list = [QVariant.Invalid,
                    QVariant.BitArray,
                    QVariant.Bitmap,
                    QVariant.Bool,
                    QVariant.Brush,
                    QVariant.ByteArray,
                    QVariant.Char,
                    QVariant.Color,
                    QVariant.Cursor,
                    QVariant.Date,
                    QVariant.DateTime,
                    QVariant.Double,
                    QVariant.EasingCurve,
                    QVariant.Font,
                    QVariant.Hash,
                    QVariant.Icon,
                    QVariant.Image,
                    QVariant.Int,
                    QVariant.KeySequence,
                    QVariant.Line,
                    QVariant.LineF,
                    QVariant.List,
                    QVariant.Locale,
                    QVariant.LongLong,
                    QVariant.Map,
                    QVariant.Matrix,
                    QVariant.Transform,
                    QVariant.Matrix4x4,
                    QVariant.Palette,
                    QVariant.Pen,
                    QVariant.Pixmap,
                    QVariant.Point,
                    QVariant.PointF,
                    QVariant.Polygon,
                    QVariant.Quaternion,
                    QVariant.Rect,
                    QVariant.RectF,
                    QVariant.RegExp,
                    QVariant.Region,
                    QVariant.Size,
                    QVariant.SizeF,
                    QVariant.SizePolicy,
                    QVariant.String,
                    QVariant.StringList,
                    QVariant.TextFormat,
                    QVariant.TextLength,
                    QVariant.Time,
                    QVariant.UInt,
                    QVariant.ULongLong,
                    QVariant.Url,
                    QVariant.Vector2D,
                    QVariant.Vector3D,
                    QVariant.Vector4D,
                    QVariant.UserType,
                    ]
    str_type_list = ['Invalid',
                     'BitArray',
                     'Bitmap',
                     'Bool',
                     'Brush',
                     'ByteArray',
                     'Char',
                     'Color',
                     'Cursor',
                     'Date',
                     'DateTime',
                     'Double',
                     'EasingCurve',
                     'Font',
                     'Hash',
                     'Icon',
                     'Image',
                     'Int',
                     'KeySequence',
                     'Line',
                     'LineF',
                     'List',
                     'Locale',
                     'LongLong',
                     'Map',
                     'Matrix',
                     'Transform',
                     'Matrix4x4',
                     'Palette',
                     'Pen',
                     'Pixmap',
                     'Point',
                     'PointF',
                     'Polygon',
                     'Quaternion',
                     'Rect',
                     'RectF',
                     'RegExp',
                     'Region',
                     'Size',
                     'SizeF',
                     'SizePolicy',
                     'String',
                     'StringList',
                     'TextFormat',
                     'TextLength',
                     'Time',
                     'UInt',
                     'ULongLong',
                     'Url',
                     'Vector2D',
                     'Vector3D',
                     'Vector4D',
                     'UserType',
                     ]
    if len(qt_type_list) == len(str_type_list):
        for i, item in enumerate(qt_type_list):
            if t == item:
                return str_type_list[i]
    return "Invalid"
