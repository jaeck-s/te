"""
设置选项卡模块
用于显示和管理应用程序的设置选项
"""
from PyQt5.QtWidgets import (QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
                            QGroupBox, QFormLayout, QComboBox, QPushButton,
                            QMessageBox, QWidget)
import os
import json
from core.factories.extractor_factory import ExtractorFactory
from core.factories.validator_factory import ValidatorFactory
from core.config import TranslationConfig
from core.events import publish, EventNames
from gui.tabs.base_tab import BaseTab
from gui.components.settings_components import (SettingsGroup, OptionsGroup, ExtractorGroup)

class SettingsTab(BaseTab):
    """设置选项卡，包含应用程序的各种设置选项"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI控件的引用
        self.extractor_groups = {}  # 存储提取器组引用
        self.validator_group = None  # 验证器组引用
        self.encoding_combo = None
        self.recursive_option = None
        self.skip_translated_option = None
        self.file_format_options = None  # 文件格式选项组
        self.person_name_writer_option = None
        
        # 提取器映射，用于反向查找
        self.extractor_map = {}
        
        # 加载提取器配置信息
        self.extractor_config = self.load_extractor_config()
        
        # 加载验证器配置信息
        self.validator_config = self.load_validator_config()
        
        # 设置布局
        self.setup_ui()
        
    def load_extractor_config(self):
        """加载提取器配置信息"""
        # 配置文件路径
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                  "configs", "extractors.json")
        
        # 如果配置文件存在，则加载
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载提取器配置失败: {str(e)}")
        
        # 如果配置文件不存在或加载失败，返回空字典
        # 这将使UI依赖于工厂中的提取器注册
        return {}
        
    def load_validator_config(self):
        """加载验证器配置信息"""
        # 配置文件路径
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                                  "configs", "validators.json")
        
        # 如果配置文件存在，则加载
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"加载验证器配置失败: {str(e)}")
        
        # 如果配置文件不存在或加载失败，返回空字典
        return {}
    
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
        config_group = SettingsGroup("配置管理", layout_type="hbox")
        
        # 简化的配置管理，只有保存和加载按钮
        save_btn = QPushButton("保存当前配置")
        save_btn.setToolTip("保存当前配置作为默认配置，下次启动时会自动加载")
        save_btn.clicked.connect(self.save_current_config)
        
        reset_btn = QPushButton("重置配置")
        reset_btn.setToolTip("重置为默认配置")
        reset_btn.clicked.connect(self.reset_config)
        
        config_group.add_widget(save_btn)
        config_group.add_widget(reset_btn)
        
        return config_group
        
    def create_file_format_group(self):
        """创建文件格式选择组"""
        file_format_group = SettingsGroup("文件格式")
        
        # 提示文本
        file_format_group.add_widget(QLabel("选择要处理的文件格式:"))
        
        # 创建文件格式选项组
        self.file_format_options = OptionsGroup("")
        self.file_format_options.setStyleSheet("QGroupBox { border: none; }")
        
        # 添加文件格式选项
        formats = {
            "rpy": "Ren'Py脚本文件 (*.rpy)",
            "json": "JSON数据文件 (*.json)"
        }
        
        for format_id, display_name in formats.items():
            option = self.file_format_options.add_option(
                format_id, display_name, checked=(format_id == "rpy")
            )
        
        # 连接文件格式变更信号
        self.file_format_options.option_changed.connect(self.on_file_format_changed)
        
        file_format_group.add_widget(self.file_format_options)
        
        return file_format_group
    
    def create_extraction_modes_group(self):
        """创建提取模式设置组"""
        extraction_modes_group = SettingsGroup("提取模式管理")
        
        # 提示文本
        extraction_modes_group.add_widget(QLabel("在此设置中您可以启用或禁用特定的提取模式:"))
        
        # 创建提取器组 - 正确传递extractor_config参数
        extractor_group = ExtractorGroup(self.extractor_config)
        self.extractor_groups = extractor_group.get_groups()
        
        extraction_modes_group.add_widget(extractor_group)
        
        # 创建按钮区域
        button_layout = QHBoxLayout()
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_extractors)
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all_extractors)
        button_layout.addWidget(select_all_btn)
        button_layout.addWidget(deselect_all_btn)
        button_layout.addStretch()
        extraction_modes_layout = extraction_modes_group.layout()
        extraction_modes_layout.addLayout(button_layout)
        
        # 初始化可用性
        self.update_extraction_modes_availability()
        
        return extraction_modes_group
    
    def create_other_settings_group(self):
        """创建其他设置组"""
        other_settings_group = SettingsGroup("其他设置", layout_type="form")
        
        # 提取选项区域
        extraction_options = OptionsGroup("")
        extraction_options.setStyleSheet("QGroupBox { border: none; }")
        
        # 是否递归搜索子目录
        self.recursive_option = extraction_options.add_option(
            "recursive", "递归搜索子目录", 
            "启用后将搜索所有子目录中的文件", True
        )

        # 是否跳过已翻译的条目
        self.skip_translated_option = extraction_options.add_option(
            "skip_translated", "跳过已翻译的条目",
            "启用后将跳过已经存在翻译的条目", True
        )
        
        # 添加人名处理选项
        self.person_name_writer_option = extraction_options.add_option(
            "person_name_writer", "使用人名专用写入器",
            "启用后将为JSON文件中的first_name和last_name生成特殊的翻译条目", False
        )
        
        other_settings_group.add_widget(extraction_options, "提取选项:")
        
        # 编码设置
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "gbk", "cp932", "latin1", "ascii"])
        other_settings_group.add_widget(self.encoding_combo, "文件编码:")
        
        # 验证器设置
        self.validator_group = OptionsGroup("文本验证器")
        
        # 验证器复选框
        validator_factory = ValidatorFactory()
        all_validators = validator_factory.get_all_validators()
        
        for name in sorted(all_validators.keys()):
            # 从配置中获取验证器信息，如果找不到则使用简单的默认值
            info = self.validator_config.get(name, {
                "desc": name,
                "default_enabled": name in ["non_empty", "no_invalid_chars"]
            })
            
            self.validator_group.add_option(
                name, 
                info["desc"],
                checked=info["default_enabled"]
            )
        
        other_settings_group.add_widget(self.validator_group, "验证器:")
        
        return other_settings_group
    
    def on_extractor_changed(self, extractor_id, checked):
        """处理提取器状态变更"""
        # 此处可添加额外的联动逻辑
        pass
    
    def on_file_format_changed(self, format_id, checked):
        """处理文件格式变更"""
        self.update_extraction_modes_availability()
    
    def select_all_extractors(self):
        """选择所有提取器"""
        for group in self.extractor_groups.values():
            for checkbox in group.values():
                checkbox.setChecked(True)
    
    def deselect_all_extractors(self):
        """取消选择所有提取器"""
        for group in self.extractor_groups.values():
            for checkbox in group.values():
                checkbox.setChecked(False)
    
    def update_extraction_modes_availability(self):
        """根据选择的文件格式更新提取模式的可用性"""
        # 获取选中的文件格式
        selected_formats = self.get_selected_file_formats()
        
        # 更新各组的可用性
        for group in self.extractor_groups.values():
            for name, checkbox in group.items():
                format_property = checkbox.property("file_format")
                if format_property:
                    checkbox.setEnabled(format_property in selected_formats)
                    if format_property not in selected_formats:
                        checkbox.setChecked(False)
    
    def get_selected_file_formats(self):
        """获取选中的文件格式列表"""
        return self.file_format_options.get_selected_options()
    
    def get_file_patterns(self):
        """获取基于选中文件格式的文件模式列表"""
        return [f"*.{fmt}" for fmt in self.get_selected_file_formats()]
    
    def get_selected_extractors(self):
        """获取选中的提取器列表"""
        result = []
        for group in self.extractor_groups.values():
            for name, checkbox in group.items():
                if checkbox.isChecked():
                    result.append(name)
        return result
    
    def get_selected_validators(self):
        """获取选中的验证器列表"""
        return self.validator_group.get_selected_options()
    
    def get_writer_format(self):
        """获取写入格式，已固定为renpy"""
        return "renpy"
    
    def get_encoding(self):
        """获取选中的编码格式"""
        return self.encoding_combo.currentText()
    
    def update_config(self, config):
        """使用当前设置更新配置对象"""
        config.extractors = self.get_selected_extractors()
        config.validators = self.get_selected_validators()
        config.writer_format = self.get_writer_format()
        config.encoding = self.get_encoding()
        config.recursive = self.recursive_option.is_checked()
        config.skip_translated = self.skip_translated_option.is_checked()
        config.file_patterns = self.get_file_patterns()
        
        # 更新人名写入器设置
        config.use_person_name_writer = self.person_name_writer_option.is_checked()
        
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
