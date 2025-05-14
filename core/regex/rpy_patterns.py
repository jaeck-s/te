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

# 新增三种提取模式的正则表达式
# 匹配 title_text= 模式
TITLE_TEXT_PATTERN = r'title_text\s*=\s*((?:f)?{})'.format(STRING_PATTERN)

# 匹配 description_text= 模式
DESCRIPTION_TEXT_PATTERN = r'description_text\s*=\s*((?:f)?{})'.format(STRING_PATTERN)

# 匹配 renpy.notify 函数调用
RENPY_NOTIFY_PATTERN = r'renpy\.notify\s*\(\s*((?:f)?{})\s*\)'.format(STRING_PATTERN)

# 多行注释模式（用于排除注释中的内容）
MULTILINE_COMMENT_PATTERN = r'"""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\''

# 单行注释模式
SINGLE_LINE_COMMENT_PATTERN = r'#.*?$'
