"""
用于提取RPY文件中的特定属性值：description, purchase_notification, unlock_notification
"""
import re
from typing import List, Tuple
from ..regex.rpy_patterns import (
    DESCRIPTION_PATTERN, 
    PURCHASE_NOTIFICATION_PATTERN, 
    UNLOCK_NOTIFICATION_PATTERN,
    MULTILINE_COMMENT_PATTERN,
    SINGLE_LINE_COMMENT_PATTERN
)

def extract_property_values(content: str, 
                           filepath: str, 
                           pattern: str,
                           property_name: str) -> List[Tuple[int, str]]:
    """
    通用属性值提取函数
    
    Args:
        content: 文件内容
        filepath: 文件路径
        pattern: 正则表达式模式
        property_name: 属性名称（用于日志）
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    entries = []
    
    # 获取所有注释的范围，以便排除
    comment_ranges = []
    
    # 匹配多行注释
    for m in re.finditer(MULTILINE_COMMENT_PATTERN, content, re.MULTILINE):
        comment_ranges.append((m.start(), m.end()))
    
    # 匹配单行注释
    for m in re.finditer(SINGLE_LINE_COMMENT_PATTERN, content, re.MULTILINE):
        comment_ranges.append((m.start(), m.end()))
    
    # 查找所有匹配的属性值
    for match in re.finditer(pattern, content):
        # 检查是否在注释范围内
        is_in_comment = any(start <= match.start() <= end for start, end in comment_ranges)
        if is_in_comment:
            continue
        
        # 计算行号
        line_num = content.count('\n', 0, match.start()) + 1
        
        # 提取文本值
        value = match.group(1)
        
        # 处理f-string前缀
        if value.startswith('f'):
            value = value[1:]
        
        # 处理不同的引号类型
        if value.startswith('"""') and value.endswith('"""'):
            text = value[3:-3]
        elif value.startswith("'''") and value.endswith("'''"):
            text = value[3:-3]
        else:
            # 单引号或双引号
            text = value[1:-1]
        
        # 过滤空字符串
        if text and text.strip():
            entries.append((line_num, text))
    
    return entries

def extract_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取description属性值"""
    return extract_property_values(content, filepath, DESCRIPTION_PATTERN, "description")

def extract_purchase_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取purchase_notification属性值"""
    return extract_property_values(content, filepath, PURCHASE_NOTIFICATION_PATTERN, "purchase_notification")

def extract_unlock_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unlock_notification属性值"""
    return extract_property_values(content, filepath, UNLOCK_NOTIFICATION_PATTERN, "unlock_notification")
