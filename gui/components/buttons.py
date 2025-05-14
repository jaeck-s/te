from PyQt5.QtWidgets import QPushButton, QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from .styles import StyleManager

class ActionButton(QPushButton):
    """
    通用操作按钮，提供统一的外观和行为
    使用StyleManager提供的样式
    """
    
    def __init__(self, text, parent=None, button_type="primary", icon=None):
        """
        初始化操作按钮
        
        Args:
            text: 按钮文字
            parent: 父组件
            button_type: 按钮类型 (primary, success, danger, default)
            icon: 按钮图标 (QIcon)
        """
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setMinimumHeight(StyleManager.SIZES["button_height"])
        
        # 设置图标
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(StyleManager.SIZES["icon_size"], StyleManager.SIZES["icon_size"]))
        
        # 应用样式
        self.setStyleSheet(StyleManager.get_button_stylesheet(button_type))
        self._original_text = text
        self._button_type = button_type
    
    def set_loading_state(self, is_loading):
        """
        设置按钮加载状态
        
        Args:
            is_loading: 是否处于加载状态
        """
        self.setEnabled(not is_loading)
        
        if is_loading:
            self.setText("处理中...")
            # 在加载状态下可以使用不同的样式
            if self._button_type == "primary":
                self.setStyleSheet(StyleManager.get_button_stylesheet("default"))
        else:
            self.setText(self._original_text)
            self.setStyleSheet(StyleManager.get_button_stylesheet(self._button_type))


class BrowseButton(QPushButton):
    """
    用于浏览文件或目录的按钮
    使用StyleManager提供的样式
    """
    
    def __init__(self, text="浏览...", parent=None, icon=None):
        """
        初始化浏览按钮
        
        Args:
            text: 按钮文字
            parent: 父组件
            icon: 按钮图标 (QIcon)
        """
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)  # 固定大小
        # 设置固定宽度，使其不影响布局
        self.setFixedWidth(80)
        
        # 设置图标
        if icon:
            self.setIcon(icon)
            self.setIconSize(QSize(StyleManager.SIZES["icon_size"], StyleManager.SIZES["icon_size"]))
        
        # 浏览按钮使用默认样式
        self.setStyleSheet(StyleManager.get_button_stylesheet("default"))


class IconButton(QPushButton):
    """
    图标按钮，主要显示图标，文字可选
    """
    
    def __init__(self, icon, text="", parent=None, tooltip="", size=None):
        """
        初始化图标按钮
        
        Args:
            icon: 按钮图标 (QIcon)
            text: 按钮文字，默认为空
            parent: 父组件
            tooltip: 提示文本
            size: 图标大小，如果为None则使用默认大小
        """
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        
        # 设置图标
        self.setIcon(icon)
        icon_size = size if size else StyleManager.SIZES["icon_size"]
        self.setIconSize(QSize(icon_size, icon_size))
        
        # 如果没有文字，则将按钮设置为方形
        if not text:
            self.setFixedSize(icon_size + 8, icon_size + 8)
        
        # 设置提示
        if tooltip:
            self.setToolTip(tooltip)
        
        # 应用透明样式
        self.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 3px;
            }
            QPushButton:pressed {
                background-color: rgba(0, 0, 0, 0.2);
            }
        """)
