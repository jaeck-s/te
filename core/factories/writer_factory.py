"""
写入工厂类
负责创建和管理翻译文件写入器
"""
import os
import re
import glob
import shutil
from typing import Dict, Callable, List, Optional, Tuple, Any
from ..logger import get_logger
from ..events import publish, EventNames

class WriterFactory:
    """
    写入工厂类
    用于创建和管理翻译文件写入器实例
    """
    
    # 定义写入模式常量
    MODE_APPEND = "append"   # 追加模式
    MODE_OVERWRITE = "overwrite"  # 覆盖模式
    
    def __init__(self) -> None:
        self.logger = get_logger()
        self.writers: Dict[str, Callable] = {
            "renpy": self._write_renpy_translation,
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
            # 获取写入模式
            write_mode = getattr(config, "write_mode", self.MODE_APPEND)
            
            # 确保目标目录存在
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # 如果是覆盖模式，先处理目录清理
            if write_mode == self.MODE_OVERWRITE:
                self._handle_overwrite_mode(filepath, config)
            
            # 准备文件内容
            file_header = 'translate schinese strings:\n\n'
            generated_content = ''
            
            # 如果文件不存在或不包含标准头，添加标准头
            if not os.path.exists(filepath) or file_header not in open(filepath, 'r', encoding=config.encoding).read():
                generated_content = file_header
            
            # 添加新条目 - 统一使用单行文本格式
            for line_num, text in entries:
                generated_content += f'    # {rel_path} line {line_num}\n'
                
                # 处理转义字符：
                # 1. 保留原字符串中的\n换行符
                # 2. 转义双引号
                escaped_text = text.replace('"', '\\"')
                
                generated_content += f'    old "{escaped_text}"\n'
                generated_content += f'    new ""\n\n'
            
            # 写入文件
            mode = 'a' if os.path.exists(filepath) else 'w'
            with open(filepath, mode, encoding=config.encoding) as f:
                f.write(generated_content)
                
            self.logger.debug(f"成功写入 {len(entries)} 个翻译条目到 {filepath}")
            
            # 发布文件保存事件
            publish(EventNames.FILE_SAVED, filepath=filepath, entry_count=len(entries), format="renpy")
            
            return True
            
        except Exception as e:
            self.logger.error(f"写入文件 {filepath} 失败: {str(e)}")
            return False
    
    def _handle_overwrite_mode(self, filepath: str, config: Any) -> None:
        """
        处理覆盖模式下的文件清理
        
        Args:
            filepath: 当前正在处理的文件路径
            config: 配置对象
        """
        # 获取翻译目录
        translation_dir = os.path.join(config.game_dir, config.translation_dir)
        
        # 检查是否已经清理过目录（使用临时标记避免重复清理）
        if not hasattr(config, "_dir_cleaned") or not config._dir_cleaned:
            # 如果目录存在，直接清空rpy文件，不再创建备份
            if os.path.exists(translation_dir):
                try:
                    # 清空翻译目录下的.rpy文件
                    for rpy_file in glob.glob(os.path.join(translation_dir, "**", "*.rpy"), recursive=True):
                        os.remove(rpy_file)
                    self.logger.info(f"已清空翻译目录中的.rpy文件")
                except Exception as e:
                    self.logger.error(f"清空翻译目录时出错: {str(e)}")
            
            # 设置标记，避免重复清理
            config._dir_cleaned = True
    
    def get_writer(self, name: str) -> Optional[Callable]:
        """
        获取指定名称的写入器，只支持renpy格式
        
        Args:
            name: 写入器名称
            
        Returns:
            写入器函数，如果不存在则返回None
        """
        # 不论传入什么名称，总是返回renpy写入器
        return self.writers["renpy"]
    
    def get_all_writers(self) -> Dict[str, Callable]:
        """
        获取所有注册的写入器
        
        Returns:
            所有写入器的字典
        """
        return self.writers.copy()
    
    def write_translation_file(self, name: str, filepath: str, entries: List[Tuple[int, str]], 
                              rel_path: str, config: Any) -> bool:
        """
        使用renpy写入器写入翻译文件
        
        Args:
            name: 写入器名称
            filepath: 目标文件路径
            entries: 需要写入的条目列表 [(行号, 文本)]
            rel_path: 源文件相对路径
            config: 配置对象
            
        Returns:
            写入是否成功
        """
        # 忽略name参数，总是使用renpy写入器
        return self._write_renpy_translation(filepath, entries, rel_path, config)
