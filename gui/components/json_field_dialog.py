"""
JSON字段编辑对话框组件
用于添加或编辑要提取的JSON字段
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                           QPushButton, QTextEdit, QMessageBox, QWidget, QCheckBox,
                           QScrollArea)
from PyQt5.QtCore import Qt
import json
import os

class JsonFieldItem(QWidget):
    """表示JSON字段列表中的单个项目"""
    
    def __init__(self, field_name, description="", enabled=True, parent=None):
        super().__init__(parent)
        self.field_name = field_name
        self.enabled = enabled
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 创建复选框用于启用/禁用字段
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(enabled)
        layout.addWidget(self.checkbox)
        
        # 创建标签显示字段名
        self.label = QLabel(field_name)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, 1)  # 设置伸展系数为1，使标签占据大部分空间
        
        # 添加描述标签(如果有)
        if description:
            desc_label = QLabel(f"({description})")
            desc_label.setStyleSheet("color: #666666;")
            layout.addWidget(desc_label)
        
        # 判断并设置复选框状态改变的连接
        self.checkbox.stateChanged.connect(self.on_state_changed)
    
    def is_enabled(self):
        """返回字段是否启用"""
        return self.checkbox.isChecked()
    
    def on_state_changed(self, state):
        """复选框状态改变时更新enabled属性"""
        self.enabled = bool(state)

class JsonFieldDialog(QDialog):
    """JSON字段编辑对话框，用于添加或编辑要提取的JSON字段"""
    
    def __init__(self, parent=None, config_path=None):
        """
        初始化对话框
        
        Args:
            parent: 父组件
            config_path: 配置文件路径
        """
        super().__init__(parent)
        self.setWindowTitle("添加自定义JSON字段")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # 设置配置文件路径
        self.config_path = config_path
        if not self.config_path:
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "configs", "json_fields.json"
            )
        
        # 存储字段项目的字典 {field_name: JsonFieldItem}
        self.field_items = {}
        
        # 初始化布局和组件
        self.setup_ui()
        
        # 加载现有字段
        self.load_existing_fields()
        
    def setup_ui(self):
        """设置UI组件"""
        # 主布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        layout.addWidget(QLabel("请输入要提取的JSON字段名："))
        
        # 添加输入区域
        input_layout = QHBoxLayout()
        
        # 添加字段名输入框
        self.field_edit = QLineEdit()
        self.field_edit.setPlaceholderText("例如：dialog_text")
        input_layout.addWidget(self.field_edit, 1)
        
        # 添加描述输入框
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("描述（可选）")
        input_layout.addWidget(self.description_edit, 1)
        
        # 添加添加按钮
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_field)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        
        # 添加现有字段标签和全选/反选按钮
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("已存在的JSON字段："))
        
        # 全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_fields)
        self.select_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.select_all_btn)
        
        # 反选按钮
        self.deselect_all_btn = QPushButton("反选")
        self.deselect_all_btn.clicked.connect(self.toggle_all_fields)
        self.deselect_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(header_layout)
        
        # 创建滚动区域用于显示已存在的字段
        self.fields_scroll_area = QScrollArea()
        self.fields_scroll_area.setWidgetResizable(True)
        self.fields_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建包含字段列表的容器
        self.fields_container = QWidget()
        self.fields_layout = QVBoxLayout(self.fields_container)
        self.fields_layout.setSpacing(1)
        self.fields_layout.setAlignment(Qt.AlignTop)
        
        # 设置滚动区域的内容
        self.fields_scroll_area.setWidget(self.fields_container)
        layout.addWidget(self.fields_scroll_area)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        # 添加保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_fields)
        
        # 添加取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        # 添加删除未选中按钮
        self.delete_selected_btn = QPushButton("删除未选中")
        self.delete_selected_btn.clicked.connect(self.delete_disabled_fields)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_selected_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_field(self):
        """添加新的字段到列表"""
        field_name = self.field_edit.text().strip()
        description = self.description_edit.text().strip()
        
        if not field_name:
            QMessageBox.warning(self, "警告", "请输入有效的字段名")
            return
        
        # 检查是否已存在
        if field_name in self.field_items:
            QMessageBox.information(self, "提示", f"字段 '{field_name}' 已存在")
            return
        
        # 创建新的字段项
        field_item = JsonFieldItem(field_name, description, True)
        self.fields_layout.addWidget(field_item)
        self.field_items[field_name] = field_item
        
        # 清空输入框
        self.field_edit.clear()
        self.description_edit.clear()
        self.field_edit.setFocus()
    
    def load_existing_fields(self):
        """加载现有的JSON字段"""
        fields = []
        field_data = {}  # 存储字段数据 {name: {description, enabled}}
        
        try:
            # 如果配置文件存在，则读取
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    field_data = data.get("fields", {})
                    fields = list(field_data.keys())
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载JSON字段时出错: {str(e)}")
        
        # 清理现有列表
        for i in reversed(range(self.fields_layout.count())):
            item = self.fields_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # 清空字段项目字典
        self.field_items.clear()
        
        # 显示现有字段
        for field_name in fields:
            field_info = field_data.get(field_name, {})
            description = field_info.get("description", "")
            enabled = field_info.get("enabled", True)
            
            field_item = JsonFieldItem(field_name, description, enabled)
            self.fields_layout.addWidget(field_item)
            self.field_items[field_name] = field_item
        
        # 如果没有字段，添加提示
        if not fields:
            empty_label = QLabel("(暂无自定义JSON字段)")
            empty_label.setAlignment(Qt.AlignCenter)
            self.fields_layout.addWidget(empty_label)
            self.fields_layout.addStretch(1)
    
    def select_all_fields(self):
        """全选所有字段"""
        for field_item in self.field_items.values():
            field_item.checkbox.setChecked(True)
    
    def toggle_all_fields(self):
        """反选所有字段"""
        for field_item in self.field_items.values():
            field_item.checkbox.setChecked(not field_item.checkbox.isChecked())
    
    def delete_disabled_fields(self):
        """删除所有未选中的字段"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除", 
            "确定要删除所有未选中的字段吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
            
        # 创建要保留的字段数据
        fields_to_keep = {}
        for field_name, item in self.field_items.items():
            if item.is_enabled():
                fields_to_keep[field_name] = {
                    "description": item.label.text() if hasattr(item, 'description') else "",
                    "enabled": True
                }
        
        # 保存更新后的字段到文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"fields": fields_to_keep}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"已删除 {len(self.field_items) - len(fields_to_keep)} 个未选中的字段")
            
            # 重新加载字段列表
            self.load_existing_fields()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除字段时出错: {str(e)}")
    
    def save_fields(self):
        """保存字段配置"""
        try:
            # 创建字段数据字典
            field_data = {}
            for field_name, item in self.field_items.items():
                field_data[field_name] = {
                    "description": getattr(item, 'description', ""),
                    "enabled": item.is_enabled()
                }
            
            # 保存到文件
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"fields": field_data}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "已保存JSON字段配置")
            
            # 清空输入框，以备继续添加
            self.field_edit.clear()
            self.description_edit.clear()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存JSON字段配置时出错: {str(e)}")
