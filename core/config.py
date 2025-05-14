import os
import json
from typing import Dict, Any, List

class TranslationConfig:
    """翻译提取的配置参数"""
    
    def __init__(self):
        # 游戏相关目录
        self.game_dir = ""           # 游戏根目录
        self.translation_dir = "game/tl/schinese"  # 翻译目录（相对于游戏目录）
        
        # 提取设置
        self.file_patterns = ["*.rpy"]  # 要处理的文件模式列表
        self.recursive = True           # 是否递归处理子目录
        self.skip_translated = True     # 是否跳过已翻译的条目
        
        # 提取规则
        self.extractors = []
        
        # 验证设置
        self.validators = ["non_empty", "no_invalid_chars", "string_consistency", "global_deduplicate"]  # 更新默认启用的验证器
        
        # 写入设置
        self.writer_format = "renpy"    # 输出文件格式，固定为renpy
        self.write_mode = "append"      # 写入模式: append(追加) 或 overwrite(覆盖)
        
        # 人名处理设置
        self.use_person_name_writer = False  # 是否启用人名专用写入器
        
        # 其他设置
        self.encoding = "utf-8"      # 文件编码
        self.max_threads = 1         # 最大线程数（暂时未使用）
        
        # 配置文件路径
        self.config_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "configs")
        os.makedirs(self.config_folder, exist_ok=True)
        self.default_config_file = os.path.join(self.config_folder, "default_config.json")
    
    def to_dict(self) -> Dict[str, Any]:
        """将配置转换为字典"""
        return {
            "game_dir": self.game_dir,
            "translation_dir": self.translation_dir,
            "file_patterns": self.file_patterns,
            "recursive": self.recursive,
            "skip_translated": self.skip_translated,
            "extractors": self.extractors,
            "validators": self.validators,
            "writer_format": self.writer_format,
            "write_mode": self.write_mode,  # 添加写入模式
            "use_person_name_writer": self.use_person_name_writer,  # 添加人名写入器设置
            "encoding": self.encoding,
            "max_threads": self.max_threads
        }
    
    def from_dict(self, data: Dict[str, Any]) -> 'TranslationConfig':
        """从字典加载配置"""
        if "game_dir" in data:
            self.game_dir = data["game_dir"]
        if "translation_dir" in data:
            self.translation_dir = data["translation_dir"]
        if "file_patterns" in data:
            self.file_patterns = data["file_patterns"]
        if "recursive" in data:
            self.recursive = data["recursive"]
        if "skip_translated" in data:
            self.skip_translated = data["skip_translated"]
        if "extractors" in data:
            self.extractors = data["extractors"]
        if "validators" in data:
            self.validators = data["validators"]
        if "writer_format" in data:
            self.writer_format = data["writer_format"]
        if "write_mode" in data:
            self.write_mode = data["write_mode"]
        if "use_person_name_writer" in data:
            self.use_person_name_writer = data["use_person_name_writer"]
        if "encoding" in data:
            self.encoding = data["encoding"]
        if "max_threads" in data:
            self.max_threads = data["max_threads"]
        return self
    
    def save_default_config(self) -> bool:
        """保存默认配置"""
        try:
            with open(self.default_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {str(e)}")
            return False
    
    def load_default_config(self) -> bool:
        """加载默认配置"""
        try:
            if not os.path.exists(self.default_config_file):
                return False
                
            with open(self.default_config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.from_dict(data)
            return True
        except Exception as e:
            print(f"加载配置失败: {str(e)}")
            return False
