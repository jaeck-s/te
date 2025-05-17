"""
通用提取方法模块
包含RPY和JSON文件共用的提取逻辑和工具函数
"""
import re
from typing import List, Tuple, Dict, Any, Union, Optional, Callable

def get_comment_ranges(content: str, patterns: List[str]) -> List[Tuple[int, int]]:
    """
    获取所有注释的范围
    
    Args:
        content: 文件内容
        patterns: 注释模式列表，如[MULTILINE_COMMENT_PATTERN, SINGLE_LINE_COMMENT_PATTERN]
        
    Returns:
        所有注释的起止位置列表 [(start, end), ...]
    """
    comment_ranges = []
    
    # 匹配所有注释
    for pattern in patterns:
        for m in re.finditer(pattern, content, re.MULTILINE):
            comment_ranges.append((m.start(), m.end()))
    
    return comment_ranges

def is_in_comments(pos: int, comment_ranges: List[Tuple[int, int]]) -> bool:
    """
    检查位置是否在注释范围内
    
    Args:
        pos: 位置
        comment_ranges: 注释范围列表
        
    Returns:
        是否在注释范围内
    """
    return any(start <= pos <= end for start, end in comment_ranges)

def get_line_number(content: str, pos: int) -> int:
    """
    获取指定位置的行号
    
    Args:
        content: 文件内容
        pos: 位置
        
    Returns:
        行号（从1开始）
    """
    return content.count('\n', 0, pos) + 1

def extract_string_value(value: str) -> str:
    """
    处理字符串值，移除引号和处理前缀
    
    Args:
        value: 原始字符串值
        
    Returns:
        处理后的字符串
    """
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
    
    return text

def extract_with_pattern(
    content: str,
    filepath: str,
    pattern: str,
    comment_patterns: List[str],
    group_index: int = 1,
    extractor_name: str = "generic_extractor"
) -> List[Tuple[int, str]]:
    """
    通用的正则表达式提取函数
    
    Args:
        content: 文件内容
        filepath: 文件路径
        pattern: 正则表达式模式
        comment_patterns: 注释模式列表
        group_index: 要提取的正则表达式组索引
        extractor_name: 提取器名称（用于日志）
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    entries = []
    
    # 获取所有注释的范围
    comment_ranges = get_comment_ranges(content, comment_patterns)
    
    # 查找所有匹配
    for match in re.finditer(pattern, content):
        # 检查是否在注释范围内
        if is_in_comments(match.start(), comment_ranges):
            continue
        
        # 计算行号
        line_num = get_line_number(content, match.start())
        
        # 提取文本值
        value = match.group(group_index)
        
        # 处理字符串值
        text = extract_string_value(value)
        
        # 过滤空字符串
        if text and text.strip():
            entries.append((line_num, text))
    
    return entries

def process_nested_objects(
    data: Union[Dict[Any, Any], List[Any]],
    processor: Callable[[Any, str, int, List[Tuple[int, str]]], None],
    path: str = "",
    level: int = 1,
    result: Optional[List[Tuple[int, str]]] = None
) -> List[Tuple[int, str]]:
    """
    递归处理嵌套对象
    
    Args:
        data: 数据（字典或列表）
        processor: 处理函数，接收(data, path, level, result)
        path: 当前路径（用于调试）
        level: 当前嵌套层级（用作行号）
        result: 结果列表
        
    Returns:
        处理结果列表
    """
    if result is None:
        result = []
    
    # 处理对象
    processor(data, path, level, result)
    
    # 递归处理嵌套对象
    if isinstance(data, dict):
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key
            if isinstance(value, (dict, list)):
                process_nested_objects(value, processor, current_path, level + 1, result)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            current_path = f"{path}[{i}]"
            if isinstance(item, (dict, list)):
                process_nested_objects(item, processor, current_path, level + 1, result)
    
    return result
