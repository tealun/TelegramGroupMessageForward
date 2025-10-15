# Telegram群组消息转发工具

一个简单高效的Telegram群组消息监听和转发工具，支持两种转发模式：**直接转发**（保留来源信息）和**下载重发**（纯净内容）。

##  核心功能

###  双转发模式
- **直接转发模式**：快速转发，保留完整来源信息（群组、发送者、时间）
- **下载重发模式**：纯净内容，无转发标记，适合内容聚合

###  智能过滤
- **消息去重**：防止重复转发相同消息
- **类型过滤**：选择性转发不同类型的消息（文本、图片、视频、文档等）
- **机器人消息过滤**：可选择是否转发机器人消息
- **文件大小控制**：下载重发模式支持文件大小限制

###  稳定可靠
- **自动重试**：网络异常时自动重试
- **API限流处理**：智能延迟避免被限流
- **错误恢复**：连接中断时自动重连
- **详细日志**：完整的操作日志记录

##  快速开始

### 1. 环境准备

`ash
# 克隆项目
git clone https://github.com/tealun/TelegramGroupMessageForward.git
cd TeleClient

# 安装依赖
pip install -r requirements.txt
`

### 2. 配置设置

`ash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
`

**必填配置：**
`ash
# Telegram API配置
TELEGRAM_API_ID=你的API_ID
TELEGRAM_API_HASH=你的API_HASH
TELEGRAM_PHONE=你的手机号

# 机器人配置
BOT_TOKEN=你的机器人Token
MONITOR_GROUPS=群组ID1,群组ID2

# 启用转发功能
ENABLE_GROUP_FORWARD=true
`

### 3. 选择转发模式

`ash
# 转发模式选择（核心配置）
DOWNLOAD_AND_RESEND=false   # false=直接转发, true=下载重发
`

### 4. 启动服务

`ash
# 启动转发服务
python telegram_client.py
`

##  转发模式详解

###  直接转发模式 (DOWNLOAD_AND_RESEND=false)

**特点：**
-  速度最快，流量最省
-  保留完整来源信息（群组、发送者、时间）
-  有转发标记
-  消息较多（前缀+原消息）

**效果示例：**
`
 [Python学习群] 张三: 2025-10-15 14:30:25
[转发来自 Python学习群] 今天学习了异步编程
`

**适用场景：**
- 日常群组监控
- 需要知道消息来源
- 流量有限环境
- 追求最快速度

###  下载重发模式 (DOWNLOAD_AND_RESEND=true)

**特点：**
-  纯净内容，无转发标记
-  消息简洁，直接显示原文
-  丢失来源信息
-  速度较慢，消耗流量

**效果示例：**
`
今天学习了异步编程
`

**适用场景：**
- 内容聚合收集
- 需要干净显示
- 避免转发痕迹
- 内容收藏整理

##  配置选项

### 基础配置

| 配置项 | 说明 | 示例 |
|--------|------|------|
| TELEGRAM_API_ID | Telegram API ID | 123456 |
| TELEGRAM_API_HASH | Telegram API Hash | bcdef123456... |
| TELEGRAM_PHONE | 绑定的手机号 | +8613800138000 |
| BOT_TOKEN | 机器人Token | 123456:ABC-DEF... |
| MONITOR_GROUPS | 监听群组ID | -1001234567890 |

### 转发模式配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DOWNLOAD_AND_RESEND | alse | 转发模式选择 |
| MAX_DOWNLOAD_SIZE | 20 | 下载重发模式文件大小限制(MB) |

### 过滤配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| FORWARD_MEDIA | 	rue | 是否转发媒体文件 |
| FORWARD_STICKERS | 	rue | 是否转发贴纸 |
| FORWARD_VOICE | 	rue | 是否转发语音消息 |
| FORWARD_BOT_MESSAGES | 	rue | 是否转发机器人消息 |
| FORWARD_FORWARDED | alse | 是否转发已转发的消息 |

### 消息格式配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| MESSAGE_PREFIX |  [{chat_title}] {sender_name}: | 直接转发模式的前缀模板 |
| SHOW_MESSAGE_TIME | 	rue | 是否显示消息时间 |
| TIME_FORMAT | %Y-%m-%d %H:%M:%S | 时间格式 |

### 高级配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| ENABLE_DEDUPLICATION | 	rue | 启用消息去重 |
| DEDUP_WINDOW | 60 | 去重时间窗口(秒) |
| FORWARD_DELAY | 1 | 转发延迟(秒) |
| MAX_MESSAGE_LENGTH | 4000 | 最大消息长度 |

##  使用场景推荐

###  内容聚合场景
`ash
DOWNLOAD_AND_RESEND=true
FORWARD_MEDIA=true
`
**适用**：新闻聚合、技术文章收集、纯净内容展示

###  完整监控场景
`ash
DOWNLOAD_AND_RESEND=false
SHOW_MESSAGE_TIME=true
`
**适用**：团队沟通备份、群组活动监控、需要完整来源信息

###  快速转发场景
`ash
DOWNLOAD_AND_RESEND=false
FORWARD_DELAY=0
`
**适用**：实时消息转发、追求速度、流量敏感环境

###  精简模式场景
`ash
DOWNLOAD_AND_RESEND=true
MAX_DOWNLOAD_SIZE=5
FORWARD_MEDIA=false
`
**适用**：仅文本转发、存储空间有限、带宽受限

##  高级功能

### 自定义消息格式

`ash
# 支持的占位符
MESSAGE_PREFIX= 群组[{chat_title}] {sender_name} {message_time}:
`

可用占位符：
- {chat_title} - 群组名称
- {sender_name} - 发送者姓名  
- {message_time} - 消息时间
- {chat_id} - 群组ID
- {message_id} - 消息ID

### 智能文件处理

下载重发模式会自动处理不同大小的文件：
-  MAX_DOWNLOAD_SIZE: 下载重发（无转发标记）
- \> MAX_DOWNLOAD_SIZE: 显示"文件过大"提示

##  监控和日志

### 日志文件
`ash
# 查看运行日志
tail -f telegram_client.log

# 查看转发统计
grep "转发统计" telegram_client.log
`

### 实时统计
程序会定期输出转发统计：
- 消息接收数量
- 消息转发数量  
- 消息过滤数量
- 错误次数

##  测试工具

### 配置测试
`ash
# 运行配置测试
python test_forwarding.py
`

### 模式演示
`ash
# 查看转发模式效果对比
python demo_corrected_modes.py
`

##  注意事项

### 1. API限制
- 遵守Telegram API使用限制
- 合理设置转发延迟避免限流
- 大量消息转发时注意频率控制

### 2. 模式选择
- **直接转发**：适合需要完整信息的场景
- **下载重发**：适合内容聚合和纯净展示
- 可随时修改配置切换模式

### 3. 存储和流量
- 下载重发模式会消耗更多流量
- 大文件会暂时占用本地存储
- 合理设置文件大小限制

### 4. 隐私安全
- 确保配置文件安全性
- 不要在公共环境暴露Token
- 注意转发内容的隐私性

##  故障排除

### 常见问题

| 问题 | 可能原因 | 解决方案 |
|------|----------|----------|
| 无法连接 | 网络问题或代理配置 | 检查网络和代理设置 |
| 机器人无响应 | Token错误或权限不足 | 验证Token和机器人权限 |
| 群组无法访问 | 未加入群组或ID错误 | 运行测试脚本检查 |
| 文件下载失败 | 文件过大或网络超时 | 调整文件大小限制 |

### 诊断工具

`ash
# 运行完整诊断
python test_forwarding.py

# 查看转发模式演示
python demo_corrected_modes.py
`

##  项目结构

`
TeleClient/
 telegram_client.py      # 主程序
 config.py              # 配置管理
 .env                   # 环境配置
 .env.example           # 配置模板
 requirements.txt       # 依赖包
 test_forwarding.py     # 测试脚本
 demo_corrected_modes.py # 模式演示
 SIMPLE_GUIDE.md        # 简化使用指南
 README.md              # 本文件
`

##  未来计划

- [ ] Web管理界面
- [ ] 数据库存储消息历史
- [ ] 多用户支持
- [ ] AI内容过滤
- [ ] 消息统计分析
- [ ] 更多转发目标支持

##  许可证

本项目采用MIT许可证，详见 [LICENSE](LICENSE) 文件。

##  贡献

欢迎提交Issue和Pull Request来改进这个项目！

##  联系

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 加入讨论群组
