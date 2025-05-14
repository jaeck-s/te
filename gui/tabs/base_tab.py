"""
基础选项卡类模块
为所有选项卡提供通用功能
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QHBoxLayout, QLabel
from PyQt5.QtCore import Qt
from gui.components.scroll_area import ScrollArea
from core.logger import get_logger

class BaseTab(QWidget):
    """
    基础选项卡类，提供通用功能如滚动区域
    所有其他选项卡类可以继承此类以获得这些功能
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        self.scroll_area = ScrollArea()
        self.main_layout.addWidget(self.scroll_area)
        
        # 内容布局引用，子类可以使用此布局添加组件
        self.content_layout = self.scroll_area.layout()
    
    def add_widget(self, widget):
        """添加小部件到内容布局"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到内容布局"""
        self.content_layout.addLayout(layout)
    
    def add_stretch(self):
        """在内容末尾添加弹性空间"""
        self.content_layout.addStretch(1)
    
    def create_group(self, title, layout=None):
        """
        创建一个带标题的组框
        
        Args:
            title: 组框标题
            layout: 组框内部布局，如果为None则创建垂直布局
            
        Returns:
            组框对象和其内部布局
        """
        group = QGroupBox(title)
        if layout is None:
            layout = QVBoxLayout()
        group.setLayout(layout)
        return group
    
    def create_section_with_label(self, label_text, label_width=70):
        """
        创建一个带有固定宽度标签的水平布局区域
        
        Args:
            label_text: 标签文本
            label_width: 标签宽度
            
        Returns:
            元组: (section_layout, container_widget, container_layout)
        """
        section = QHBoxLayout()
        section.setContentsMargins(5, 5, 5, 5)
        
        # 创建固定宽度的标签
        label = QLabel(label_text)
        label.setFixedWidth(label_width)
        section.addWidget(label)
        
        # 创建容器
        container = QWidget()
        container_layout = QHBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)
        
        # 添加容器到区域
        section.addWidget(container)
        
        return section, container, container_layout
    
    def log(self, message):
        """记录日志"""
        self.logger.info(message)
