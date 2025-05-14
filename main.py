import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QTextCursor

# 移除无法导入的 qRegisterMetaType 函数
# 不再需要注册元类型，因为我们将使用更安全的方法处理跨线程信号

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

if __name__ == "__main__":
    sys.exit(main())
