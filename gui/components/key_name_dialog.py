"""
键名编辑对话框组件
用于添加或编辑要提取的键名
"""
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QTextEdit, QMessageBox, QListWidget,
                            QListWidgetItem, QCheckBox, QWidget, QScrollArea)
from PyQt5.QtCore import Qt
import json
import os

class KeyNameListItem(QWidget):
    """表示键名列表中的单个项目"""
    
    def __init__(self, key_name, enabled=True, parent=None):
        super().__init__(parent)
        self.key_name = key_name
        self.enabled = enabled
        
        # 创建水平布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 2, 5, 2)
        
        # 创建复选框用于启用/禁用键名
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(enabled)
        layout.addWidget(self.checkbox)
        
        # 创建标签显示键名
        self.label = QLabel(key_name)
        self.label.setWordWrap(True)
        layout.addWidget(self.label, 1)  # 设置伸展系数为1，使标签占据大部分空间
        
        # 判断并设置复选框状态改变的连接
        self.checkbox.stateChanged.connect(self.on_state_changed)
    
    def is_enabled(self):
        """返回键名是否启用"""
        return self.checkbox.isChecked()
    
    def on_state_changed(self, state):
        """复选框状态改变时更新enabled属性"""
        self.enabled = bool(state)

class KeyNameDialog(QDialog):
    """键名编辑对话框，用于添加或编辑要提取的键名"""
    
    def __init__(self, parent=None, config_path=None):
        """
        初始化对话框
        
        Args:
            parent: 父组件
            config_path: 配置文件路径
        """
        super().__init__(parent)
        self.setWindowTitle("添加键名")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # 设置配置文件路径
        self.config_path = config_path
        if not self.config_path:
            self.config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                "configs", "dict_keys.json"
            )
        
        # 存储键名项目的字典 {key_name: KeyNameListItem}
        self.key_items = {}
        
        # 初始化布局和组件
        self.setup_ui()
        
        # 加载现有键名
        self.load_existing_keys()
        
    def setup_ui(self):
        """设置UI组件"""
        # 主布局
        layout = QVBoxLayout(self)
        
        # 添加说明标签
        layout.addWidget(QLabel("请输入要提取字符串的键名："))
        layout.addWidget(QLabel("(多个键名请每行输入一个，不需要添加引号和冒号)"))
        
        # 添加输入框
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("例如：\naction_damaged_clothing\ngirl.has_trait('onanist')\nperson_doing_action != player")
        self.text_edit.setMaximumHeight(150)
        layout.addWidget(self.text_edit)
        
        # 添加现有键名标签和全选/反选按钮
        header_layout = QHBoxLayout()
        header_layout.addWidget(QLabel("已存在的键名："))
        
        # 全选按钮
        self.select_all_btn = QPushButton("全选")
        self.select_all_btn.clicked.connect(self.select_all_keys)
        self.select_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.select_all_btn)
        
        # 反选按钮
        self.deselect_all_btn = QPushButton("反选")
        self.deselect_all_btn.clicked.connect(self.toggle_all_keys)
        self.deselect_all_btn.setFixedWidth(60)
        header_layout.addWidget(self.deselect_all_btn)
        
        layout.addLayout(header_layout)
        
        # 创建滚动区域用于显示已存在的键名
        self.keys_scroll_area = QScrollArea()
        self.keys_scroll_area.setWidgetResizable(True)
        self.keys_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建包含键名列表的容器
        self.keys_container = QWidget()
        self.keys_layout = QVBoxLayout(self.keys_container)
        self.keys_layout.setSpacing(1)
        self.keys_layout.setAlignment(Qt.AlignTop)
        
        # 设置滚动区域的内容
        self.keys_scroll_area.setWidget(self.keys_container)
        layout.addWidget(self.keys_scroll_area)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        
        # 添加保存按钮
        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_keys)
        
        # 添加取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        
        # 添加删除选中按钮
        self.delete_selected_btn = QPushButton("删除未选中")
        self.delete_selected_btn.clicked.connect(self.delete_disabled_keys)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.delete_selected_btn)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_existing_keys(self):
        """加载现有的键名"""
        keys = []
        key_states = {}  # 存储键名的启用状态
        
        try:
            # 如果配置文件存在，则读取
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # 兼容旧格式：如果是简单列表则所有键默认启用
                    if isinstance(data.get("key_names"), list):
                        keys = data.get("key_names", [])
                        key_states = {key: True for key in keys}
                    # 新格式：键名是字典，包含启用状态
                    elif isinstance(data.get("key_names"), dict):
                        key_states = data.get("key_names", {})
                        keys = list(key_states.keys())
        except Exception as e:
            QMessageBox.warning(self, "错误", f"加载现有键名时出错: {str(e)}")
        
        # 清理现有列表
        for i in reversed(range(self.keys_layout.count())):
            item = self.keys_layout.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()
        
        # 清空键项目字典
        self.key_items.clear()
        
        # 显示现有键名，包括启用/禁用状态
        for key in keys:
            enabled = key_states.get(key, True)
            key_item = KeyNameListItem(key, enabled)
            self.keys_layout.addWidget(key_item)
            self.key_items[key] = key_item
        
        # 如果没有键名，添加提示
        if not keys:
            empty_label = QLabel("(暂无键名)")
            empty_label.setAlignment(Qt.AlignCenter)
            self.keys_layout.addWidget(empty_label)
            self.keys_layout.addStretch(1)
    
    def select_all_keys(self):
        """全选所有键名"""
        for key_item in self.key_items.values():
            key_item.checkbox.setChecked(True)
    
    def toggle_all_keys(self):
        """反选所有键名"""
        for key_item in self.key_items.values():
            key_item.checkbox.setChecked(not key_item.checkbox.isChecked())
    
    def delete_disabled_keys(self):
        """删除所有未选中的键名"""
        # 确认对话框
        reply = QMessageBox.question(
            self,
            "确认删除", 
            "确定要删除所有未选中的键名吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.No:
            return
            
        # 创建要保留的键名列表
        keys_to_keep = {}
        for key, item in self.key_items.items():
            if item.is_enabled():
                keys_to_keep[key] = True
        
        # 保存更新后的键名到文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"key_names": keys_to_keep}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", f"已删除 {len(self.key_items) - len(keys_to_keep)} 个未选中的键名")
            
            # 重新加载键名列表
            self.load_existing_keys()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除键名时出错: {str(e)}")
    
    def save_keys(self):
        """保存键名"""
        # 获取输入的键名，只按行分割
        text = self.text_edit.toPlainText()
        input_keys = [line.strip() for line in text.split('\n') if line.strip()]
        
        if not input_keys:
            # 如果没有新键名，检查是否有启用/禁用状态变更
            self.save_key_states()
            return
        
        try:
            # 读取现有配置
            key_states = {}
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 兼容旧格式：如果是简单列表则所有键默认启用
                    if isinstance(data.get("key_names"), list):
                        key_states = {key: True for key in data.get("key_names", [])}
                    # 新格式：键名是字典，包含启用状态
                    elif isinstance(data.get("key_names"), dict):
                        key_states = data.get("key_names", {})
            
            # 更新现有键名的启用状态
            for key, item in self.key_items.items():
                key_states[key] = item.is_enabled()
            
            # 检查并统计重复的键名
            duplicate_keys = []
            new_keys = []
            for key in input_keys:
                if key in key_states:
                    duplicate_keys.append(key)
                else:
                    new_keys.append(key)
                    key_states[key] = True  # 新键默认启用
            
            # 如果存在重复键名，显示提示
            if duplicate_keys:
                duplicate_message = f"以下键名已存在，将被跳过:\n{', '.join(duplicate_keys)}"
                QMessageBox.information(self, "发现重复键名", duplicate_message)
            
            # 如果没有新键名，提示用户
            if not new_keys:
                QMessageBox.information(self, "提示", "所有输入的键名都已存在，没有添加新键名。")
            
            # 保存回文件
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"key_names": key_states}, f, ensure_ascii=False, indent=2)
            
            # 更新成功消息
            if new_keys:
                QMessageBox.information(self, "成功", f"成功添加 {len(new_keys)} 个新键名")
            
            # 清空输入框，方便继续输入
            self.text_edit.clear()
            
            # 更新已存在键名的显示
            self.load_existing_keys()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存键名时出错: {str(e)}")
    
    def save_key_states(self):
        """仅保存键名的启用/禁用状态"""
        try:
            # 创建键名状态字典
            key_states = {}
            for key, item in self.key_items.items():
                key_states[key] = item.is_enabled()
            
            # 保存到文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"key_names": key_states}, f, ensure_ascii=False, indent=2)
            
            QMessageBox.information(self, "成功", "已保存键名状态")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存键名状态时出错: {str(e)}")
