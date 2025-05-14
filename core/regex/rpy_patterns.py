"""
Renpy文件的正则表达式模式集合，专用于提取指定的三种属性
"""

# 通用字符串匹配模式
# 匹配单引号、双引号和三引号字符串
STRING_PATTERN = r'(?:"(?:\\"|[^"])*"|\'(?:\\\'|[^\'])*\'|"""(?:[^"]|"(?!""))*"""|\'\'\'(?:[^\']|\'(?!\'\'))*\'\'\')'

# 匹配属性赋值模式
# 适用于description、purchase_notification、unlock_notification等
# 格式: 属性名=值，值可以是字符串，包括f-string
# 例如: description="这是描述"
def create_property_pattern(property_name):
    """创建用于匹配特定属性的正则表达式模式"""
    return rf'{property_name}\s*=\s*((?:f)?{STRING_PATTERN})'

# 预定义三个目标属性模式
DESCRIPTION_PATTERN = create_property_pattern('description')
PURCHASE_NOTIFICATION_PATTERN = create_property_pattern('purchase_notification')
UNLOCK_NOTIFICATION_PATTERN = create_property_pattern('unlock_notification')

# 多行注释模式（用于排除注释中的内容）
MULTILINE_COMMENT_PATTERN = r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''

# 单行注释模式
SINGLE_LINE_COMMENT_PATTERN = r'#.*?$'
