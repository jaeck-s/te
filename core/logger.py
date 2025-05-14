"""
全局日志管理模块
提供统一的日志记录和管理功能
"""
import os
import logging
import datetime
from typing import Optional, Callable, List, ClassVar

class Logger:
    """日志管理器，提供统一的日志记录接口"""
    
    _instance: ClassVar[Optional['Logger']] = None  # 单例实例
    
    @classmethod
    def instance(cls) -> 'Logger':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = Logger()
        return cls._instance
    
    def __init__(self) -> None:
        """初始化日志管理器"""
        # 防止重复初始化
        if Logger._instance is not None:
            return
            
        # 创建日志目录
        self.log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        
        # 创建日志记录器
        self.logger = logging.getLogger("translation_extractor")
        self.logger.setLevel(logging.DEBUG)
        
        # 清除已存在的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建文件处理器
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(self.log_dir, f"extractor_{timestamp}.log")
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 设置格式
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s', 
                                     datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # 用于UI回调的列表
        self.ui_callbacks: List[Callable[[str], None]] = []
    
    def add_ui_callback(self, callback: Callable[[str], None]) -> None:
        """添加UI日志回调函数"""
        if callback not in self.ui_callbacks:
            self.ui_callbacks.append(callback)
    
    def remove_ui_callback(self, callback: Callable[[str], None]):
        """移除UI日志回调函数"""
        if callback in self.ui_callbacks:
            self.ui_callbacks.remove(callback)
    
    def _notify_ui(self, message: str):
        """通知所有UI回调"""
        for callback in self.ui_callbacks:
            try:
                callback(message)
            except Exception as e:
                self.logger.error(f"UI回调异常: {str(e)}")
    
    def debug(self, message: str):
        """记录调试级别日志"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """记录信息级别日志"""
        self.logger.info(message)
        self._notify_ui(message)
    
    def warning(self, message: str):
        """记录警告级别日志"""
        self.logger.warning(message)
        self._notify_ui(f"⚠️ {message}")
    
    def error(self, message: str):
        """记录错误级别日志"""
        self.logger.error(message)
        self._notify_ui(f"❌ {message}")
    
    def critical(self, message: str):
        """记录严重错误级别日志"""
        self.logger.critical(message)
        self._notify_ui(f"🔥 {message}")

# 提供便捷访问方式
def get_logger() -> Logger:
    """获取日志管理器实例"""
    return Logger.instance()

# 提供便捷函数
def debug(message: str):
    """记录调试级别日志"""
    get_logger().debug(message)

def info(message: str):
    """记录信息级别日志"""
    get_logger().info(message)

def warning(message: str):
    """记录警告级别日志"""
    get_logger().warning(message)

def error(message: str):
    """记录错误级别日志"""
    get_logger().error(message)

def critical(message: str):
    """记录严重错误级别日志"""
    get_logger().critical(message)
