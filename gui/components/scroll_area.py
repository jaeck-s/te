"""
滚动区域组件
用于为任何选项卡内容提供滚动功能
"""
from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

class ScrollArea(QScrollArea):
    """
    通用滚动区域组件，可包装任何QWidget使其具备滚动功能
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置滚动区域属性
        self.setWidgetResizable(True)  # 允许内容小部件调整大小
        self.setFrameShape(QScrollArea.NoFrame)  # 不显示边框
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示水平滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # 需要时显示垂直滚动条
        
        # 创建内容小部件和布局
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 设置内容小部件为滚动区域的小部件
        self.setWidget(self.content_widget)
    
    def layout(self):
        """获取内容布局"""
        return self.content_layout
    
    def add_widget(self, widget):
        """添加小部件到内容布局"""
        self.content_layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加布局到内容布局"""
        self.content_layout.addLayout(layout)
