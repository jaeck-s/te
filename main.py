import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextCursor

from gui.main_window import MainWindow
from core.logger import get_logger
from core.events import get_event_manager, EventNames, publish
from gui.components.styles import StyleManager
from core.config import TranslationConfig

def main():
    # 确保工作目录正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化日志系统
    logger = get_logger()
    logger.info("应用程序启动")
    
    try:
        # 发布应用程序初始化事件
        publish(EventNames.APP_INIT)
        
        # 创建dict_keys.json默认文件（如果不存在）
        ensure_dict_keys_file()
        
        # 创建并加载默认配置
        config = TranslationConfig()
        config.load_default_config()  # 尝试加载默认配置，如果不存在则使用初始值
        
        # 启动应用程序
        app = QApplication(sys.argv)
        
        # 应用默认主题样式
        StyleManager.apply_default_theme(app)
        
        window = MainWindow(config)  # 传递配置给主窗口
        window.show()
        
        exit_code = app.exec_()
        logger.info(f"应用程序退出，退出码: {exit_code}")
        
        # 发布应用程序退出事件
        publish(EventNames.APP_EXIT, exit_code=exit_code)
        
        return exit_code
    except Exception as e:
        logger.critical(f"应用程序异常: {str(e)}")
        return 1

def ensure_dict_keys_file():
    """确保dict_keys.json文件存在，如果不存在则创建"""
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "configs", "dict_keys.json")
    
    if not os.path.exists(config_path):
        # 创建目录（如果不存在）
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # 默认键名列表
        default_keys = [
            "generic", "broke", "modest", "brilliant", "obedient", "sharp", "rich", "famous",
            "cold", "rebellious", "stressed", "isinstance(girl, Mother)",
            "person_doing_action != player", "girl.get_tracked_action_count('fuck_ass') < 9",
            "person_getting_line == player", "action_damaged_clothing", "action_damaged_clothing > 2", 
            "girl.part_covered_by_clothing('panties')",
            "selected_clothing_item and selected_clothing_item.owner.id == selected_girl.id",
            "girl.has_trait('onanist')"
        ]
        
        # 创建默认配置
        with open(config_path, 'w', encoding='utf-8') as f:
            import json
            json.dump({"key_names": default_keys}, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    sys.exit(main())
