"""
用于提取JSON文件中的特定字段值，提供通用的字段提取实现
"""
import json
import re
from typing import List, Tuple, Dict, Any, Union, Optional, Set
from .common import process_nested_objects

def get_json_fields() -> Dict[str, Dict]:
    """获取自定义JSON字段配置"""
    try:
        import json
        import os
        
        # 获取配置文件路径
        config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            "configs", "json_fields.json"
        )
        
        # 如果配置文件存在，加载字段
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("fields", {})
    except Exception as e:
        print(f"加载JSON字段配置时出错: {str(e)}")
    
    return {}

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

def extract_specific_json_field(content: str, filepath: str, field_name: str) -> List[Tuple[int, str]]:
    """
    从JSON文件中提取特定字段的值
    
    Args:
        content: JSON文件内容
        filepath: 文件路径
        field_name: 要提取的字段名
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    try:
        # 移除JSON注释 (如果存在)
        # 这里处理两种常见的JSON注释格式
        # 单行注释: // 注释内容
        content = re.sub(r'//.*$', '', content, flags=re.MULTILINE)
        
        # 解析JSON
        json_data = json.loads(content)
        
        # 提取指定字段
        return extract_field_from_json(json_data, field_name)
    except json.JSONDecodeError:
        # 如果JSON解析失败，返回空列表
        return []
    except Exception:
        # 其他异常处理
        return []

def extract_all_json_fields(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    从JSON文件中提取所有配置的字段值
    
    Args:
        content: JSON文件内容
        filepath: 文件路径
        
    Returns:
        提取的(行号, 文本内容)列表
    """
    entries = []
    
    # 获取JSON字段配置
    json_fields = get_json_fields()
    
    # 提取每个启用的JSON字段
    for field_name, field_info in json_fields.items():
        if field_info.get("enabled", True):
            field_entries = extract_specific_json_field(content, filepath, field_name)
            entries.extend(field_entries)
    
    return entries

# 为了向后兼容保留的函数，现在调用通用方法
def extract_display_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取JSON文件中的display_name字段值
    
    Args:
        content: JSON文件内容
        filepath: 文件路径(用于日志)
        
    Returns:
        提取的(行号, 文本内容)列表，行号表示JSON嵌套层级
    """
    return extract_specific_json_field(content, filepath, "display_name")

def extract_json_description(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    提取JSON文件中的description字段值
    """
    return extract_specific_json_field(content, filepath, "description")

def extract_person_name(content: str, filepath: str) -> List[Tuple[int, str]]:
    """
    从JSON文件中提取人名相关字段(first_name和last_name)
    
    Args:
        content: JSON文件内容
        filepath: 文件路径(用于日志)
        
    Returns:
        提取的(行号, 文本内容)列表
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
