"""
事件管理模块
提供统一的事件发布-订阅机制，用于应用程序内部组件间通信
"""
from typing import Dict, List, Callable, Any, Optional
from .logger import get_logger

class EventManager:
    """事件管理器，提供事件的发布和订阅功能"""
    
    _instance: Optional['EventManager'] = None  # 单例实例
    
    @classmethod
    def instance(cls) -> 'EventManager':
        """获取单例实例"""
        if cls._instance is None:
            cls._instance = EventManager()
        return cls._instance
    
    def __init__(self) -> None:
        """初始化事件管理器"""
        # 防止重复初始化
        if EventManager._instance is not None:
            return
            
        self.logger = get_logger()
        # 事件订阅字典 {event_name: [callback1, callback2, ...]}
        self.subscribers: Dict[str, List[Callable[..., None]]] = {}
        self.logger.debug("事件管理器初始化完成")
        
    def subscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        """
        订阅事件
        
        Args:
            event_name: 事件名称
            callback: 事件回调函数
        """
        if event_name not in self.subscribers:
            self.subscribers[event_name] = []
        
        if callback not in self.subscribers[event_name]:
            self.subscribers[event_name].append(callback)
            self.logger.debug(f"已订阅事件 '{event_name}'")
    
    def unsubscribe(self, event_name: str, callback: Callable[..., None]) -> None:
        """
        取消订阅事件
        
        Args:
            event_name: 事件名称
            callback: 事件回调函数
        """
        if event_name in self.subscribers and callback in self.subscribers[event_name]:
            self.subscribers[event_name].remove(callback)
            self.logger.debug(f"已取消订阅事件 '{event_name}'")
            
            # 如果没有订阅者了，清理事件
            if not self.subscribers[event_name]:
                del self.subscribers[event_name]
    
    def publish(self, event_name: str, **kwargs: Any) -> None:
        """
        发布事件
        
        Args:
            event_name: 事件名称
            **kwargs: 事件参数
        """
        if event_name not in self.subscribers:
            return
            
        for callback in self.subscribers[event_name]:
            try:
                callback(**kwargs)
            except Exception as e:
                self.logger.error(f"执行事件 '{event_name}' 回调时出错: {str(e)}")
    
    def clear_all_subscribers(self) -> None:
        """清除所有订阅者"""
        self.subscribers.clear()
        self.logger.debug("已清除所有事件订阅")
    
    def clear_event(self, event_name: str) -> None:
        """
        清除特定事件的所有订阅者
        
        Args:
            event_name: 事件名称
        """
        if event_name in self.subscribers:
            del self.subscribers[event_name]
            self.logger.debug(f"已清除事件 '{event_name}' 的所有订阅")

# 常用事件名称定义
class EventNames:
    """预定义的事件名称"""
    # 应用程序事件
    APP_INIT = "app:init"                  # 应用程序初始化
    APP_EXIT = "app:exit"                  # 应用程序退出
    
    # 提取相关事件
    EXTRACTION_STARTED = "extraction:started"  # 开始提取
    EXTRACTION_PROGRESS = "extraction:progress"  # 提取进度更新
    EXTRACTION_COMPLETED = "extraction:completed"  # 提取完成
    EXTRACTION_ERROR = "extraction:error"  # 提取错误
    
    # 配置相关事件
    CONFIG_CHANGED = "config:changed"  # 配置变更
    
    # 文件操作事件
    FILE_SAVED = "file:saved"  # 文件保存
    FILE_LOADED = "file:loaded"  # 文件加载

# 提供便捷访问方式
def get_event_manager() -> EventManager:
    """获取事件管理器实例"""
    return EventManager.instance()

# 提供便捷函数
def subscribe(event_name: str, callback: Callable[..., None]) -> None:
    """订阅事件"""
    get_event_manager().subscribe(event_name, callback)

def unsubscribe(event_name: str, callback: Callable[..., None]) -> None:
    """取消订阅事件"""
    get_event_manager().unsubscribe(event_name, callback)

def publish(event_name: str, **kwargs: Any) -> None:
    """发布事件"""
    get_event_manager().publish(event_name, **kwargs)
