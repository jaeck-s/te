import sys
import os
from PyQt5.QtWidgets import QApplication
from gui.main_window import MainWindow
from core.logger import get_logger

def main():
    # 确保工作目录正确
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # 初始化日志系统
    logger = get_logger()
    logger.info("应用程序启动")
    
    try:
        # 启动应用程序
        app = QApplication(sys.argv)
        app.setStyle("Fusion")  # 使用Fusion风格以获得更一致的跨平台外观
        window = MainWindow()
        window.show()
        
        exit_code = app.exec_()
        logger.info(f"应用程序退出，退出码: {exit_code}")
        return exit_code
    except Exception as e:
        logger.critical(f"应用程序异常: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
