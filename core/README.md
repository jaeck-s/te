# 核心模块说明

## 事件系统使用指南

本应用程序使用事件驱动架构，通过`events.py`模块提供统一的事件发布-订阅机制。

### 主要事件

1. **应用程序事件**
   - `app:init` - 应用程序初始化
   - `app:exit` - 应用程序退出

2. **提取相关事件**
   - `extraction:started` - 开始提取
   - `extraction:progress` - 提取进度更新
   - `extraction:completed` - 提取完成
   - `extraction:error` - 提取错误

3. **配置相关事件**
   - `config:changed` - 配置变更

4. **文件操作事件**
   - `file:saved` - 文件保存
   - `file:loaded` - 文件加载

### 事件使用示例

```python
# 订阅事件
from core.events import subscribe, EventNames

def handle_extraction_completed(success, count, message):
    print(f"提取完成: 成功={success}, 条目数={count}, 消息={message}")

subscribe(EventNames.EXTRACTION_COMPLETED, handle_extraction_completed)

# 发布事件
from core.events import publish, EventNames

publish(EventNames.EXTRACTION_COMPLETED, success=True, count=10, message="提取成功")

# 取消订阅
from core.events import unsubscribe, EventNames

unsubscribe(EventNames.EXTRACTION_COMPLETED, handle_extraction_completed)
```

## 工厂模式

应用程序使用工厂模式分离组件创建和使用逻辑：

1. **ExtractorFactory** - 管理提取器
2. **ValidatorFactory** - 管理验证器
3. **WriterFactory** - 管理写入器

## 模块依赖关系

```
events.py <-- logger.py
   ^
   |
extractor.py --> factories/*.py
   |              |
   v              v
config.py <-- core modules
```

## 注意事项

- 事件处理器应确保异常被捕获，避免影响事件流
- 发布事件时应提供所有必要参数
- 取消订阅时应使用相同的处理函数引用
