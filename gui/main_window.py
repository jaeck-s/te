import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QMessageBox,
                            QGroupBox, QFormLayout, QLineEdit, QTabWidget,
                            QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QSettings, pyqtSlot, QMetaObject, Q_ARG
from PyQt5.QtGui import QIcon
from core.extractor import TranslationExtractor
from core.config import TranslationConfig
from core.logger import get_logger
from core.events import subscribe, unsubscribe, publish, EventNames
from gui.components.buttons import ActionButton
from gui.tabs.settings_tab import SettingsTab
from gui.tabs.home_tab import HomeTab

class ExtractorThread(QThread):
    """执行翻译提取的后台线程"""
    progress_update = pyqtSignal(int, int)  # 发出信号：当前进度, 总数
    log_update = pyqtSignal(str)  # 发出日志信息
    finished_signal = pyqtSignal(bool, str)  # 发出完成信号：成功/失败, 消息

    def __init__(self, config):
        super().__init__()
        self.config = config
        # 重要：在线程中创建提取器对象而不是传递已有对象
        self.extractor = None
        
    def run(self):
        try:
            # 在线程内部创建对象，避免线程所有权问题
            self.extractor = TranslationExtractor(self.config)
            
            # 使用信号机制传递进度和日志
            def safe_emit_progress(current, total):
                try:
                    # 使用emit而不是直接调用回调函数
                    self.progress_update.emit(current, total)
                except Exception as e:
                    print(f"发送进度信号错误: {str(e)}")
                    
            def safe_emit_log(message):
                try:
                    # 使用emit而不是直接调用回调函数
                    self.log_update.emit(message)
                except Exception as e:
                    print(f"发送日志信号错误: {str(e)}")
            
            # 连接信号
            self.extractor.progress_callback = safe_emit_progress
            self.extractor.log_callback = safe_emit_log
            
            # 发布开始提取事件
            publish(EventNames.EXTRACTION_STARTED, config=self.config)
            
            # 执行提取
            result = self.extractor.extract()
            
            if result:
                message = f"提取完成，成功生成 {result} 个翻译条目。"
                self.finished_signal.emit(True, message)
                # 发布提取完成事件
                publish(EventNames.EXTRACTION_COMPLETED, success=True, count=result, message=message)
            else:
                message = "提取过程没有生成任何新的翻译条目。"
                self.finished_signal.emit(False, message)
                # 发布提取完成事件
                publish(EventNames.EXTRACTION_COMPLETED, success=False, count=0, message=message)
                
        except Exception as e:
            error_msg = f"提取失败: {str(e)}"
            self.log_update.emit(f"错误: {str(e)}")
            self.finished_signal.emit(False, error_msg)
            
            # 发布提取错误事件
            publish(EventNames.EXTRACTION_ERROR, error=str(e), message=error_msg)


class MainWindow(QMainWindow):
    def __init__(self, config=None):
        super().__init__()
        self.setWindowTitle("Renpy游戏翻译提取器")
        self.setMinimumSize(800, 600)
        self.config = config if config else TranslationConfig()
        
        # 设置日志记录器
        self.logger = get_logger()
        self.logger.add_ui_callback(self.log)
        
        # 初始化历史目录列表
        self.history_dirs = []
        self.load_history_dirs()
        
        # 订阅事件
        self._setup_event_handlers()
        
        self.setup_ui()
        
        # 应用配置到UI
        if config:
            self.apply_config_to_ui()
    
    def load_history_dirs(self):
        """加载历史目录记录"""
        settings = QSettings("FY-Team", "RenpyTranslationExtractor")
        self.history_dirs = settings.value("history_dirs", [])
        if not isinstance(self.history_dirs, list):
            self.history_dirs = []
    
    def save_history_dirs(self):
        """保存历史目录记录"""
        settings = QSettings("FY-Team", "RenpyTranslationExtractor")
        settings.setValue("history_dirs", self.history_dirs)
    
    def add_to_history_dirs(self, dir_path):
        """添加目录到历史记录"""
        if dir_path in self.history_dirs:
            # 如果已存在，移到最前面
            self.history_dirs.remove(dir_path)
        # 添加到列表前面
        self.history_dirs.insert(0, dir_path)
        # 保持列表最多5个
        self.history_dirs = self.history_dirs[:5]
        # 保存设置
        self.save_history_dirs()
        # 更新主页选项卡的历史菜单
        self.home_tab.update_history_menu(self.history_dirs)
    
    def _setup_event_handlers(self):
        """设置事件处理器"""
        # 订阅提取进度更新事件
        subscribe(EventNames.EXTRACTION_PROGRESS, self.handle_extraction_progress)
        
        # 订阅提取完成事件
        subscribe(EventNames.EXTRACTION_COMPLETED, self.handle_extraction_completed)
        
        # 订阅提取错误事件
        subscribe(EventNames.EXTRACTION_ERROR, self.handle_extraction_error)
        
        # 订阅配置变更事件
        subscribe(EventNames.CONFIG_CHANGED, self.handle_config_changed)
    
    def handle_extraction_progress(self, current, total):
        """处理提取进度更新事件"""
        if QThread.currentThread() != QApplication.instance().thread():
            # 通过Qt信号机制将进度更新请求转发到主线程
            QMetaObject.invokeMethod(self, "update_progress_in_main_thread",
                                    Qt.QueuedConnection,
                                    Q_ARG(int, current),
                                    Q_ARG(int, total))
            return
            
        if total > 0:
            progress_value = int(current / total * 100)
            if hasattr(self, 'home_tab') and self.home_tab:
                try:
                    # 使用简单直接的方式更新UI
                    self.home_tab.update_progress(progress_value)
                except Exception as e:
                    print(f"更新进度条时出错: {str(e)}")
    
    @pyqtSlot(int, int)
    def update_progress_in_main_thread(self, current, total):
        """主线程中的进度更新函数(槽)"""
        if total > 0:
            progress_value = int(current / total * 100)
            if hasattr(self, 'home_tab') and self.home_tab:
                try:
                    self.home_tab.update_progress(progress_value)
                except Exception as e:
                    print(f"更新进度条时出错: {str(e)}")
    
    def handle_extraction_completed(self, success, count, message):
        """处理提取完成事件"""
        pass
    
    def handle_extraction_error(self, error, message):
        """处理提取错误事件"""
        self.logger.error(f"提取错误: {error}")
    
    def handle_config_changed(self, config):
        """处理配置变更事件"""
        # 如果需要，可以根据配置更新界面
        pass
    
    def setup_ui(self):
        """设置UI组件"""
        # 主布局
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)
        
        # 创建选项卡
        self.tabs = QTabWidget()
        self.home_tab = HomeTab()
        self.settings_tab = SettingsTab()
        
        self.tabs.addTab(self.home_tab, "主页")
        self.tabs.addTab(self.settings_tab, "设置")
        
        main_layout.addWidget(self.tabs)
        
        # 初始化主页选项卡
        self.init_home_tab()
        
        # 显示默认日志
        self.home_tab.display_default_log()
    
    def init_home_tab(self):
        """初始化主页选项卡的事件连接"""
        # 连接开始提取按钮
        self.home_tab.start_btn.clicked.connect(self.start_extraction)
        
        # 更新历史目录菜单
        self.home_tab.update_history_menu(self.history_dirs)
    
    def log(self, message):
        """添加日志到日志文本框"""
        try:
            # 在子线程中，必须使用信号机制将消息传递到主线程
            if QThread.currentThread() != QApplication.instance().thread():
                # 通过Qt信号机制将日志请求转发到主线程
                QMetaObject.invokeMethod(self, "log_in_main_thread",
                                        Qt.QueuedConnection,
                                        Q_ARG(str, message))
                return
                
            if hasattr(self, 'home_tab') and self.home_tab:
                # 使用简单直接的方式更新日志
                self.home_tab.append_log(message)
        except Exception as e:
            print(f"日志更新错误: {str(e)}")
    
    @pyqtSlot(str)
    def log_in_main_thread(self, message):
        """主线程中的日志处理函数(槽)"""
        if hasattr(self, 'home_tab') and self.home_tab:
            self.home_tab.append_log(message)
    
    def update_progress(self, current, total):
        """更新进度条"""
        if total > 0:
            progress_value = int(current / total * 100)
            if hasattr(self, 'home_tab') and self.home_tab:
                self.home_tab.update_progress(progress_value)
    
    def update_config(self):
        """将当前UI设置更新到配置对象"""
        # 从主页选项卡获取基本设置
        self.config.game_dir = self.home_tab.get_game_dir()
        self.config.translation_dir = self.home_tab.get_translation_dir()
        self.config.write_mode = self.home_tab.get_write_mode()  # 获取写入模式
        
        # 从设置选项卡获取高级设置
        self.settings_tab.update_config(self.config)
        return self.config
    
    def apply_config_to_ui(self):
        """将配置对象应用到UI"""
        # 更新主页选项卡
        self.home_tab.set_game_dir(self.config.game_dir)
        self.home_tab.set_translation_dir(self.config.translation_dir)
        self.home_tab.set_write_mode(self.config.write_mode)  # 设置写入模式
        
        # 更新设置选项卡中的文件格式
        if self.config.file_patterns:
            # 获取设置选项卡中的文件格式组
            if hasattr(self.settings_tab, 'file_format_options'):
                for fmt in ["rpy", "json"]:
                    pattern = f"*.{fmt}"
                    if pattern in self.config.file_patterns:
                        self.settings_tab.file_format_options.set_option_checked(fmt, True)
                    else:
                        self.settings_tab.file_format_options.set_option_checked(fmt, False)
                
                # 触发文件格式更新事件
                self.settings_tab.update_extraction_modes_availability()
        
        # 更新提取选项
        if hasattr(self.settings_tab, 'recursive_option'):
            self.settings_tab.recursive_option.set_checked(self.config.recursive)
        
        if hasattr(self.settings_tab, 'skip_translated_option'):
            self.settings_tab.skip_translated_option.set_checked(self.config.skip_translated)
        
        if hasattr(self.settings_tab, 'person_name_writer_option'):
            use_person_name = getattr(self.config, 'use_person_name_writer', False)
            self.settings_tab.person_name_writer_option.set_checked(use_person_name)
        
        # 更新提取器选择
        if self.config.extractors:
            for group_name, extractors_dict in self.settings_tab.extractor_groups.items():
                for name, checkbox in extractors_dict.items():
                    checkbox.setChecked(name in self.config.extractors)
        
        # 更新验证器选择
        if hasattr(self.settings_tab, 'validator_group') and self.settings_tab.validator_group:
            for validator_name in self.settings_tab.validator_group.options.keys():
                self.settings_tab.validator_group.set_option_checked(
                    validator_name, 
                    validator_name in self.config.validators
                )
        
        # 更新编码选择
        if hasattr(self.settings_tab, 'encoding_combo'):
            index = self.settings_tab.encoding_combo.findText(self.config.encoding)
            if index >= 0:
                self.settings_tab.encoding_combo.setCurrentIndex(index)
    
    def start_extraction(self):
        """开始提取翻译文本"""
        game_dir = self.home_tab.get_game_dir()
        if not game_dir:
            self.logger.warning("请先选择游戏目录")
            QMessageBox.warning(self, "警告", "请先选择游戏目录")
            return
        
        # 获取选中的提取器
        selected_extractors = self.settings_tab.get_selected_extractors()
        if not selected_extractors:
            self.logger.warning("请选择至少一个提取器")
            QMessageBox.warning(self, "警告", "请选择至少一个提取器")
            return
        
        # 更新配置
        self.update_config()
        
        # 如果是覆盖模式，弹出确认对话框
        if self.config.write_mode == "overwrite":
            reply = QMessageBox.question(
                self,
                "覆盖模式确认",
                "您选择了覆盖模式，这将清空翻译目录中的所有.rpy文件并重新创建。\n任何现有的翻译都将被删除且无法恢复。\n\n确定要继续吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # 发布配置变更事件
        publish(EventNames.CONFIG_CHANGED, config=self.config)
        
        # 禁用开始按钮
        self.home_tab.start_btn.set_loading_state(True)
        self.home_tab.update_progress(0)
        self.logger.info("开始提取翻译文本...")
        
        # 切换到主页选项卡以显示进度
        self.tabs.setCurrentIndex(0)
        
        # 创建并启动提取线程
        self.extractor_thread = ExtractorThread(self.config)
        self.extractor_thread.progress_update.connect(self.handle_extraction_progress)
        self.extractor_thread.log_update.connect(self.log)
        self.extractor_thread.finished_signal.connect(self.extraction_finished)
        self.extractor_thread.start()
    
    def extraction_finished(self, success, message):
        """处理提取完成事件"""
        # 重新启用开始按钮
        self.home_tab.start_btn.set_loading_state(False)
        self.home_tab.start_btn.setText("开始提取")  # 恢复原始文本
        self.home_tab.update_progress(0)
        
        # 显示结果
        if success:
            self.logger.info(f"✅ {message}")
            QMessageBox.information(self, "成功", message)
        else:
            self.logger.error(message)
            QMessageBox.warning(self, "失败", message)
    
    def on_game_dir_selected(self, dir_path):
        """处理游戏目录选择事件"""
        # 添加到历史记录
        self.add_to_history_dirs(dir_path)
        
        # 检查游戏目录是否有效
        if not os.path.exists(os.path.join(dir_path, "game")):
            self.logger.warning(f"所选目录似乎不是一个标准的Renpy游戏目录，未找到game文件夹")
    
    def on_invalid_dir_selected(self, dir_path):
        """处理无效目录选择事件"""
        # 从历史记录中移除不存在的目录
        if dir_path in self.history_dirs:
            self.history_dirs.remove(dir_path)
            self.save_history_dirs()
            self.home_tab.update_history_menu(self.history_dirs)
    
    def on_clear_history_requested(self):
        """处理清除历史记录请求事件"""
        self.history_dirs = []
        self.save_history_dirs()
        self.home_tab.update_history_menu(self.history_dirs)
        self.logger.info("已清除历史目录记录")
    
    def closeEvent(self, event):
        """窗口关闭时的处理"""
        try:
            # 自动保存配置
            self.update_config()
            self.config.save_default_config()
            self.logger.debug("配置已自动保存")
        except Exception as e:
            self.logger.error(f"自动保存配置失败: {str(e)}")
        
        # 保存历史目录
        self.save_history_dirs()
        
        # 移除日志回调，防止内存泄漏
        self.logger.remove_ui_callback(self.log)
        
        # 取消订阅所有事件
        unsubscribe(EventNames.EXTRACTION_PROGRESS, self.handle_extraction_progress)
        unsubscribe(EventNames.EXTRACTION_COMPLETED, self.handle_extraction_completed)
        unsubscribe(EventNames.EXTRACTION_ERROR, self.handle_extraction_error)
        unsubscribe(EventNames.CONFIG_CHANGED, self.handle_config_changed)
        
        event.accept()
