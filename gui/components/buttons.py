from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import Qt

class ActionButton(QPushButton):
    """通用操作按钮，提供统一的外观和行为"""
    
    def __init__(self, text, parent=None, min_height=40):
        super().__init__(text, parent)
        self.setMinimumHeight(min_height)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
    
    def set_loading_state(self, is_loading):
        """设置按钮加载状态"""
        self.setEnabled(not is_loading)
        if is_loading:
            self.setText("正在处理...")
        else:
            # 恢复原始文本需要在调用此方法时提供
            pass


class BrowseButton(QPushButton):
    """用于浏览文件或目录的按钮"""
    
    def __init__(self, text="浏览...", parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                padding: 4px 8px;
                background-color: #f0f0f0;
                border: 1px solid #cccccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
