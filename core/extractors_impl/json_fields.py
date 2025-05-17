"""
用于提取JSON文件中的特定字段值，目前支持提取任何层级的display_name字段
"""
import json
import re
from typing import List, Tuple, Dict, Any, Union, Optional
from .common import process_nested_objects

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
    def field_processor(data, path, level, result):
        if isinstance(data, dict) and field_name in data and isinstance(data[field_name], str):
            result.append((level, data[field_name]))
    
    return process_nested_objects(json_data, field_processor, path, level, result)

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

def extract_json_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取JSON文件中的description字段值
    
    Args:
        content: JSON文件内容
        filepath: 文件路径(用于日志)
        
    Returns:
        提取的(行号, 文本内容)列表，行号表示JSON嵌套层级
    """
    try:
        # 移除JSON注释 (如果存在)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 解析JSON
        json_data = json.loads(content)
        
        # 提取description字段
        return extract_field_from_json(json_data, "description")
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回空列表
        return []
    except Exception:
        # 其他异常处理
        return []

def extract_person_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    从JSON文件中提取人名相关字段(first_name和last_name)
    
    Args:
        content: JSON文件内容
        filepath: 文件路径(用于日志)
        
    Returns:
        提取的(行号, 文本内容)列表，其中行号包含额外编码：
        - 正数表示常规字段（如display_name）
        - -1表示first_name字段
        - -2表示last_name字段
        负数用来在写入器中区分不同类型的名字字段
    """
    try:
        # 移除JSON注释 (如果存在)
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 解析JSON
        json_data = json.loads(content)
        
        # 存储结果，使用特殊行号标记不同类型的名字
        result: List[Tuple[int, str]] = []
        
        # 使用通用处理函数提取人名
        def name_processor(data, path, level, result):
            if isinstance(data, dict):
                # 检查first_name和last_name
                first_name = data.get("first_name")
                last_name = data.get("last_name")
                
                if first_name and isinstance(first_name, str):
                    result.append((-1, first_name))
                
                if last_name and isinstance(last_name, str):
                    result.append((-2, last_name))
        
        # 开始递归提取
        return process_nested_objects(json_data, name_processor)
        
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回空列表
        return []
    except Exception:
        # 其他异常处理
        return []
