"""
写入工厂类
负责创建和管理翻译文件写入器
"""
import os
import re
from typing import Dict, Callable, List, Optional, Tuple, Any
from ..logger import get_logger

class WriterFactory:
    """
    写入工厂类
    用于创建和管理翻译文件写入器实例
    """
    
    def __init__(self) -> None:
        self.logger = get_logger()
        self.writers: Dict[str, Callable] = {
            "renpy": self._write_renpy_translation,
            "json": self._write_json_translation,
            "csv": self._write_csv_translation
        }
        self.logger.debug(f"写入工厂初始化完成，加载了 {len(self.writers)} 个写入器")
    
    def _write_renpy_translation(self, filepath: str, entries: List[Tuple[int, str]], 
                               rel_path: str, config: Any) -> bool:
        """
        写入Renpy格式的翻译文件
        
        Args:
            filepath: 目标文件路径
            entries: 需要写入的条目列表 [(行号, 文本)]
            rel_path: 源文件相对路径
            config: 配置对象
            
        Returns:
            写入是否成功
        """
        try:
            # 确保目标目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 准备文件内容
            file_header = 'translate schinese strings:\n\n'
            generated_content = ''
            
            # 如果文件不存在或不包含标准头，添加标准头
            if not os.path.exists(filepath) or file_header not in open(filepath, 'r', encoding=config.encoding).read():
                generated_content = file_header
            
            # 添加新条目
            for line_num, text in entries:
                generated_content += f'    # {rel_path} line {line_num}\n'
                if '\n' in text:
                    # 多行文本
                    generated_content += '    old """\n'
                    generated_content += f'{text}\n'
                    generated_content += '    """\n'
                    generated_content += '    new """\n'
                    generated_content += '    """\n\n'
                else:
                    # 单行文本
                    escaped_text = text.replace('"', '\\"')
                    generated_content += f'    old "{escaped_text}"\n'
                    generated_content += f'    new ""\n\n'
            
            # 写入文件
            mode = 'a' if os.path.exists(filepath) else 'w'
            with open(filepath, mode, encoding=config.encoding) as f:
                f.write(generated_content)
                
            self.logger.debug(f"成功写入 {len(entries)} 个翻译条目到 {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"写入文件 {filepath} 失败: {str(e)}")
            return False
    
    def _write_json_translation(self, filepath: str, entries: List[Tuple[int, str]], 
                              rel_path: str, config: Any) -> bool:
        """写入JSON格式的翻译文件"""
        try:
            import json
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 修改扩展名为.json
            filepath = os.path.splitext(filepath)[0] + ".json"
            
            # 准备JSON数据
            translation_data = {
                "source_file": rel_path,
                "entries": [
                    {"line": line, "source": text, "translation": ""} 
                    for line, text in entries
                ]
            }
            
            # 写入文件
            with open(filepath, 'w', encoding=config.encoding) as f:
                json.dump(translation_data, f, ensure_ascii=False, indent=2)
                
            self.logger.debug(f"成功写入 {len(entries)} 个翻译条目到JSON文件 {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"写入JSON文件 {filepath} 失败: {str(e)}")
            return False
    
    def _write_csv_translation(self, filepath: str, entries: List[Tuple[int, str]], 
                             rel_path: str, config: Any) -> bool:
        """写入CSV格式的翻译文件"""
        try:
            import csv
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 修改扩展名为.csv
            filepath = os.path.splitext(filepath)[0] + ".csv"
            
            # 写入CSV文件
            with open(filepath, 'w', encoding=config.encoding, newline='') as f:
                writer = csv.writer(f)
                # 写入标题行
                writer.writerow(["Line", "SourceFile", "SourceText", "Translation"])
                # 写入数据行
                for line_num, text in entries:
                    writer.writerow([line_num, rel_path, text, ""])
                
            self.logger.debug(f"成功写入 {len(entries)} 个翻译条目到CSV文件 {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"写入CSV文件 {filepath} 失败: {str(e)}")
            return False
    
    def get_writer(self, name: str) -> Optional[Callable]:
        """
        获取指定名称的写入器
        
        Args:
            name: 写入器名称
            
        Returns:
            写入器函数，如果不存在则返回None
        """
        if name in self.writers:
            return self.writers[name]
        self.logger.warning(f"未找到名为 '{name}' 的写入器")
        return None
    
    def get_all_writers(self) -> Dict[str, Callable]:
        """
        获取所有注册的写入器
        
        Returns:
            所有写入器的字典
        """
        return self.writers.copy()
    
    def register_writer(self, name: str, writer: Callable) -> bool:
        """
        注册新的写入器
        
        Args:
            name: 写入器名称
            writer: 写入器函数
            
        Returns:
            注册是否成功
        """
        if name in self.writers:
            self.logger.warning(f"写入器 '{name}' 已存在，将被覆盖")
        
        self.writers[name] = writer
        self.logger.debug(f"成功注册写入器 '{name}'")
        return True
    
    def unregister_writer(self, name: str) -> bool:
        """
        注销写入器
        
        Args:
            name: 写入器名称
            
        Returns:
            注销是否成功
        """
        if name in self.writers:
            del self.writers[name]
            self.logger.debug(f"成功注销写入器 '{name}'")
            return True
        return False
    
    def write_translation_file(self, name: str, filepath: str, entries: List[Tuple[int, str]], 
                              rel_path: str, config: Any) -> bool:
        """
        使用指定的写入器写入翻译文件
        
        Args:
            name: 写入器名称
            filepath: 目标文件路径
            entries: 需要写入的条目列表 [(行号, 文本)]
            rel_path: 源文件相对路径
            config: 配置对象
            
        Returns:
            写入是否成功
        """
        writer = self.get_writer(name)
        if not writer:
            return False
            
        return writer(filepath, entries, rel_path, config)
