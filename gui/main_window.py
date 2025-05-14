import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QFileDialog, QTextEdit,
                            QProgressBar, QMessageBox, QComboBox, QCheckBox,
                            QGroupBox, QFormLayout, QLineEdit, QSpinBox, QListWidget,
                            QTabWidget, QGridLayout, QPushButton)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.extractor import TranslationExtractor
from core.config import TranslationConfig
from core.factories.extractor_factory import ExtractorFactory
from core.factories.validator_factory import ValidatorFactory
from core.logger import get_logger
from gui.components.buttons import ActionButton, BrowseButton

class ExtractorThread(QThread):
    """执行翻译提取的后台线程"""
    progress_update = pyqtSignal(int, int)  # 发出信号：当前进度, 总数
    log_update = pyqtSignal(str)  # 发出日志信息
    finished_signal = pyqtSignal(bool, str)  # 发出完成信号：成功/失败, 消息

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.extractor = TranslationExtractor(config)
        
    def run(self):
        try:
            # 连接信号
            self.extractor.progress_callback = self.progress_update.emit
            self.extractor.log_callback = self.log_update.emit
            
            # 执行提取
            result = self.extractor.extract()
            if result:
                self.finished_signal.emit(True, f"提取完成，成功生成 {result} 个翻译条目。")
            else:
                self.finished_signal.emit(False, "提取过程没有生成任何新的翻译条目。")
        except Exception as e:
            self.log_update.emit(f"错误: {str(e)}")
            self.finished_signal.emit(False, f"提取失败: {str(e)}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Renpy游戏翻译提取器")
        self.setMinimumSize(800, 600)
        self.config = TranslationConfig()
        
        # 设置日志记录器
        self.logger = get_logger()
        self.logger.add_ui_callback(self.log)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.main_tab = QWidget()
        self.settings_tab = QWidget()
        
        self.tabs.addTab(self.main_tab, "主页")
        self.tabs.addTab(self.settings_tab, "设置")
        
        main_layout.addWidget(self.tabs)
        
        # 设置主选项卡
        self.setup_main_tab()
        
        # 设置设置选项卡
        self.setup_settings_tab()
        
    def setup_main_tab(self):
        # 主选项卡布局
        main_tab_layout = QVBoxLayout(self.main_tab)
        
        # 配置区域
        config_group = QGroupBox("配置")
        config_layout = QFormLayout()
        
        # 游戏目录选择
        game_layout = QHBoxLayout()
        self.game_dir_edit = QLineEdit()
        self.game_dir_edit.setReadOnly(True)
        browse_btn = BrowseButton()
        browse_btn.clicked.connect(self.select_game_dir)
        game_layout.addWidget(self.game_dir_edit)
        game_layout.addWidget(browse_btn)
        config_layout.addRow("游戏目录:", game_layout)
        
        # 翻译目录选择
        tl_layout = QHBoxLayout()
        self.tl_dir_edit = QLineEdit("game/tl/schinese")
        self.tl_dir_edit.setToolTip("相对于游戏目录的翻译文件夹路径")
        tl_layout.addWidget(self.tl_dir_edit)
        config_layout.addRow("翻译目录:", tl_layout)
        
        # 提取选项
        self.file_patterns_edit = QLineEdit("*.rpy")
        self.file_patterns_edit.setToolTip("用逗号分隔的文件模式，例如: *.rpy,*.rpym")
        config_layout.addRow("文件模式:", self.file_patterns_edit)
        
        # 是否递归搜索子目录
        self.recursive_checkbox = QCheckBox("递归搜索子目录")
        self.recursive_checkbox.setChecked(True)
        config_layout.addRow("", self.recursive_checkbox)

        # 是否跳过已翻译的条目
        self.skip_translated_checkbox = QCheckBox("跳过已翻译的条目")
        self.skip_translated_checkbox.setChecked(True)
        config_layout.addRow("", self.skip_translated_checkbox)
        
        config_group.setLayout(config_layout)
        main_tab_layout.addWidget(config_group)
        
        # 操作区域
        actions_layout = QHBoxLayout()
        self.start_btn = ActionButton("开始提取")
        self.start_btn.clicked.connect(self.start_extraction)
        actions_layout.addWidget(self.start_btn)
        main_tab_layout.addLayout(actions_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        main_tab_layout.addLayout(progress_layout)
        
        # 日志输出区域
        log_group = QGroupBox("日志输出")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        main_tab_layout.addWidget(log_group)

        # 默认日志
        self.logger.info("欢迎使用Renpy游戏翻译提取器")
        self.logger.info("请选择游戏目录并配置选项后，点击'开始提取'按钮")
        self.logger.info("当前支持提取以下属性值：description、purchase_notification、unlock_notification")
    
    def setup_settings_tab(self):
        # 设置选项卡布局
        settings_layout = QVBoxLayout(self.settings_tab)
        
        # 提取模式区域
        extraction_modes_group = QGroupBox("提取模式管理")
        extraction_modes_layout = QVBoxLayout()
        
        # 提示文本
        extraction_modes_layout.addWidget(QLabel("在此设置中您可以启用或禁用特定的提取模式:"))
        
        # 提取模式网格
        modes_grid = QGridLayout()
        
        # 每个提取器的启用/禁用复选框
        self.extractor_checkboxes = {}
        
        # 获取所有提取器
        extractor_factory = ExtractorFactory()
        all_extractors = extractor_factory.get_all_extractors()
        
        row = 0
        for name in sorted(all_extractors.keys()):
            checkbox = QCheckBox(name)
            checkbox.setChecked(True)  # 默认全部启用
            
            # 为复选框添加描述标签
            description = ""
            if name == "description":
                description = "提取属性值 'description'"
            elif name == "purchase_notification":
                description = "提取属性值 'purchase_notification'"
            elif name == "unlock_notification":
                description = "提取属性值 'unlock_notification'"
            
            desc_label = QLabel(description)
            desc_label.setStyleSheet("color: #666666; font-style: italic;")
            
            modes_grid.addWidget(checkbox, row, 0)
            modes_grid.addWidget(desc_label, row, 1)
            
            self.extractor_checkboxes[name] = checkbox
            row += 1
        
        extraction_modes_layout.addLayout(modes_grid)
        
        # 按钮区域
        buttons_layout = QHBoxLayout()
        
        select_all_btn = QPushButton("全选")
        select_all_btn.clicked.connect(self.select_all_extractors)
        
        deselect_all_btn = QPushButton("取消全选")
        deselect_all_btn.clicked.connect(self.deselect_all_extractors)
        
        buttons_layout.addWidget(select_all_btn)
        buttons_layout.addWidget(deselect_all_btn)
        buttons_layout.addStretch()  # 添加弹性空间
        
        extraction_modes_layout.addLayout(buttons_layout)
        extraction_modes_group.setLayout(extraction_modes_layout)
        
        # 输出设置区域
        output_settings_group = QGroupBox("输出设置")
        output_settings_layout = QFormLayout()
        
        # 添加写入格式选择
        self.writer_combo = QComboBox()
        self.writer_combo.addItems(["renpy", "json", "csv"])
        self.writer_combo.setToolTip("选择翻译文件的输出格式")
        output_settings_layout.addRow("输出格式:", self.writer_combo)
        
        output_settings_group.setLayout(output_settings_layout)
        
        # 其他设置区域
        other_settings_group = QGroupBox("其他设置")
        other_settings_layout = QFormLayout()
        
        # 编码设置
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["utf-8", "gbk", "cp932", "latin1", "ascii"])
        other_settings_layout.addRow("文件编码:", self.encoding_combo)
        
        # 验证器设置区域
        validator_layout = QVBoxLayout()
        validator_layout.addWidget(QLabel("启用的文本验证器:"))
        
        # 验证器复选框
        self.validator_checkboxes = {}
        validator_factory = ValidatorFactory()
        all_validators = validator_factory.get_all_validators()
        
        # 验证器中文显示名称映射
        validator_display_names = {
            "non_empty": "非空验证 (过滤空文本)",
            "has_alphanumeric": "字母数字验证 (确保包含字母或数字)",
            "no_invalid_chars": "无效字符验证 (过滤包含无效字符的文本)"
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
        
        # 添加到布局
        settings_layout.addWidget(extraction_modes_group)
        settings_layout.addWidget(output_settings_group)
        settings_layout.addWidget(other_settings_group)
        settings_layout.addStretch()  # 添加弹性空间使控件垂直靠上
    
    def select_all_extractors(self):
        """选择所有提取器"""
        for checkbox in self.extractor_checkboxes.values():
            checkbox.setChecked(True)
    
    def deselect_all_extractors(self):
        """取消选择所有提取器"""
        for checkbox in self.extractor_checkboxes.values():
            checkbox.setChecked(False)
    
    def select_game_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "选择游戏目录")
        if dir_path:
            self.game_dir_edit.setText(dir_path)
            # 检查游戏目录是否有效
            if not os.path.exists(os.path.join(dir_path, "game")):
                self.logger.warning(f"所选目录似乎不是一个标准的Renpy游戏目录，未找到game文件夹")
    
    def log(self, message):
        """添加日志到日志文本框"""
        self.log_text.append(message)
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            self.progress_bar.setValue(int(current / total * 100))
        else:
            self.progress_bar.setValue(0)
    
    def start_extraction(self):
        game_dir = self.game_dir_edit.text()
        if not game_dir:
            self.logger.warning("请先选择游戏目录")
            QMessageBox.warning(self, "警告", "请先选择游戏目录")
            return
            
        # 获取选中的提取器
        selected_extractors = [name for name, checkbox in self.extractor_checkboxes.items() 
                              if checkbox.isChecked()]
        
        if not selected_extractors:
            self.logger.warning("请选择至少一个提取器")
            QMessageBox.warning(self, "警告", "请选择至少一个提取器")
            return
            
        # 获取选中的验证器
        selected_validators = [name for name, checkbox in self.validator_checkboxes.items() 
                              if checkbox.isChecked()]
        
        # 更新配置
        self.config.game_dir = game_dir
        self.config.translation_dir = self.tl_dir_edit.text()
        self.config.file_patterns = self.file_patterns_edit.text().split(',')
        self.config.recursive = self.recursive_checkbox.isChecked()
        self.config.skip_translated = self.skip_translated_checkbox.isChecked()
        self.config.extractors = selected_extractors
        self.config.validators = selected_validators  # 将选中的验证器添加到配置
        self.config.encoding = self.encoding_combo.currentText()
        self.config.writer_format = self.writer_combo.currentText()
        
        # 禁用开始按钮
        self.start_btn.set_loading_state(True)
        self.progress_bar.setValue(0)
        self.logger.info("开始提取翻译文本...")
        
        # 切换到主页选项卡以显示进度
        self.tabs.setCurrentIndex(0)
        
        # 创建并启动提取线程
        self.extractor_thread = ExtractorThread(self.config)
        self.extractor_thread.progress_update.connect(self.update_progress)
        self.extractor_thread.log_update.connect(self.log)
        self.extractor_thread.finished_signal.connect(self.extraction_finished)
        self.extractor_thread.start()
    
    def extraction_finished(self, success, message):
        # 重新启用开始按钮
        self.start_btn.set_loading_state(False)
        self.start_btn.setText("开始提取")  # 恢复原始文本
        
        # 显示结果
        if success:
            self.logger.info(f"✅ {message}")
            QMessageBox.information(self, "成功", message)
        else:
            self.logger.error(message)
            QMessageBox.warning(self, "失败", message)
            
    def closeEvent(self, event):
        """窗口关闭时的处理"""
        # 移除日志回调，防止内存泄漏
        self.logger.remove_ui_callback(self.log)
        event.accept()
