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
        self.validators = ["non_empty", "no_invalid_chars"]  # 默认启用的验证器
        
        # 写入设置
        self.writer_format = "renpy"    # 输出文件格式
        
        # 其他设置
        self.encoding = "utf-8"      # 文件编码
        self.max_threads = 1         # 最大线程数（暂时未使用）
