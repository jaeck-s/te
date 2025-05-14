import os
import re
import glob
from pathlib import Path
from typing import Dict, List, Tuple, Callable, Set, Optional
from .config import TranslationConfig
from .factories.extractor_factory import ExtractorFactory
from .factories.validator_factory import ValidatorFactory
from .factories.writer_factory import WriterFactory
from .logger import get_logger
from .events import publish, EventNames

class TranslationExtractor:
    """翻译文本提取器"""
    
    def __init__(self, config: TranslationConfig):
        self.config = config
        self.progress_callback = None  # 进度回调函数
        self.log_callback = None       # 日志回调函数
        self.logger = get_logger()     # 使用全局日志管理器
        
        # 初始化工厂实例
        self.extractor_factory = ExtractorFactory()
        self.validator_factory = ValidatorFactory()
        self.writer_factory = WriterFactory()
    
    def log(self, message: str):
        """输出日志"""
        self.logger.info(message)      # 记录到全局日志
        if self.log_callback:
            self.log_callback(message) # 同时调用回调函数
    
    def update_progress(self, current: int, total: int):
        """更新进度"""
        # 发布进度更新事件
        publish(EventNames.EXTRACTION_PROGRESS, current=current, total=total)
        
        # 同时调用回调函数（向后兼容）
        if self.progress_callback:
            self.progress_callback(current, total)
    
    def extract(self) -> int:
        """执行翻译提取，返回生成的条目数"""
        if not self.config.game_dir:
            self.log("错误: 未指定游戏目录")
            return 0
            
        # 重置验证器的去重状态
        self.validator_factory.reset_deduplication()
        
        # 验证游戏目录
        game_dir = os.path.join(self.config.game_dir, "game")
        if not os.path.isdir(game_dir):
            self.log(f"错误: 无效的游戏目录，未找到game文件夹: {game_dir}")
            return 0
            
        # 确保翻译目录存在
        translation_dir = os.path.join(self.config.game_dir, self.config.translation_dir)
        os.makedirs(translation_dir, exist_ok=True)
        
        # 查找所有需要处理的文件
        self.log("正在搜索游戏文件...")
        files_to_process = self._find_files(game_dir)
        if not files_to_process:
            self.log("未找到符合条件的游戏文件")
            return 0
            
        self.log(f"找到{len(files_to_process)}个文件需要处理")
        
        # 第一步：从所有文件中提取字符串
        self.log("正在分析文件内容...")
        file_entries = self._extract_strings(files_to_process)
        
        # 第二步：生成翻译文件
        self.log("正在生成翻译文件...")
        entries_count = self._generate_translation_files(file_entries, translation_dir)
        
        return entries_count
    
    def _find_files(self, game_dir: str) -> List[str]:
        """查找所有需要处理的文件"""
        files = []
        
        if self.config.recursive:
            # 递归搜索所有子目录
            for pattern in self.config.file_patterns:
                found = glob.glob(os.path.join(game_dir, "**", pattern), recursive=True)
                files.extend(found)
        else:
            # 只搜索当前目录
            for pattern in self.config.file_patterns:
                found = glob.glob(os.path.join(game_dir, pattern))
                files.extend(found)
        
        # 跳过翻译目录中的文件
        tl_path = os.path.join(self.config.game_dir, self.config.translation_dir)
        if os.path.exists(tl_path):
            files = [f for f in files if not f.startswith(tl_path)]
        
        return files
    
    def _extract_strings(self, files: List[str]) -> Dict[str, List[Tuple[int, str]]]:
        """从所有文件中提取需要翻译的字符串"""
        file_entries = {}  # {filepath: [(line_num, original_text), ...]}
        seen_strings = set()  # 用于去重
        
        total_files = len(files)
        for i, filepath in enumerate(files):
            try:
                # 更新进度
                self.update_progress(i, total_files)
                
                # 添加文件处理开始的日志
                self.logger.debug(f"正在处理文件: {os.path.basename(filepath)}")
                
                try:
                    # 使用with语句确保文件正确关闭
                    with open(filepath, 'r', encoding=self.config.encoding, errors='replace') as f:
                        content = f.read()
                    
                    # 发布文件加载事件
                    publish(EventNames.FILE_LOADED, filepath=filepath, content_length=len(content))
                    
                    # 使用提取工厂提取文本
                    entries = self.extractor_factory.extract_from_content(content, filepath, self.config.extractors)
                    
                    # 验证提取的文本
                    validated_entries = []
                    for line_num, text in entries:
                        # 使用配置中指定的验证器验证文本是否有效
                        if self.validator_factory.validate_text(text, self.config.validators):
                            validated_entries.append((line_num, text))
                        else:
                            self.logger.debug(f"文本未通过验证: '{text[:30]}...'")
                    
                    # 去重并添加到结果
                    if validated_entries:
                        # 过滤已经见过的字符串
                        unique_entries = []
                        for line_num, text in validated_entries:
                            if text not in seen_strings:
                                seen_strings.add(text)
                                unique_entries.append((line_num, text))
                        
                        if unique_entries:
                            file_entries[filepath] = unique_entries
                            self.log(f"从文件 {os.path.basename(filepath)} 提取了 {len(unique_entries)} 个有效文本条目")
                
                except UnicodeDecodeError as e:
                    self.logger.error(f"文件编码错误 {filepath}: {str(e)}, 尝试跳过该文件")
                    # 发布提取错误事件但继续处理
                    publish(EventNames.EXTRACTION_ERROR, error=str(e), message=f"文件编码错误 {filepath}: {str(e)}")
                    continue
                
                except Exception as e:
                    self.logger.error(f"处理文件出错 {filepath}: {str(e)}")
                    # 发布提取错误事件但继续处理
                    publish(EventNames.EXTRACTION_ERROR, error=str(e), message=f"处理文件出错 {filepath}: {str(e)}")
                    continue
                    
                # 每隔100个文件，强制垃圾回收一次，防止内存占用过高
                if i % 100 == 0:
                    import gc
                    gc.collect()
                    
            except Exception as e:
                self.logger.error(f"文件处理异常 {filepath}: {str(e)}")
                # 发布提取错误事件但继续处理
                publish(EventNames.EXTRACTION_ERROR, error=str(e), message=f"文件处理异常 {filepath}: {str(e)}")
                continue
        
        # 确保最终进度为100%
        self.update_progress(total_files, total_files)
        
        return file_entries
    
    def _generate_translation_files(self, file_entries: Dict[str, List[Tuple[int, str]]], 
                                   translation_dir: str) -> int:
        """生成翻译文件，返回生成的条目数"""
        total_entries = 0
        generated_entries = 0
        
        # 计算总条目数
        for entries in file_entries.values():
            total_entries += len(entries)
        
        if total_entries == 0:
            self.log("没有找到需要翻译的文本")
            return 0
            
        self.log(f"找到{total_entries}个需要翻译的文本条目")
        
        # 处理每个文件
        file_count = 0
        for src_file, entries in file_entries.items():
            if not entries:
                continue
                
            # 计算相对路径
            rel_path = os.path.relpath(src_file, os.path.join(self.config.game_dir, "game"))
            dst_file = os.path.join(translation_dir, rel_path)
            
            # 读取已有翻译（如果存在）
            new_entries = entries
            if os.path.exists(dst_file) and self.config.skip_translated:
                try:
                    with open(dst_file, 'r', encoding=self.config.encoding) as f:
                        content = f.read()
                    
                    # 提取已存在的翻译条目
                    existing_entries = set()
                    for match in re.finditer(r'old\s+(?:"([^"\\]*(?:\\.[^"\\]*)*)"|"""([\s\S]*?)""")', content):
                        text = match.group(1) if match.group(1) is not None else match.group(2)
                        existing_entries.add(text.strip())
                    
                    # 过滤掉已存在的条目
                    new_entries = [(line, text) for line, text in entries 
                                  if text.strip() not in existing_entries]
                except Exception as e:
                    self.logger.warning(f"读取已有翻译文件失败 {dst_file}: {str(e)}")
            
            if not new_entries:
                continue
                
            # 使用写入工厂写入翻译文件，只支持renpy格式
            success = self.writer_factory.write_translation_file(
                "renpy", dst_file, new_entries, rel_path, self.config
            )
            
            if success:
                file_count += 1
                generated_entries += len(new_entries)
                self.log(f"已生成翻译文件: {rel_path} ({len(new_entries)}个条目)")
                
                # 发布文件保存事件
                publish(EventNames.FILE_SAVED, filepath=dst_file, entry_count=len(new_entries))
        
        self.log(f"总计处理了{file_count}个文件，生成了{generated_entries}个翻译条目")
        return generated_entries
