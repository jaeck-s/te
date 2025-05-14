"""
主页选项卡模块
用于显示主要的应用程序功能，包括游戏目录选择和提取进度显示
"""
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QProgressBar, QGroupBox,
                            QPushButton, QFileDialog, QMenu, QAction,
                            QTextEdit, QRadioButton, QApplication)
import os
from gui.components.buttons import ActionButton, BrowseButton
from gui.tabs.base_tab import BaseTab


class HomeTab(BaseTab):
    """主页选项卡，显示主要功能界面"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 初始化UI组件引用
        self.game_dir_edit = None
        self.history_btn = None
        self.history_menu = None
        self.tl_dir_edit = None
        self.start_btn = None
        self.progress_bar = None
        self.log_text = None
        self.write_mode_append = None
        self.write_mode_overwrite = None
        
        # 历史目录列表
        self.history_dirs = []
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI组件"""
        # 配置区域
        config_group = self.create_group("配置")
        config_layout = config_group.layout()
        
        # 游戏目录选择
        game_dir_section, game_dir_container, game_dir_layout = self.create_section_with_label("游戏目录:")
        
        self.game_dir_edit = QLineEdit()
        self.game_dir_edit.setReadOnly(True)
        
        # 创建历史目录下拉按钮
        self.history_btn = QPushButton()
        self.history_btn.setToolTip("选择历史目录")
        self.history_btn.setFixedSize(24, 24)
        self.history_btn.setStyleSheet("""
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
                border-radius: 3px;
            }
            QPushButton::menu-indicator {
                width: 0px;
            }
        """)
        self.history_btn.setText("▾")
        
        # 创建历史目录菜单
        self.history_menu = QMenu()
        self.history_btn.setMenu(self.history_menu)
        
        browse_btn = BrowseButton()
        browse_btn.clicked.connect(self.select_game_dir)
        
        # 添加组件到布局
        game_dir_layout.addWidget(self.game_dir_edit)
        game_dir_layout.addWidget(self.history_btn)
        game_dir_layout.addWidget(browse_btn)
        
        # 将游戏目录部分添加到主配置布局
        config_layout.addLayout(game_dir_section)
        
        # 翻译目录选择
        tl_dir_section, tl_container, tl_layout = self.create_section_with_label("翻译目录:")
        
        self.tl_dir_edit = QLineEdit("game/tl/schinese")
        self.tl_dir_edit.setToolTip("相对于游戏目录的翻译文件夹路径")
        tl_layout.addWidget(self.tl_dir_edit)
        
        # 将翻译目录部分添加到主配置布局
        config_layout.addLayout(tl_dir_section)
        
        # 写入模式选择
        write_mode_section, write_mode_container, write_mode_layout = self.create_section_with_label("写入模式:")
        
        # 创建单选框组
        self.write_mode_append = QRadioButton("追加模式")
        self.write_mode_append.setToolTip("只添加新条目，不修改现有翻译")
        self.write_mode_append.setChecked(True)  # 默认选中追加模式
        
        self.write_mode_overwrite = QRadioButton("覆盖模式")
        self.write_mode_overwrite.setToolTip("清空现有翻译文件夹并重新创建所有翻译文件，注意：此操作会删除所有现有翻译！")
        
        # 添加到布局
        write_mode_layout.addWidget(self.write_mode_append)
        write_mode_layout.addWidget(self.write_mode_overwrite)
        write_mode_layout.addStretch()  # 添加弹性空间，防止单选框占满整行
        
        # 将写入模式选择添加到配置布局
        config_layout.addLayout(write_mode_section)
        
        # 添加配置组到内容布局
        self.add_widget(config_group)
        
        # 操作区域
        actions_layout = QHBoxLayout()
        self.start_btn = ActionButton("开始提取")
        # 连接信号在MainWindow中设置
        actions_layout.addWidget(self.start_btn)
        self.add_layout(actions_layout)
        
        # 进度条
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        self.add_layout(progress_layout)
        
        # 日志输出区域
        log_group = self.create_group("日志输出")
        log_layout = log_group.layout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        self.add_widget(log_group)
        
        # 添加伸缩因子，使组件靠上对齐
        self.add_stretch()

    def update_history_menu(self, history_dirs):
        """更新历史目录菜单"""
        self.history_menu.clear()
        self.history_dirs = history_dirs
        
        if not history_dirs:
            no_history = QAction("暂无历史记录", self)
            no_history.setEnabled(False)
            self.history_menu.addAction(no_history)
            return
            
        for dir_path in history_dirs:
            action = QAction(dir_path, self)
            action.triggered.connect(lambda checked=False, path=dir_path: self.on_history_dir_selected(path))
            self.history_menu.addAction(action)
            
        # 添加清除历史记录选项
        self.history_menu.addSeparator()
        clear_action = QAction("清除历史记录", self)
        clear_action.triggered.connect(self.on_clear_history)
        self.history_menu.addAction(clear_action)
    
    def select_game_dir(self):
        """选择游戏目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择游戏目录")
        if dir_path:
            self.game_dir_edit.setText(dir_path)
            # 请求主窗口处理游戏目录选择
            if hasattr(self.parent(), "on_game_dir_selected"):
                self.parent().on_game_dir_selected(dir_path)
    
    def on_history_dir_selected(self, dir_path):
        """处理从历史记录中选择目录"""
        if os.path.exists(dir_path):
            self.game_dir_edit.setText(dir_path)
            # 请求主窗口处理游戏目录选择
            if hasattr(self.parent(), "on_game_dir_selected"):
                self.parent().on_game_dir_selected(dir_path)
        else:
            self.logger.warning(f"所选目录不存在: {dir_path}")
            # 请求主窗口处理不存在的目录
            if hasattr(self.parent(), "on_invalid_dir_selected"):
                self.parent().on_invalid_dir_selected(dir_path)
    
    def on_clear_history(self):
        """请求清除历史记录"""
        if hasattr(self.parent(), "on_clear_history_requested"):
            self.parent().on_clear_history_requested()
    
    def append_log(self, message):
        """添加日志到日志文本框"""
        try:
            # 我们不再需要线程检查，因为MainWindow已经确保了这点
            # 只需简单直接地添加文本
            self.log_text.append(message)
            
            # 滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"日志更新错误: {str(e)}")
    
    def update_progress(self, value):
        """更新进度条值"""
        self.progress_bar.setValue(value)
    
    def get_game_dir(self):
        """获取游戏目录"""
        return self.game_dir_edit.text()
    
    def get_translation_dir(self):
        """获取翻译目录"""
        return self.tl_dir_edit.text()
    
    def set_game_dir(self, dir_path):
        """设置游戏目录"""
        self.game_dir_edit.setText(dir_path)
    
    def set_translation_dir(self, dir_path):
        """设置翻译目录"""
        self.tl_dir_edit.setText(dir_path)
    
    def get_write_mode(self):
        """获取当前选择的写入模式"""
        return "overwrite" if self.write_mode_overwrite.isChecked() else "append"

    def set_write_mode(self, mode):
        """设置写入模式"""
        if mode == "overwrite":
            self.write_mode_overwrite.setChecked(True)
        else:
            self.write_mode_append.setChecked(True)
    
    def display_default_log(self):
        """显示默认日志信息"""
        self.logger.info("欢迎使用Renpy游戏翻译提取器")
        self.logger.info("请选择游戏目录并配置选项后，点击'开始提取'按钮")
        self.logger.info("当前支持提取以下属性值和函数：description、purchase_notification、unlock_notification、title_text、description_text、renpy.notify")
