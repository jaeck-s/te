"""
验证工厂类
负责创建和管理文本验证器
"""
from typing import Dict, Callable, List, Optional, Any

from ..logger import get_logger

class ValidatorFactory:
    """
    验证工厂类
    用于创建和管理文本验证器实例
    """
    
    def __init__(self) -> None:
        self.logger = get_logger()
        self.validators: Dict[str, Callable[[str], bool]] = {
            "non_empty": self._validate_non_empty,
            "has_alphanumeric": self._validate_has_alphanumeric,
            "no_invalid_chars": self._validate_no_invalid_chars
        }
        self.logger.debug(f"验证工厂初始化完成，加载了 {len(self.validators)} 个验证器")
    
    def _validate_non_empty(self, text: str) -> bool:
        """验证文本非空"""
        return bool(text and text.strip())
    
    def _validate_has_alphanumeric(self, text: str) -> bool:
        """验证文本包含字母或数字"""
        return any(c.isalnum() for c in text)
    
    def _validate_no_invalid_chars(self, text: str) -> bool:
        """验证文本不包含无效字符"""
        invalid_chars = ['\0', '\ufffd']  # 空字符和替换字符
        return not any(c in text for c in invalid_chars)
    
    def get_validator(self, name: str) -> Optional[Callable[[str], bool]]:
        """
        获取指定名称的验证器
        
        Args:
            name: 验证器名称
            
        Returns:
            验证器函数，如果不存在则返回None
        """
        if name in self.validators:
            return self.validators[name]
        self.logger.warning(f"未找到名为 '{name}' 的验证器")
        return None
    
    def get_all_validators(self) -> Dict[str, Callable[[str], bool]]:
        """
        获取所有注册的验证器
        
        Returns:
            所有验证器的字典
        """
        return self.validators.copy()
    
    def register_validator(self, name: str, validator: Callable[[str], bool]) -> bool:
        """
        注册新的验证器
        
        Args:
            name: 验证器名称
            validator: 验证器函数
            
        Returns:
            注册是否成功
        """
        if name in self.validators:
            self.logger.warning(f"验证器 '{name}' 已存在，将被覆盖")
        
        self.validators[name] = validator
        self.logger.debug(f"成功注册验证器 '{name}'")
        return True
    
    def unregister_validator(self, name: str) -> bool:
        """
        注销验证器
        
        Args:
            name: 验证器名称
            
        Returns:
            注销是否成功
        """
        if name in self.validators:
            del self.validators[name]
            self.logger.debug(f"成功注销验证器 '{name}'")
            return True
        return False
    
    def validate_text(self, text: str, validator_names: Optional[List[str]] = None) -> bool:
        """
        使用指定的验证器验证文本
        
        Args:
            text: 要验证的文本
            validator_names: 要使用的验证器名称列表，为None时使用所有验证器
            
        Returns:
            验证是否通过
        """
        if validator_names is None:
            validator_names = list(self.validators.keys())
        
        for name in validator_names:
            validator = self.get_validator(name)
            if validator and not validator(text):
                self.logger.debug(f"文本 '{text[:30]}...' 未通过验证器 '{name}'")
                return False
        
        return True
