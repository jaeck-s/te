# Renpy游戏翻译提取器

一个用于提取Renpy游戏中可翻译文本并生成翻译模板的图形化工具。

## 功能特点

- 图形用户界面，操作简便直观
- 专注提取RPY文件中的三种关键属性值：
  - `description`
  - `purchase_notification`
  - `unlock_notification`
- 自动生成标准格式的翻译文件
- 可跳过已翻译条目，支持增量提取
- 模块化设计，易于未来扩展

## 使用方法

1. 安装依赖：`pip install -r requirements.txt`
2. 运行程序：`python main.py`
3. 在界面中选择游戏目录
4. 配置提取选项
5. 选择要使用的提取器（可多选）
6. 点击"开始提取"按钮

## 提取器说明

当前版本仅支持以下三种提取器：

- `description`: 提取RPY文件中的description属性值
- `purchase_notification`: 提取RPY文件中的purchase_notification属性值
- `unlock_notification`: 提取RPY文件中的unlock_notification属性值

## 项目结构

```
.
├── main.py                     # 主程序入口
├── gui/                        # GUI相关模块
│   ├── components/             # 界面组件
│   │   ├── buttons.py          # 按钮组件
│   │   └── __init__.py
│   ├── main_window.py          # 主窗口类
│   └── __init__.py
├── core/                       # 核心功能模块
│   ├── factories/              # 工厂类模块
│   │   ├── extractor_factory.py # 提取器工厂
│   │   ├── validator_factory.py # 验证器工厂
│   │   ├── writer_factory.py    # 写入器工厂
│   │   └── __init__.py
│   ├── extractors_impl/        # 提取器实现
│   │   ├── rpy_properties.py   # RPY属性提取器
│   │   └── __init__.py
│   ├── regex/                  # 正则表达式模块
│   │   ├── rpy_patterns.py     # RPY文件模式
│   │   └── __init__.py
│   ├── config.py               # 配置类
│   ├── extractor.py            # 提取器核心类
│   ├── logger.py               # 日志管理模块
│   └── __init__.py
└── requirements.txt            # 依赖项
```

## 许可证

MIT
