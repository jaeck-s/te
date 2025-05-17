"""
设置组件模块
提供设置选项卡使用的可重用组件，减少代码重复
"""
from PyQt5.QtWidgets import (QGroupBox, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, 
                            QPushButton, QWidget, QFormLayout, QScrollArea, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal
import json
import os
from core.factories.extractor_factory import ExtractorFactory

class SettingsGroup(QGroupBox):
    """
    通用设置组组件
    提供统一的设置组布局和功能
    """
    
    def __init__(self, title, parent=None, layout_type="vbox"):
        """
        初始化设置组
        
        Args:
            title: 组标题
            parent: 父组件
            layout_type: 布局类型，支持"vbox"、"hbox"、"form"
        """
        super().__init__(title, parent)
        
        # 根据指定类型创建布局
        if layout_type == "hbox":
            self._layout = QHBoxLayout(self)
        elif layout_type == "form":
            self._layout = QFormLayout(self)
        else:  # 默认为垂直布局
            self._layout = QVBoxLayout(self)
    
    def layout(self):
        """获取布局"""
        return self._layout
    
    def add_widget(self, widget, label=None):
        """
        添加小部件到布局
        
        Args:
            widget: 要添加的小部件
            label: 标签文本，仅用于表单布局
        """
        if isinstance(self._layout, QFormLayout) and label:
            self._layout.addRow(label, widget)
        else:
            self._layout.addWidget(widget)
    
    def add_layout(self, layout):
        """添加子布局"""
        self._layout.addLayout(layout)


class CheckboxOption(QWidget):
    """单个复选框选项，带有描述标签"""
    
    # 状态变更信号
    state_changed = pyqtSignal(str, bool)  # 发出信号：(选项ID, 是否选中)
    
    def __init__(self, option_id, label, description="", checked=False, parent=None):
        """
        初始化复选框选项
        
        Args:
            option_id: 选项ID
            label: 复选框标签文本
            description: 描述文本
            checked: 是否默认选中
            parent: 父组件
        """
        super().__init__(parent)
        self.option_id = option_id
        
        # 创建布局
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建复选框
        self.checkbox = QCheckBox(label)
        self.checkbox.setChecked(checked)
        
        # 连接状态变更信号
        self.checkbox.stateChanged.connect(
            lambda state: self.state_changed.emit(option_id, bool(state))
        )
        
        # 添加复选框到布局
        layout.addWidget(self.checkbox)
        
        # 如果有描述，添加描述标签
        if description:
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666666; font-style: italic;")
            layout.addWidget(desc_label)
        
        # 添加弹性空间
        layout.addStretch()
    
    def is_checked(self):
        """获取是否选中"""
        return self.checkbox.isChecked()
    
    def set_checked(self, checked):
        """设置选中状态"""
        self.checkbox.setChecked(checked)
    
    def set_enabled(self, enabled):
        """设置启用状态"""
        self.checkbox.setEnabled(enabled)
    
    def set_property(self, name, value):
        """设置复选框属性"""
        self.checkbox.setProperty(name, value)
    
    def property(self, name):
        """获取复选框属性"""
        return self.checkbox.property(name)


class OptionsGroup(QGroupBox):
    """选项组，管理多个相关的选项"""
    
    # 任何选项变更时发出的信号
    option_changed = pyqtSignal(str, bool)  # (选项ID, 是否选中)
    
    def __init__(self, title, parent=None):
        """
        初始化选项组
        
        Args:
            title: 组标题
            parent: 父组件
        """
        super().__init__(title, parent)
        
        # 设置垂直布局
        self.main_layout = QVBoxLayout(self)
        
        # 存储选项 {id: option_widget}
        self.options = {}
    
    def add_option(self, option_id, label, description="", checked=False):
        """
        添加选项
        
        Args:
            option_id: 选项ID
            label: 选项标签
            description: 选项描述
            checked: 是否默认选中
            
        Returns:
            创建的选项小部件
        """
        option = CheckboxOption(option_id, label, description, checked, self)
        
        # 连接信号
        option.state_changed.connect(self.on_option_state_changed)
        
        # 添加到布局
        self.main_layout.addWidget(option)
        
        # 保存引用
        self.options[option_id] = option
        
        return option
    
    def on_option_state_changed(self, option_id, checked):
        """处理选项状态变更"""
        # 转发信号
        self.option_changed.emit(option_id, checked)
    
    def get_selected_options(self):
        """
        获取所有选中的选项ID列表
        
        Returns:
            选中的选项ID列表
        """
        return [id for id, option in self.options.items() if option.is_checked()]
    
    def set_option_checked(self, option_id, checked):
        """
        设置选项的选中状态
        
        Args:
            option_id: 选项ID
            checked: 是否选中
        """
        if option_id in self.options:
            self.options[option_id].set_checked(checked)
    
    def set_option_enabled(self, option_id, enabled):
        """
        设置选项的启用状态
        
        Args:
            option_id: 选项ID
            enabled: 是否启用
        """
        if option_id in self.options:
            self.options[option_id].set_enabled(enabled)
    
    def select_all(self):
        """选中所有选项"""
        for option in self.options.values():
            option.set_checked(True)
    
    def clear_all(self):
        """清除所有选项"""
        for option in self.options.values():
            option.set_checked(False)
    
    def set_option_property(self, option_id, prop_name, value):
        """
        设置选项属性
        
        Args:
            option_id: 选项ID
            prop_name: 属性名
            value: 属性值
        """
        if option_id in self.options:
            self.options[option_id].set_property(prop_name, value)
    
    def update_options_by_property(self, prop_name, valid_values, enable_only=False):
        """
        根据属性值更新选项的可用性或选中状态
        
        Args:
            prop_name: 属性名
            valid_values: 有效的属性值列表
            enable_only: 如果为True，仅更新启用状态；如果为False，也会取消选中不可用的选项
        """
        for option in self.options.values():
            prop_value = option.property(prop_name)
            if prop_value:
                is_valid = prop_value in valid_values
                option.set_enabled(is_valid)
                
                if not is_valid and not enable_only:
                    option.set_checked(False)


class ExtractorGroup(QWidget):
    """
    提取器分组组件
    管理所有提取器的显示和交互
    """
    
    def __init__(self, extractor_config=None, parent=None):
        """
        初始化提取器组件
        
        Args:
            extractor_config: 提取器配置数据字典
            parent: 父组件
        """
        super().__init__(parent)
        
        self.extractor_factory = ExtractorFactory()
        if extractor_config is None:
            extractor_config = {}
        
        # 主布局
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # 提取器分组字典
        self.extractor_groups = {}
        
        self._setup_ui(extractor_config)
        
    def _setup_ui(self, extractor_config):
        """设置UI布局和组件"""
        # 创建RPY基本属性组
        rpy_basic_group = QGroupBox("RPY文件基本属性提取")
        rpy_basic_layout = QVBoxLayout(rpy_basic_group)
        
        # 创建RPY字典值组 - 添加新组
        rpy_dict_group = QGroupBox("RPY文件字典值提取")
        rpy_dict_layout = QVBoxLayout(rpy_dict_group)
        
        # 创建RPY函数调用组
        rpy_func_group = QGroupBox("RPY文件函数调用提取")
        rpy_func_layout = QVBoxLayout(rpy_func_group)
        
        # 创建JSON字段组
        json_group = QGroupBox("JSON文件提取")
        json_layout = QVBoxLayout(json_group)
        
        # 初始化组引用
        basic_extractors = {}
        rpy_dict_extractors = {}  # 添加新组引用
        func_extractors = {}
        json_extractors = {}
        
        self.extractor_groups = {
            "basic_props": basic_extractors,
            "rpy_dict": rpy_dict_extractors,  # 注册新的组
            "func_props": func_extractors,
            "json": json_extractors
        }
        
        # 获取所有提取器
        all_extractors = self.extractor_factory.get_all_extractors()
        
        # 遍历所有提取器
        for name in sorted(all_extractors.keys()):
            # 从配置中获取提取器信息
            info = extractor_config.get(name, {
                "group": "basic_props",
                "desc": f"提取 {name}",
                "format": "rpy",
                "default_enabled": True
            })
            
            group = info["group"]
            default_enabled = info.get("default_enabled", True)
            desc = info.get("desc", f"提取 {name}")
            file_format = info.get("format", "rpy")
            
            # 创建选项组件
            option_widget = QWidget()
            option_layout = QHBoxLayout(option_widget)
            option_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建复选框
            checkbox = QCheckBox(name)
            checkbox.setChecked(default_enabled)
            checkbox.setProperty("file_format", file_format)
            
            # 添加到布局
            option_layout.addWidget(checkbox)
            
            # 添加描述标签
            if desc:
                desc_label = QLabel(desc)
                desc_label.setStyleSheet("color: #666666; font-style: italic;")
                option_layout.addWidget(desc_label)
            
            option_layout.addStretch()
            
            # 根据分组将选项添加到对应布局
            if group == "basic_props":
                rpy_basic_layout.addWidget(option_widget)
                basic_extractors[name] = checkbox
            elif group == "rpy_dict":  # 添加新组的处理
                rpy_dict_layout.addWidget(option_widget)
                rpy_dict_extractors[name] = checkbox
            elif group == "func_props":
                rpy_func_layout.addWidget(option_widget)
                func_extractors[name] = checkbox
            elif group == "json":
                json_layout.addWidget(option_widget)
                json_extractors[name] = checkbox
        
        # 添加组到主布局
        self.main_layout.addWidget(rpy_basic_group)
        self.main_layout.addWidget(rpy_dict_group)  # 添加字典提取组到UI
        self.main_layout.addWidget(rpy_func_group)
        self.main_layout.addWidget(json_group)
    
    def get_groups(self):
        """获取提取器组引用"""
        return self.extractor_groups
        
    def get_selected_extractors(self):
        """
        获取所有选中的提取器列表
        
        Returns:
            选中的提取器名称列表
        """
        result = []
        for group in self.extractor_groups.values():
            for name, checkbox in group.items():
                if checkbox.isChecked():
                    result.append(name)
        return result
    
    def update_availability(self, file_formats):
        """根据文件格式更新提取器可用性"""
        for group in self.extractor_groups.values():
            for name, checkbox in group.items():
                format_value = checkbox.property("file_format")
                enabled = format_value in file_formats
                checkbox.setEnabled(enabled)
                if not enabled:
                    checkbox.setChecked(False)
