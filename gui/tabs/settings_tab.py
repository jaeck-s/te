"""
设置选项卡模块
用于显示和管理应用程序的设置选项
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                            QGroupBox, QFormLayout, QComboBox, QGridLayout, QPushButton,
                            QMessageBox)
import os
from core.factories.extractor_factory import ExtractorFactory
from core.factories.validator_factory import ValidatorFactory
from core.config import TranslationConfig
from core.events import publish, EventNames
from gui.tabs.base_tab import BaseTab

class SettingsTab(BaseTab):
    """设置选项卡，包含应用程序的各种设置选项"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI控件的引用
        self.extractor_checkboxes = {}
        self.validator_checkboxes = {}
        self.encoding_combo = None
        self.recursive_checkbox = None
        self.skip_translated_checkbox = None
        self.file_format_checkboxes = {}
        self.person_name_writer_checkbox = None
        
        # 设置布局
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 配置保存/加载区域
        self.add_widget(self.create_config_management_group())
        
        # 文件格式选择区域
        self.add_widget(self.create_file_format_group())
        
        # 提取模式区域
        self.add_widget(self.create_extraction_modes_group())
        
        # 其他设置区域
        self.add_widget(self.create_other_settings_group())
        
        # 添加弹性空间使控件垂直靠上
        self.add_stretch()
        
    def create_config_management_group(self):
        """创建配置管理设置组"""
        config_group = QGroupBox("配置管理")
        config_layout = QHBoxLayout()
        
        # 简化的配置管理，只有保存和加载按钮
        save_btn = QPushButton("保存当前配置")
        save_btn.setToolTip("保存当前配置作为默认配置，下次启动时会自动加载")
        save_btn.clicked.connect(self.save_current_config)
        
        reset_btn = QPushButton("重置配置")
        reset_btn.setToolTip("重置为默认配置")
        reset_btn.clicked.connect(self.reset_config)
        
        config_layout.addWidget(save_btn)
        config_layout.addWidget(reset_btn)
        
        config_group.setLayout(config_layout)
        return config_group
        
    def create_file_format_group(self):
        """创建文件格式选择组"""
        file_format_group = QGroupBox("文件格式")
        file_format_layout = QVBoxLayout()
        
        # 提示文本
        file_format_layout.addWidget(QLabel("选择要处理的文件格式:"))
        
        # 文件格式复选框
        formats = {
            "rpy": "Ren'Py脚本文件 (*.rpy)",
            "json": "JSON数据文件 (*.json)"
        }
        
        for format_id, display_name in formats.items():
            checkbox = QCheckBox(display_name)
            # RPY格式默认选中
            checkbox.setChecked(format_id == "rpy")
            checkbox.stateChanged.connect(self.on_file_format_changed)
            self.file_format_checkboxes[format_id] = checkbox
            file_format_layout.addWidget(checkbox)
        
        file_format_group.setLayout(file_format_layout)
        return file_format_group
    
    def create_extraction_modes_group(self):
        """创建提取模式设置组"""
        extraction_modes_group = QGroupBox("提取模式管理")
        extraction_modes_layout = QVBoxLayout()
        
        # 提示文本
        extraction_modes_layout.addWidget(QLabel("在此设置中您可以启用或禁用特定的提取模式:"))
        
        # 提取模式分组（按文件格式）
        rpy_modes_group = QGroupBox("RPY文件提取模式")
        rpy_modes_layout = QGridLayout()
        
        json_modes_group = QGroupBox("JSON文件提取模式")
        json_modes_layout = QGridLayout()
        
        # 获取所有提取器
        extractor_factory = ExtractorFactory()
        all_extractors = extractor_factory.get_all_extractors()
        
        rpy_row = 0
        json_row = 0
        
        for name in sorted(all_extractors.keys()):
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)  # 默认全部启用
            
            # 为复选框添加描述标签并判断属于哪种文件格式
            description = ""
            file_format = "rpy"  # 默认为RPY格式
            
            if name == "description":
                description = "提取属性值 'description'"
            elif name == "purchase_notification":
                description = "提取属性值 'purchase_notification'"
            elif name == "unlock_notification":
                description = "提取属性值 'unlock_notification'"
            elif name == "json_display_name":
                file_format = "json"
                description = "从JSON文件中提取 'display_name' 字段"
            elif name == "json_person_name":
                file_format = "json"
                description = "从JSON文件中提取 'first_name'和'last_name' 字段"
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666666; font-style: italic;")
            
            # 根据文件格式分配到不同组
            if file_format == "json":
                json_modes_layout.addWidget(checkbox, json_row, 0)
                json_modes_layout.addWidget(desc_label, json_row, 1)
                json_row += 1
                # 给复选框添加标记，方便后续联动处理
                checkbox.setProperty("file_format", "json")
            else:
                rpy_modes_layout.addWidget(checkbox, rpy_row, 0)
                rpy_modes_layout.addWidget(desc_label, rpy_row, 1)
                rpy_row += 1
                # 给复选框添加标记，方便后续联动处理
                checkbox.setProperty("file_format", "rpy")
            
            self.extractor_checkboxes[name] = checkbox
        
        # 设置分组布局
        rpy_modes_group.setLayout(rpy_modes_layout)
        json_modes_group.setLayout(json_modes_layout)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_extractors)
        
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all_extractors)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(deselect_all_btn)
        buttons_layout.addStretch()  # 添加弹性空间
        
        # 添加分组和按钮到主布局
        extraction_modes_layout.addWidget(rpy_modes_group)
        extraction_modes_layout.addWidget(json_modes_group)
        extraction_modes_layout.addLayout(buttons_layout)
        
        extraction_modes_group.setLayout(extraction_modes_layout)
        
        # 初始化文件格式对应的提取模式可用性
        self.update_extraction_modes_availability()
        
        return extraction_modes_group
    
    def create_other_settings_group(self):
        """创建其他设置组"""
        other_settings_group = QGroupBox("其他设置")
        other_settings_layout = QFormLayout()
        
        # 提取选项区域
        extraction_options_layout = QVBoxLayout()
        
        # 是否递归搜索子目录
        self.recursive_checkbox = QCheckBox("递归搜索子目录")
        self.recursive_checkbox.setChecked(True)
        self.recursive_checkbox.setToolTip("启用后将搜索所有子目录中的文件")
        extraction_options_layout.addWidget(self.recursive_checkbox)

        # 是否跳过已翻译的条目
        self.skip_translated_checkbox = QCheckBox("跳过已翻译的条目")
        self.skip_translated_checkbox.setChecked(True)
        self.skip_translated_checkbox.setToolTip("启用后将跳过已经存在翻译的条目")
        extraction_options_layout.addWidget(self.skip_translated_checkbox)
        
        # 添加人名处理选项
        self.person_name_writer_checkbox = QCheckBox("使用人名专用写入器")
        self.person_name_writer_checkbox.setChecked(False)
        self.person_name_writer_checkbox.setToolTip("启用后将为JSON文件中的first_name和last_name生成特殊的翻译条目")
        extraction_options_layout.addWidget(self.person_name_writer_checkbox)
        
        other_settings_layout.addRow("提取选项:", extraction_options_layout)
        
        # 编码设置
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "gbk", "cp932", "latin1", "ascii"])
        other_settings_layout.addRow("文件编码:", self.encoding_combo)
        
        # 验证器设置区域
        validator_layout = QVBoxLayout()
        validator_layout.addWidget(QLabel("启用的文本验证器:"))
        
        # 验证器复选框
        validator_factory = ValidatorFactory()
        all_validators = validator_factory.get_all_validators()
        
        # 验证器中文显示名称映射
        validator_display_names = {
            "non_empty": "非空验证 (过滤空文本)",
            "has_alphanumeric": "字母数字验证 (确保包含字母或数字)",
            "no_invalid_chars": "无效字符验证 (过滤包含无效字符的文本)",
            "string_consistency": "字符串一致性 (确保提取的字符串与游戏显示一致)",
            "global_deduplicate": "全局去重 (避免生成重复的翻译条目)"
        }
        
        for name in sorted(all_validators.keys()):
            # 使用映射中的中文名称创建复选框
            display_name = validator_display_names.get(name, name)
            checkbox = QCheckBox(display_name)
            # 根据配置设置初始状态
            checkbox.setChecked(name in ["non_empty", "no_invalid_chars"])
            self.validator_checkboxes[name] = checkbox
            validator_layout.addWidget(checkbox)
        
        other_settings_layout.addRow("验证器:", validator_layout)
        
        other_settings_group.setLayout(other_settings_layout)
        return other_settings_group
    
    def select_all_extractors(self):
        """选择所有提取器"""
        for checkbox in self.extractor_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_extractors(self):
        """取消选择所有提取器"""
        for checkbox in self.extractor_checkboxes.values():
            checkbox.setChecked(False)
    
    def get_selected_extractors(self):
        """获取选中的提取器列表"""
        return [name for name, checkbox in self.extractor_checkboxes.items() if checkbox.isChecked()]
    
    def get_selected_validators(self):
        """获取选中的验证器列表"""
        return [name for name, checkbox in self.validator_checkboxes.items() if checkbox.isChecked()]
    
    def get_writer_format(self):
        """获取写入格式，已固定为renpy"""
        return "renpy"
    
    def get_encoding(self):
        """获取选中的编码格式"""
        return self.encoding_combo.currentText()
    
    def on_file_format_changed(self):
        """当文件格式选择变更时更新提取模式的可用性"""
        self.update_extraction_modes_availability()
    
    def update_extraction_modes_availability(self):
        """根据选择的文件格式更新提取模式的可用性"""
        # 获取选中的文件格式
        selected_formats = self.get_selected_file_formats()
        
        # 对每个提取器检查其文件格式
        for name, checkbox in self.extractor_checkboxes.items():
            format_property = checkbox.property("file_format")
            
            if format_property:
                # 如果提取器有文件格式属性，检查该格式是否被选中
                checkbox.setEnabled(format_property in selected_formats)
                if format_property not in selected_formats:
                    checkbox.setChecked(False)
    
    def get_selected_file_formats(self):
        """获取选中的文件格式列表"""
        return [fmt for fmt, checkbox in self.file_format_checkboxes.items() if checkbox.isChecked()]
    
    def get_file_patterns(self):
        """获取基于选中文件格式的文件模式列表"""
        patterns = []
        if "rpy" in self.get_selected_file_formats():
            patterns.append("*.rpy")
        if "json" in self.get_selected_file_formats():
            patterns.append("*.json")
        return patterns
    
    def update_config(self, config):
        """使用当前设置更新配置对象"""
        config.extractors = self.get_selected_extractors()
        config.validators = self.get_selected_validators()
        config.writer_format = self.get_writer_format()  # 总是返回 "renpy"
        config.encoding = self.get_encoding()
        config.recursive = self.recursive_checkbox.isChecked()
        config.skip_translated = self.skip_translated_checkbox.isChecked()
        config.file_patterns = self.get_file_patterns()  # 使用文件格式选择生成文件模式
        
        # 更新人名写入器设置
        config.use_person_name_writer = self.person_name_writer_checkbox.isChecked()
        
        return config
    
    def save_current_config(self):
        """保存当前配置为默认配置"""
        # 获取当前配置
        main_window = self.window()
        if not hasattr(main_window, 'config'):
            QMessageBox.warning(self, "错误", "无法获取当前配置")
            return
            
        # 更新配置
        main_window.update_config()
        
        # 保存配置
        if main_window.config.save_default_config():
            self.logger.info("配置已保存为默认配置")
            QMessageBox.information(self, "成功", "配置已保存为默认配置，下次启动时将自动加载")
        else:
            QMessageBox.warning(self, "错误", "保存配置失败")
    
    def reset_config(self):
        """重置为初始配置"""
        reply = QMessageBox.question(self, "确认重置", 
                                   "确定要重置所有配置吗？这将恢复到初始设置。",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.No:
            return
            
        # 重置配置
        main_window = self.window()
        if hasattr(main_window, 'config'):
            # 创建新配置
            main_window.config = TranslationConfig()
            
            # 更新UI
            main_window.apply_config_to_ui()
            
            # 发布配置变更事件
            publish(EventNames.CONFIG_CHANGED, config=main_window.config)
            
            self.logger.info("配置已重置为初始设置")
            QMessageBox.information(self, "成功", "配置已重置为初始设置")
