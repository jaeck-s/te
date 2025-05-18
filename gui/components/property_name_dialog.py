"""
属性名编辑对话框组件
用于添加或编辑要提取的自定义属性名
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QTextEdit, QMessageBox, QListWidget,
                            QListWidgetItem, QCheckBox, QWidget, QScrollArea, QComboBox)
from PyQt5.QtCore import Qt
import json
import os

class PropertyListItem(QWidget):
    """表示属性列表中的单个项目"""
    
    def __init__(self, property_name, assignment_type=1, enabled=True, parent=None):
        super().__init__(parent)
        self.property_name = property_name
        self.assignment_type = assignment_type
        self.enabled = enabled
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 创建复选框用于启用/禁用属性
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(enabled)
        layout.addWidget(self.checkbox)
        
        # 创建标签显示属性名
        self.label = QLabel(property_name)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, 1)  # 设置伸展系数为1，使标签占据大部分空间
        
        # 创建标签显示赋值方式
        assignment_text = ["等号赋值", "键值对", "空格隔开"][assignment_type - 1]
        self.type_label = QLabel(f"({assignment_text})")
        layout.addWidget(self.type_label)
        
        # 判断并设置复选框状态改变的连接
        self.checkbox.stateChanged.connect(self.on_state_changed)
    
    def is_enabled(self):
        """返回属性是否启用"""
        return self.checkbox.isChecked()
    
    def on_state_changed(self, state):
        """复选框状态改变时更新enabled属性"""
        self.enabled = bool(state)

class PropertyNameDialog(QDialog):
    """属性名编辑对话框，用于添加或编辑要提取的自定义属性名"""
    
    def __init__(self, parent=None, config_path=None):
        """
        初始化对话框
        
        Args:
            parent: 父组件
            config_path: 配置文件路径
        """
        super().__init__(parent)
        self.setWindowTitle("添加自定义属性名")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # 设置配置文件路径
        self.config_path = config_path
        if not self.config_path:
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "configs", "custom_properties.json"
            )
        
        # 存储属性项目的字典 {property_key: PropertyListItem}
        self.property_items = {}
        
        # 初始化布局和组件
        self.setup_ui()
        
        # 加载现有属性名
        self.load_existing_properties()
        
    def setup_ui(self):
        """设置UI组件"""
        # 主布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        layout.addWidget(QLabel("请输入要提取的自定义属性名："))
        
        # 添加输入区域
        input_layout = QHBoxLayout()
        
        # 添加属性名输入框
        self.property_edit = QLineEdit()
        self.property_edit.setPlaceholderText("例如：custom_description")
        input_layout.addWidget(self.property_edit, 1)  # 占据更多空间
        
        # 添加赋值方式选择
        self.assignment_combo = QComboBox()
        self.assignment_combo.addItems([
            "等号赋值 (name=value)",
            "键值对 (name: value)",
            "空格隔开 (name value)"
        ])
        input_layout.addWidget(self.assignment_combo)
        
        # 添加添加按钮
        add_btn = QPushButton("添加")
        add_btn.clicked.connect(self.add_property)
        input_layout.addWidget(add_btn)
        
        layout.addLayout(input_layout)
        layout.addWidget(QLabel("提示：等号赋值会自动处理等号两边是否有空格的情况，键值对会自动处理引号"))
        
        # 添加现有属性名标签和全选/反选按钮
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("已存在的自定义属性名："))
        
        # 全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_properties)
        self.select_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.select_all_btn)
        
        # 反选按钮
        self.deselect_all_btn = QPushButton("反选")
        self.deselect_all_btn.clicked.connect(self.toggle_all_properties)
        self.deselect_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(header_layout)
        
        # 创建滚动区域用于显示已存在的属性名
        self.properties_scroll_area = QScrollArea()
        self.properties_scroll_area.setWidgetResizable(True)
        self.properties_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建包含属性列表的容器
        self.properties_container = QWidget()
        self.properties_layout = QVBoxLayout(self.properties_container)
        self.properties_layout.setSpacing(1)
        self.properties_layout.setAlignment(Qt.AlignTop)
        
        # 设置滚动区域的内容
        self.properties_scroll_area.setWidget(self.properties_container)
        layout.addWidget(self.properties_scroll_area)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        # 添加保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_properties)
        
        # 添加取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        # 添加删除未选中按钮
        self.delete_selected_btn = QPushButton("删除未选中")
        self.delete_selected_btn.clicked.connect(self.delete_disabled_properties)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_selected_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def add_property(self):
        """添加新的属性到列表"""
        property_name = self.property_edit.text().strip()
        if not property_name:
            QMessageBox.warning(self, "警告", "请输入有效的属性名")
            return
        
        # 获取赋值方式 (1: 等号赋值, 2: 键值对, 3: 空格隔开)
        assignment_type = self.assignment_combo.currentIndex() + 1
        
        # 生成属性的唯一标识符，格式为 "属性名:赋值类型"
        property_key = f"{property_name}:{assignment_type}"
        
        # 检查是否已存在同名且同赋值方式的属性
        if property_key in self.property_items:
            QMessageBox.information(self, "提示", f"属性名 '{property_name}' (赋值方式: {self.assignment_combo.currentText()}) 已存在")
            return
        
        # 创建新的属性项
        property_item = PropertyListItem(property_name, assignment_type, True)
        self.properties_layout.addWidget(property_item)
        self.property_items[property_key] = property_item
        
        # 清空输入框
        self.property_edit.clear()
        self.property_edit.setFocus()
    
    def load_existing_properties(self):
        """加载现有的属性名"""
        prop_list = []  # 属性列表
        
        try:
            # 如果配置文件存在，则读取
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    prop_list = data.get("properties", [])
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载现有属性名时出错: {str(e)}")
        
        # 清理现有列表
        for i in reversed(range(self.properties_layout.count())):
            item = self.properties_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # 清空属性项目字典
        self.property_items.clear()
        
        # 显示现有属性名，包括赋值方式和启用/禁用状态
        for prop_info in prop_list:
            prop_name = prop_info.get("name", "")
            assignment_type = prop_info.get("type", 1)
            enabled = prop_info.get("enabled", True)
            
            if prop_name:  # 确保属性名非空
                # 生成属性键
                property_key = f"{prop_name}:{assignment_type}"
                
                property_item = PropertyListItem(prop_name, assignment_type, enabled)
                self.properties_layout.addWidget(property_item)
                self.property_items[property_key] = property_item
        
        # 如果没有属性，添加提示
        if not self.property_items:
            empty_label = QLabel("(暂无自定义属性)")
            empty_label.setAlignment(Qt.AlignCenter)
            self.properties_layout.addWidget(empty_label)
            self.properties_layout.addStretch(1)
    
    def select_all_properties(self):
        """全选所有属性"""
        for prop_item in self.property_items.values():
            prop_item.checkbox.setChecked(True)
    
    def toggle_all_properties(self):
        """反选所有属性"""
        for prop_item in self.property_items.values():
            prop_item.checkbox.setChecked(not prop_item.checkbox.isChecked())
    
    def delete_disabled_properties(self):
        """删除所有未选中的属性"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除", 
            "确定要删除所有未选中的属性吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
            
        # 创建要保留的属性列表
        properties_to_keep = []
        for property_key, item in self.property_items.items():
            if item.is_enabled():
                properties_to_keep.append({
                    "name": item.property_name,
                    "type": item.assignment_type,
                    "enabled": True
                })
        
        # 保存更新后的属性到文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"properties": properties_to_keep}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"已删除 {len(self.property_items) - len(properties_to_keep)} 个未选中的属性")
            
            # 重新加载属性列表
            self.load_existing_properties()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除属性时出错: {str(e)}")
    
    def save_properties(self):
        """保存属性配置"""
        try:
            # 创建属性数据列表
            properties_list = []
            for property_key, item in self.property_items.items():
                properties_list.append({
                    "name": item.property_name,
                    "type": item.assignment_type,
                    "enabled": item.is_enabled()
                })
            
            # 保存到文件
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"properties": properties_list}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "已保存属性配置")
            
            # 设置结果为接受，触发主窗口的更新逻辑
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存属性配置时出错: {str(e)}")
