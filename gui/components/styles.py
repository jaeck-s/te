"""
样式管理模块
提供全局统一的UI样式定义，使界面风格保持一致
"""
from PyQt5.QtGui import QColor, QFont, QPalette
from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit, QApplication
from typing import Dict, Any, Optional

class StyleManager:
    """样式管理器，提供统一的应用风格"""
    
    # 颜色定义
    COLORS = {
        "primary": "#3498db",       # 主色调
        "primary_dark": "#2980b9",  # 深色主色调
        "primary_light": "#5dade2", # 浅色主色调
        "secondary": "#27ae60",     # 次要色调
        "accent": "#e74c3c",        # 强调色
        "warning": "#f39c12",       # 警告色
        "error": "#c0392b",         # 错误色
        "success": "#2ecc71",       # 成功色
        "background": "#f5f5f5",    # 背景色
        "surface": "#ffffff",       # 表面色
        "text": "#2c3e50",          # 主要文本色
        "text_secondary": "#7f8c8d", # 次要文本色
        "disabled": "#bdc3c7",      # 禁用状态色
        "border": "#d0d0d0",        # 边框色
    }
    
    # 字体定义
    FONTS = {
        "default": QFont("Microsoft YaHei UI", 9),     # 默认字体
        "title": QFont("Microsoft YaHei UI", 12, QFont.Bold),  # 标题字体
        "subtitle": QFont("Microsoft YaHei UI", 10, QFont.Bold), # 小标题字体
        "monospace": QFont("Consolas", 9)   # 等宽字体
    }
    
    # 尺寸定义
    SIZES = {
        "button_height": 36,         # 按钮高度
        "input_height": 30,          # 输入框高度
        "padding": 8,                # 基本内边距
        "margin": 10,                # 基本外边距
        "border_radius": 4,          # 边框圆角
        "icon_size": 16,             # 图标大小
    }
    
    @classmethod
    def apply_default_theme(cls, app: QApplication) -> None:
        """应用默认主题到整个应用程序"""
        # 设置应用程序调色板
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(cls.COLORS["background"]))
        palette.setColor(QPalette.WindowText, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.Base, QColor(cls.COLORS["surface"]))
        palette.setColor(QPalette.AlternateBase, QColor(cls.COLORS["background"]))
        palette.setColor(QPalette.ToolTipBase, QColor(cls.COLORS["surface"]))
        palette.setColor(QPalette.ToolTipText, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.Text, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.Button, QColor(cls.COLORS["background"]))
        palette.setColor(QPalette.ButtonText, QColor(cls.COLORS["text"]))
        palette.setColor(QPalette.Link, QColor(cls.COLORS["primary"]))
        palette.setColor(QPalette.Highlight, QColor(cls.COLORS["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor(cls.COLORS["surface"]))
        
        # 禁用状态颜色
        palette.setColor(QPalette.Disabled, QPalette.Text, QColor(cls.COLORS["disabled"]))
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor(cls.COLORS["disabled"]))
        
        app.setPalette(palette)
        app.setFont(cls.FONTS["default"])
    
    @staticmethod
    def get_button_stylesheet(button_type: str = "default") -> str:
        """获取按钮样式表"""
        styles = {
            "default": f"""
                QPushButton {{
                    background-color: {StyleManager.COLORS["background"]};
                    color: {StyleManager.COLORS["text"]};
                    border: 1px solid {StyleManager.COLORS["border"]};
                    border-radius: {StyleManager.SIZES["border_radius"]}px;
                    padding: {StyleManager.SIZES["padding"]}px;
                    min-height: {StyleManager.SIZES["button_height"]}px;
                }}
                QPushButton:hover {{
                    background-color: #e0e0e0;
                }}
                QPushButton:pressed {{
                    background-color: #d0d0d0;
                }}
                QPushButton:disabled {{
                    background-color: #f0f0f0;
                    color: {StyleManager.COLORS["disabled"]};
                }}
            """,
            "primary": f"""
                QPushButton {{
                    background-color: {StyleManager.COLORS["primary"]};
                    color: white;
                    border: none;
                    border-radius: {StyleManager.SIZES["border_radius"]}px;
                    padding: {StyleManager.SIZES["padding"]}px;
                    min-height: {StyleManager.SIZES["button_height"]}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {StyleManager.COLORS["primary_dark"]};
                }}
                QPushButton:pressed {{
                    background-color: #1c6ea4;
                }}
                QPushButton:disabled {{
                    background-color: {StyleManager.COLORS["disabled"]};
                    color: white;
                }}
            """,
            "success": f"""
                QPushButton {{
                    background-color: {StyleManager.COLORS["success"]};
                    color: white;
                    border: none;
                    border-radius: {StyleManager.SIZES["border_radius"]}px;
                    padding: {StyleManager.SIZES["padding"]}px;
                    min-height: {StyleManager.SIZES["button_height"]}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #27ae60;
                }}
                QPushButton:pressed {{
                    background-color: #219955;
                }}
                QPushButton:disabled {{
                    background-color: {StyleManager.COLORS["disabled"]};
                    color: white;
                }}
            """,
            "danger": f"""
                QPushButton {{
                    background-color: {StyleManager.COLORS["error"]};
                    color: white;
                    border: none;
                    border-radius: {StyleManager.SIZES["border_radius"]}px;
                    padding: {StyleManager.SIZES["padding"]}px;
                    min-height: {StyleManager.SIZES["button_height"]}px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #a93226;
                }}
                QPushButton:pressed {{
                    background-color: #922b21;
                }}
                QPushButton:disabled {{
                    background-color: {StyleManager.COLORS["disabled"]};
                    color: white;
                }}
            """
        }
        return styles.get(button_type, styles["default"])
    
    @staticmethod
    def get_input_stylesheet() -> str:
        """获取输入框样式表"""
        return f"""
            QLineEdit, QTextEdit, QComboBox, QSpinBox {{
                background-color: {StyleManager.COLORS["surface"]};
                color: {StyleManager.COLORS["text"]};
                border: 1px solid {StyleManager.COLORS["border"]};
                border-radius: {StyleManager.SIZES["border_radius"]}px;
                padding: {StyleManager.SIZES["padding"]}px;
                min-height: {StyleManager.SIZES["input_height"]}px;
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus {{
                border: 1px solid {StyleManager.COLORS["primary"]};
            }}
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled {{
                background-color: #f0f0f0;
                color: {StyleManager.COLORS["disabled"]};
            }}
            QComboBox::drop-down {{
                border: none;
                width: 20px;
            }}
        """
    
    @staticmethod
    def get_label_stylesheet(label_type: str = "default") -> str:
        """获取标签样式表"""
        styles = {
            "default": f"""
                QLabel {{
                    color: {StyleManager.COLORS["text"]};
                }}
            """,
            "title": f"""
                QLabel {{
                    color: {StyleManager.COLORS["text"]};
                    font-size: 16px;
                    font-weight: bold;
                }}
            """,
            "subtitle": f"""
                QLabel {{
                    color: {StyleManager.COLORS["text"]};
                    font-size: 14px;
                    font-weight: bold;
                }}
            """,
            "description": f"""
                QLabel {{
                    color: {StyleManager.COLORS["text_secondary"]};
                    font-style: italic;
                }}
            """
        }
        return styles.get(label_type, styles["default"])
    
    @staticmethod
    def get_groupbox_stylesheet() -> str:
        """获取分组框样式表"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                border: 1px solid {StyleManager.COLORS["border"]};
                border-radius: {StyleManager.SIZES["border_radius"]}px;
                margin-top: 20px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px;
            }}
        """
    
    @staticmethod
    def get_progressbar_stylesheet() -> str:
        """获取进度条样式表"""
        return f"""
            QProgressBar {{
                border: 1px solid {StyleManager.COLORS["border"]};
                border-radius: {StyleManager.SIZES["border_radius"]}px;
                text-align: center;
                background-color: {StyleManager.COLORS["background"]};
                min-height: 18px;
            }}
            QProgressBar::chunk {{
                background-color: {StyleManager.COLORS["primary"]};
                border-radius: 2px;
            }}
        """
    
    @staticmethod
    def apply_style_to_widget(widget: QWidget, style_type: Optional[str] = None) -> None:
        """根据组件类型应用适当的样式到组件"""
        if isinstance(widget, QPushButton):
            if style_type in ["primary", "success", "danger"]:
                widget.setStyleSheet(StyleManager.get_button_stylesheet(style_type))
            else:
                widget.setStyleSheet(StyleManager.get_button_stylesheet())
        elif isinstance(widget, QLineEdit):
            widget.setStyleSheet(StyleManager.get_input_stylesheet())
        elif isinstance(widget, QLabel):
            # 修复类型错误: 确保传递给 get_label_stylesheet 的参数是字符串而非 None
            widget.setStyleSheet(StyleManager.get_label_stylesheet(style_type or "default"))
