"""
用于提取RPY文件中的特定属性值和函数调用
"""
import re
from typing import List, Tuple
from ..regex.rpy_patterns import (
    MULTILINE_COMMENT_PATTERN,
    SINGLE_LINE_COMMENT_PATTERN,
    RENPY_NOTIFY_PATTERN,
    STRING_PATTERN,
    # ...其他需要的模式...
)
from .common import extract_with_pattern, extract_string_value, get_comment_ranges, is_in_comments, get_line_number

# 保留renpy.notify函数提取功能
def extract_renpy_notify(content: str, filepath: str) -> List[Tuple[int, str]]:
    """提取renpy.notify函数调用中的文本"""
    return extract_with_pattern(
        content=content,
        filepath=filepath,
        pattern=RENPY_NOTIFY_PATTERN,
        comment_patterns=[MULTILINE_COMMENT_PATTERN, SINGLE_LINE_COMMENT_PATTERN],
        group_index=1,
        extractor_name="renpy.notify"
    )

# 保留字典键值提取功能
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
