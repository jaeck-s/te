"""
验证工厂类
负责创建和管理文本验证器
"""
from typing import Dict, Callable, List, Optional, Any, Set
import re

from ..logger import get_logger

class ValidatorFactory:
    """
    验证工厂类
    用于创建和管理文本验证器实例
    """
    
    def __init__(self) -> None:
        self.logger = get_logger()
        # 用于全局去重的集合 - 这是关键部分，它存储了所有已见过的文本
        self._seen_texts: Set[str] = set()
        
        self.validators: Dict[str, Callable[[str], bool]] = {
            "non_empty": self._validate_non_empty,
            "has_alphanumeric": self._validate_has_alphanumeric,
            "no_invalid_chars": self._validate_no_invalid_chars,
            "string_consistency": self._validate_string_consistency,
            "global_deduplicate": self._validate_global_deduplicate,
            "no_underscore": self._validate_no_underscore,  # 新增验证器
            "no_webp": self._validate_no_webp  # 添加新的验证器
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
    
    def _validate_string_consistency(self, text: str) -> bool:
        """
        验证字符串一致性，确保提取的字符串与游戏显示一致，并且能够被正确地写入到翻译文件中
        
        简化实现：只检查基本的语法平衡，不干扰游戏中使用的任何变量或标记
        """
        # 检查引号和花括号是否平衡
        brackets = {'"': 0, "'": 0, "{": 0, "}": 0}
        escape_flag = False
        
        # 简单遍历字符串，检查引号和花括号是否平衡
        # 但需要特殊处理英语中的撇号（所有格's和缩写n't等）
        i = 0
        while i < len(text):
            char = text[i]
            
            if escape_flag:
                escape_flag = False
                i += 1
                continue
                
            if char == '\\':
                escape_flag = True
            elif char == "'":
                # 特殊处理可能的撇号情况
                # 检查是否是英语中常见的撇号模式：
                # 1. 's, 't, 'd, 'll, 've, 're 等所有格或缩写形式
                # 2. n't 形式的否定缩写
                if i > 0 and i < len(text) - 1:
                    if text[i-1].isalpha() and (text[i+1] in "stdlrvm" or (i < len(text) - 2 and text[i+1:i+3] == "re")):
                        # 这可能是一个缩写，不计入引号计数
                        pass
                    elif i > 1 and text[i-2:i] == "n'" and i < len(text) - 1 and text[i+1] == "t":
                        # n't 形式的否定缩写
                        pass
                    else:
                        # 其他情况视为普通单引号
                        brackets["'"] += 1
                else:
                    # 字符串开头或结尾的单引号，直接计数
                    brackets["'"] += 1
            elif char in brackets:
                brackets[char] += 1
            
            i += 1
        
        # 确保双引号成对
        if brackets['"'] % 2 != 0:
            self.logger.debug(f"文本 '{text[:30]}...' 中的双引号不平衡")
            return False
        
        # 确保单引号成对 - 考虑到撇号的特殊处理后，应该是成对的
        if brackets["'"] % 2 != 0:
            # 记录日志但不要直接拒绝，可能是一些复杂的英语缩写导致误判
            self.logger.debug(f"文本 '{text[:30]}...' 中的单引号不平衡 (可能包含缩写或所有格)")
            # 不返回 False，允许通过验证
        
        # 确保花括号成对
        if brackets["{"] != brackets["}"]:
            self.logger.debug(f"文本 '{text[:30]}...' 中的花括号不平衡: {{ = {brackets['{']}, }} = {brackets['}']}")
            return False
        
        # 所有检查都通过
        return True
    
    def _validate_global_deduplicate(self, text: str) -> bool:
        """
        全局去重验证，确保在所有翻译文件中不会有重复的条目
        """
        # 格式化字符串，去除前后空格，便于准确比较
        normalized_text = text.strip()
        
        if normalized_text in self._seen_texts:
            self.logger.debug(f"文本 '{text[:30]}...' 已存在，被全局去重验证器拒绝")
            return False
        
        # 添加到已见过的文本集合
        self._seen_texts.add(normalized_text)
        return True
    
    def _validate_no_underscore(self, text: str) -> bool:
        """
        验证文本不包含下划线，但允许中括号和花括号内的下划线
        
        Args:
            text: 要验证的文本
            
        Returns:
            如果文本不包含不允许的下划线则返回True，否则返回False
        """
        # 定义正则表达式模式来匹配花括号和中括号内的内容
        bracket_patterns = [
            r'\{[^{}]*\}',  # 匹配花括号 {...} 内的内容
            r'\[[^\[\]]*\]'  # 匹配中括号 [...] 内的内容
        ]
        
        # 创建一个文本的副本
        processed_text = text
        
        # 将所有括号内的内容替换为占位符
        for pattern in bracket_patterns:
            # 使用一个只包含字母的占位符来替换括号内容，避免添加额外的下划线
            processed_text = re.sub(pattern, "PLACEHOLDER", processed_text)
        
        # 在处理后的文本中检查下划线
        if '_' in processed_text:
            self.logger.debug(f"文本 '{text[:30]}...' 包含不允许的下划线，被拒绝提取")
            return False
            
        return True
    
    def _validate_no_webp(self, text: str) -> bool:
        """
        验证文本不包含.webp扩展名，使用正则表达式确保只匹配真正的文件引用
        
        Args:
            text: 要验证的文本
            
        Returns:
            如果文本不包含.webp文件引用则返回True，否则返回False
        """
        # 匹配更精确的模式：
        # 1. 文件路径格式的.webp: xxx/xxx.webp 或 xxx\\xxx.webp
        # 2. 直接的文件名引用: xxx.webp
        # 3. 引号内的文件名: "xxx.webp" 或 'xxx.webp'
        # 确保.webp在单词边界或字符串结尾
        if re.search(r'(?:\/|\\|\s|^|\")([^\/\\"\s]+)\.webp(?:\b|"|\'|$)', text.lower()):
            self.logger.debug(f"文本 '{text[:30]}...' 包含.webp文件引用，被拒绝提取")
            return False
        return True
    
    def reset_deduplication(self) -> None:
        """
        重置去重状态，清空已见过的文本集合
        """
        self._seen_texts.clear()
        self.logger.debug("已重置全局去重状态")
    
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
