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
    SINGLE_LINE_COMMENT_PATTERN,
    TITLE_TEXT_PATTERN,
    DESCRIPTION_TEXT_PATTERN,
    RENPY_NOTIFY_PATTERN,
    NAME_PATTERN,
    SPONSOR_DESCRIPTION_PATTERN,  # 添加新的模式
    TOOLTIP_PATTERN,  # 添加tooltip模式
    TEXT_PATTERN,        # 添加text模式
    TEXTBUTTON_PATTERN,  # 添加textbutton模式
    AVAILABLE_TOOLTIP_PATTERN,      # 添加新模式
    UNAVAILABLE_TOOLTIP_PATTERN,    # 添加新模式
    UNAVAILABLE_NOTIFICATION_PATTERN,  # 添加新模式
    GENERIC_KEY_PATTERN,  # 更改为新的模式
    COLD_KEY_PATTERN,     # 更改为新的模式
    STRING_PATTERN
)
from .common import extract_with_pattern, extract_string_value

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
    return extract_with_pattern(
        content=content,
        filepath=filepath,
        pattern=pattern,
        comment_patterns=[MULTILINE_COMMENT_PATTERN, SINGLE_LINE_COMMENT_PATTERN],
        group_index=1,
        extractor_name=property_name
    )

def extract_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取description属性值"""
    return extract_property_values(content, filepath, DESCRIPTION_PATTERN, "description")

def extract_purchase_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取purchase_notification属性值"""
    return extract_property_values(content, filepath, PURCHASE_NOTIFICATION_PATTERN, "purchase_notification")

def extract_unlock_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unlock_notification属性值"""
    return extract_property_values(content, filepath, UNLOCK_NOTIFICATION_PATTERN, "unlock_notification")

def extract_title_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取title_text属性值"""
    return extract_property_values(content, filepath, TITLE_TEXT_PATTERN, "title_text")

def extract_description_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取description_text属性值"""
    return extract_property_values(content, filepath, DESCRIPTION_TEXT_PATTERN, "description_text")

def extract_renpy_notify(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取renpy.notify函数调用中的文本"""
    return extract_property_values(content, filepath, RENPY_NOTIFY_PATTERN, "renpy.notify")

def extract_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取name属性值"""
    return extract_property_values(content, filepath, NAME_PATTERN, "name")

def extract_sponsor_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取sponsor_description属性值"""
    return extract_property_values(content, filepath, SPONSOR_DESCRIPTION_PATTERN, "sponsor_description")

def extract_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取tooltip属性值"""
    return extract_property_values(content, filepath, TOOLTIP_PATTERN, "tooltip")

def extract_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取text标签文本"""
    return extract_property_values(content, filepath, TEXT_PATTERN, "text")

def extract_textbutton(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取textbutton标签文本"""
    return extract_property_values(content, filepath, TEXTBUTTON_PATTERN, "textbutton")

def extract_available_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取available_tooltip属性值"""
    return extract_property_values(content, filepath, AVAILABLE_TOOLTIP_PATTERN, "available_tooltip")

def extract_unavailable_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unavailable_tooltip属性值"""
    return extract_property_values(content, filepath, UNAVAILABLE_TOOLTIP_PATTERN, "unavailable_tooltip")

def extract_unavailable_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unavailable_notification属性值"""
    return extract_property_values(content, filepath, UNAVAILABLE_NOTIFICATION_PATTERN, "unavailable_notification")

def extract_dict_keys(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取所有字符串块中的字符串值
    不分析嵌套结构，直接匹配文本中的模式
    
    Args:
        content: 文件内容
        filepath: 文件路径
        
    Returns:
        提取的(行号, 值)列表
    """
    entries = []
    
    # 获取所有注释的范围
    comment_patterns = [MULTILINE_COMMENT_PATTERN, SINGLE_LINE_COMMENT_PATTERN]
    from .common import get_comment_ranges, is_in_comments, get_line_number
    
    comment_ranges = get_comment_ranges(content, comment_patterns)
    
    # 初始化键名列表
    key_starts = []
    
    # 从配置文件加载键名
    try:
        import json
        import os
        
        # 获取配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "configs", "dict_keys.json"
        )
        
        # 如果配置文件存在，加载键名
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # 处理新的键名格式（字典格式，包含启用状态）
                if isinstance(data.get("key_names"), dict):
                    key_dict = data.get("key_names", {})
                    # 只加载启用的键名
                    key_names = [key for key, enabled in key_dict.items() if enabled]
                else:
                    # 向后兼容，处理旧的列表格式
                    key_names = data.get("key_names", [])
                
                # 将键名转换为查找格式："键名":
                for key in key_names:
                    # 仅对双引号进行转义，保留单引号原样
                    key = key.replace('"', '\\"')
                    formatted_key = f'"{key}":'
                    key_starts.append(formatted_key)
    except Exception as e:
        print(f"加载键名时出错: {str(e)}")
    
    # 如果没有从配置文件加载到键名，使用一个空列表
    if not key_starts:
        # 不再使用默认键名列表，而是记录一条日志信息
        print("警告: 未能从配置文件加载键名，将不会提取任何字符串")
    
    # 对每个关键字进行处理
    for key_start in key_starts:
        start_pos = 0
        while True:
            # 查找关键字
            pos = content.find(key_start, start_pos)
            if pos == -1:
                break
                
            # 检查是否在注释中
            if is_in_comments(pos, comment_ranges):
                start_pos = pos + len(key_start)
                continue
                
            # 寻找方括号开始位置
            bracket_start = content.find('[', pos)
            if bracket_start == -1:
                start_pos = pos + len(key_start)
                continue
                
            # 寻找对应的闭合方括号
            bracket_depth = 1
            i = bracket_start + 1
            bracket_end = -1
            
            while i < len(content) and bracket_depth > 0:
                if content[i] == '[':
                    bracket_depth += 1
                elif content[i] == ']':
                    bracket_depth -= 1
                    if bracket_depth == 0:
                        bracket_end = i
                        break
                i += 1
                
            if bracket_end == -1:
                # 未找到匹配的右括号
                start_pos = pos + len(key_start)
                continue
                
            # 提取字符串数组内容
            array_content = content[bracket_start+1:bracket_end]
            
            # 提取所有字符串
            for string_match in re.finditer(STRING_PATTERN, array_content):
                string_value = string_match.group(0)
                text = extract_string_value(string_value)
                
                if text and text.strip():
                    # 计算字符串在原文本中的位置和行号
                    string_pos = bracket_start + 1 + string_match.start()
                    line_num = get_line_number(content, string_pos)
                    entries.append((line_num, text))
            
            # 从结束位置继续查找
            start_pos = bracket_end + 1
    
    return entries
