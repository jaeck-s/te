"""
用于提取RPY文件中的自定义属性值和标准属性值
集成了所有属性提取功能，包括原有的内置属性和用户自定义属性
"""
import re
from typing import List, Tuple, Dict, Any
from ..regex.rpy_patterns import (
    MULTILINE_COMMENT_PATTERN,
    SINGLE_LINE_COMMENT_PATTERN,
    STRING_PATTERN
)
from .common import extract_with_pattern, extract_string_value, get_comment_ranges, is_in_comments, get_line_number

def get_custom_properties() -> List[Dict[str, Any]]:
    """获取自定义属性配置"""
    try:
        import json
        import os
        
        # 获取配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "configs", "custom_properties.json"
        )
        
        # 如果配置文件存在，加载属性
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # 返回属性列表
                return data.get("properties", [])
    except Exception as e:
        print(f"加载自定义属性时出错: {str(e)}")
    
    return []

def extract_custom_property(content: str, filepath: str, prop_name: str, assignment_type: int) -> List[Tuple[int, str]]:
    """
    根据赋值方式提取指定属性的值
    
    Args:
        content: 文件内容
        filepath: 文件路径
        prop_name: 属性名
        assignment_type: 赋值方式 (1: 等号赋值, 2: 键值对, 3: 空格隔开)
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    entries = []
    
    # 获取所有注释的范围
    comment_patterns = [MULTILINE_COMMENT_PATTERN, SINGLE_LINE_COMMENT_PATTERN]
    comment_ranges = get_comment_ranges(content, comment_patterns)
    
    # 根据赋值方式创建正则表达式模式
    if assignment_type == 1:  # 等号赋值 (处理等号两边可能有空格的情况)
        pattern = rf'\b{re.escape(prop_name)}\s*=\s*((?:f)?{STRING_PATTERN})'
    elif assignment_type == 2:  # 键值对
        # 修改了正则表达式，使双引号和单引号变成可选，用户无需输入引号
        pattern = rf'["\']?{re.escape(prop_name)}["\']?[\s]*:[\s]*((?:f)?{STRING_PATTERN})'
    elif assignment_type == 3:  # 空格隔开
        pattern = rf'\b{re.escape(prop_name)}\s+((?:f)?{STRING_PATTERN})'
    else:
        return []  # 不支持的赋值方式
    
    # 查找所有匹配
    for match in re.finditer(pattern, content):
        # 检查是否在注释范围内
        if is_in_comments(match.start(), comment_ranges):
            continue
        
        # 计算行号
        line_num = get_line_number(content, match.start())
        
        # 提取文本值
        value = match.group(1)
        
        # 处理字符串值
        text = extract_string_value(value)
        
        # 过滤空字符串
        if text and text.strip():
            entries.append((line_num, text))
    
    return entries

def extract_all_custom_properties(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取所有自定义属性的值（包括内置属性和用户自定义属性）
    
    Args:
        content: 文件内容
        filepath: 文件路径
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    entries = []
    
    # 获取自定义属性配置（现在是列表形式）
    custom_properties = get_custom_properties()
    
    # 提取每个启用的自定义属性
    for prop_info in custom_properties:
        if prop_info.get("enabled", True):
            prop_name = prop_info.get("name", "")
            assignment_type = prop_info.get("type", 1)
            
            if prop_name:  # 确保属性名非空
                prop_entries = extract_custom_property(content, filepath, prop_name, assignment_type)
                entries.extend(prop_entries)
    
    return entries

# 以下是为了向后兼容而保留的函数，直接调用集成后的提取逻辑
def extract_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取description属性值"""
    return extract_custom_property(content, filepath, "description", 1)

def extract_purchase_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取purchase_notification属性值"""
    return extract_custom_property(content, filepath, "purchase_notification", 1)

def extract_unlock_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unlock_notification属性值"""
    return extract_custom_property(content, filepath, "unlock_notification", 1)

def extract_title_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取title_text属性值"""
    return extract_custom_property(content, filepath, "title_text", 1)

def extract_description_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取description_text属性值"""
    return extract_custom_property(content, filepath, "description_text", 1)

# 注意：不再实现extract_renpy_notify，该函数将从rpy_properties.py导入

def extract_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取name属性值"""
    return extract_custom_property(content, filepath, "name", 1)

def extract_sponsor_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取sponsor_description属性值"""
    return extract_custom_property(content, filepath, "sponsor_description", 1)

def extract_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取tooltip属性值"""
    return extract_custom_property(content, filepath, "tooltip", 3)

def extract_text(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取text标签文本"""
    return extract_custom_property(content, filepath, "text", 3)

def extract_textbutton(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取textbutton标签文本"""
    return extract_custom_property(content, filepath, "textbutton", 3)

def extract_available_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取available_tooltip属性值"""
    return extract_custom_property(content, filepath, "available_tooltip", 2)

def extract_unavailable_tooltip(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unavailable_tooltip属性值"""
    return extract_custom_property(content, filepath, "unavailable_tooltip", 2)

def extract_unavailable_notification(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取unavailable_notification属性值"""
    return extract_custom_property(content, filepath, "unavailable_notification", 2)
