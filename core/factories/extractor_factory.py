"""
提取工厂类
负责创建和管理文本提取器
"""
from typing import Dict, Callable, List, Tuple, Optional
from ..extractors_impl.rpy_properties import (
    extract_description,
    extract_purchase_notification,
    extract_unlock_notification
)
from ..logger import get_logger

class ExtractorFactory:
    """
    提取工厂类
    用于创建和管理文本提取器实例
    """
    
    def __init__(self) -> None:
        self.logger = get_logger()
        # 直接在工厂类中初始化提取器，而不是从外部导入
        self.extractors: Dict[str, Callable[[str, str], List[Tuple[int, str]]]] = {
            "description": extract_description,
            "purchase_notification": extract_purchase_notification,
            "unlock_notification": extract_unlock_notification,
        }
        self.logger.debug(f"提取工厂初始化完成，加载了 {len(self.extractors)} 个提取器")
    
    def get_extractor(self, name: str) -> Optional[Callable[[str, str], List[Tuple[int, str]]]]:
        """
        获取指定名称的提取器
        
        Args:
            name: 提取器名称
            
        Returns:
            提取器函数，如果不存在则返回None
        """
        if name in self.extractors:
            return self.extractors[name]
        self.logger.warning(f"未找到名为 '{name}' 的提取器")
        return None
    
    def get_all_extractors(self) -> Dict[str, Callable[[str, str], List[Tuple[int, str]]]]:
        """
        获取所有注册的提取器
        
        Returns:
            所有提取器的字典
        """
        return self.extractors.copy()
    
    def get_extractors_by_names(self, names: List[str]) -> Dict[str, Callable[[str, str], List[Tuple[int, str]]]]:
        """
        根据名称列表获取提取器
        
        Args:
            names: 提取器名称列表
            
        Returns:
            匹配的提取器字典
        """
        result = {}
        for name in names:
            extractor = self.get_extractor(name)
            if extractor:
                result[name] = extractor
        return result
    
    def register_extractor(self, name: str, extractor: Callable[[str, str], List[Tuple[int, str]]]) -> bool:
        """
        注册新的提取器
        
        Args:
            name: 提取器名称
            extractor: 提取器函数
            
        Returns:
            注册是否成功
        """
        if name in self.extractors:
            self.logger.warning(f"提取器 '{name}' 已存在，将被覆盖")
        
        self.extractors[name] = extractor
        self.logger.debug(f"成功注册提取器 '{name}'")
        return True
    
    def unregister_extractor(self, name: str) -> bool:
        """
        注销提取器
        
        Args:
            name: 提取器名称
            
        Returns:
            注销是否成功
        """
        if name in self.extractors:
            del self.extractors[name]
            self.logger.debug(f"成功注销提取器 '{name}'")
            return True
        return False
    
    def extract_from_content(self, content: str, filepath: str, extractor_names: List[str]) -> List[Tuple[int, str]]:
        """
        使用指定的提取器从内容中提取文本
        
        Args:
            content: 文件内容
            filepath: 文件路径
            extractor_names: 要使用的提取器名称列表
            
        Returns:
            提取的文本元组列表 [(行号, 文本)]
        """
        result = []
        for name in extractor_names:
            extractor = self.get_extractor(name)
            if extractor:
                entries = extractor(content, filepath)
                if entries:
                    result.extend(entries)
                    self.logger.debug(f"使用提取器 '{name}' 从 {filepath} 提取了 {len(entries)} 个条目")
        
        return result
