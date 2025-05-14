"""
用于提取JSON文件中的特定字段值，目前支持提取任何层级的display_name字段
"""
import json
import re
from typing import List, Tuple, Dict, Any, Union, Optional

def extract_field_from_json(json_data: Union[Dict[Any, Any], List[Any]], field_name: str, 
                           path: str = "", level: int = 1, 
                           result: Optional[List[Tuple[int, str]]] = None) -> List[Tuple[int, str]]:
    """
    递归提取JSON数据中的指定字段
    
    Args:
        json_data: JSON数据（字典或列表）
        field_name: 要提取的字段名
        path: 当前JSON路径（用于调试）
        level: 当前嵌套层级（用作行号）
        result: 结果列表，格式为(行号, 文本)
        
    Returns:
        提取的文本列表，格式为(行号, 文本)
    """
    if result is None:
        result = []
    
    # 处理字典类型
    if isinstance(json_data, dict):
        for key, value in json_data.items():
            current_path = f"{path}.{key}" if path else key
            
            # 检查当前键是否匹配目标字段
            if key == field_name and isinstance(value, str):
                # 使用当前层级作为行号
                result.append((level, value))
            
            # 递归处理嵌套对象
            if isinstance(value, (dict, list)):
                extract_field_from_json(value, field_name, current_path, level + 1, result)
    
    # 处理列表类型
    elif isinstance(json_data, list):
        for i, item in enumerate(json_data):
            current_path = f"{path}[{i}]"
            if isinstance(item, (dict, list)):
                extract_field_from_json(item, field_name, current_path, level + 1, result)
    
    return result

def extract_display_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取JSON文件中的display_name字段值
    
    Args:
        content: JSON文件内容
        filepath: 文件路径(用于日志)
        
    Returns:
        提取的(行号, 文本内容)列表，行号表示JSON嵌套层级
    """
    try:
        # 移除JSON注释 (如果存在)
        # 这里处理两种常见的JSON注释格式
        # 单行注释: // 注释内容
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 解析JSON
        json_data = json.loads(content)
        
        # 提取display_name字段
        return extract_field_from_json(json_data, "display_name")
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回空列表
        return []
    except Exception:
        # 其他异常处理
        return []
