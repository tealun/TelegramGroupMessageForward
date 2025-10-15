#  Telegram群组消息转发工具

![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)

**一个简单高效的Telegram群组消息监听和转发工具**

支持 **直接转发** 和 **下载重发** 两种模式，满足不同使用场景

##  功能特性

###  双转发模式
- **直接转发模式**：快速转发，保留完整来源信息（群组、发送者、时间）
- **下载重发模式**：纯净内容，无转发标记，适合内容聚合

###  智能特性
-  **消息去重** - 防止重复转发
-  **类型过滤** - 选择性转发不同消息类型
-  **机器人过滤** - 可选择忽略机器人消息
-  **文件大小控制** - 智能处理大文件
-  **自动重试** - 网络异常自动恢复
-  **详细日志** - 完整的操作记录

##  快速开始

###  系统要求
-  **Python 3.8+**
-  **Windows / Linux / macOS**
-  **稳定网络连接**

### 1 安装项目

`ash
# 克隆项目
git clone https://github.com/tealun/TelegramGroupMessageForward.git
cd TelegramGroupMessageForward

# 安装依赖
pip install -r requirements.txt
`

### 2 获取API凭据

####  获取Telegram API凭据
1. 访问 [https://my.telegram.org/apps](https://my.telegram.org/apps)
2. 使用手机号登录
3. 点击 **"Create application"**
4. 填写应用信息并获取 API ID 和 API Hash

####  创建转发机器人
1. 在Telegram中找到 [@BotFather](https://t.me/botfather)
2. 发送 /newbot 命令创建机器人
3. 获取机器人Token
4. 发送 /setprivacy  选择 Disable

####  获取群组ID
1. 将机器人添加到群组
2. 访问：https://api.telegram.org/bot<TOKEN>/getUpdates
3. 找到 "chat":{"id":-1001234567890}

### 3 配置设置

`ash
# 复制配置模板
copy .env.example .env    # Windows
cp .env.example .env      # Linux/macOS

# 编辑配置文件
notepad .env             # Windows
nano .env                # Linux/macOS
`

### 4 填写配置

`nv
# Telegram API配置
TELEGRAM_API_ID=123456
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+8613800138000

# 机器人配置  
BOT_TOKEN=123456789:ABCDEFghijklmnopQRSTUVwxyz123456789
MONITOR_GROUPS=-1001234567890,-1009876543210

# 转发模式选择
DOWNLOAD_AND_RESEND=false   # false=直接转发, true=下载重发
ENABLE_GROUP_FORWARD=true
`

### 5 启动服务

`ash
python telegram_client.py
`

##  转发模式对比

###  直接转发模式 (DOWNLOAD_AND_RESEND=false)

**效果示例：**
`
 [Python学习群] 张三: 2025-10-15 14:30:25
[转发来自 Python学习群] 今天学习了异步编程
`

**特点：**
-  速度极快，流量最少
-  保留完整来源信息
-  有转发标记

**适用场景：** 监控备份、需要追溯来源

###  下载重发模式 (DOWNLOAD_AND_RESEND=true)

**效果示例：**
`
今天学习了异步编程
`

**特点：**
-  纯净内容，无转发标记
-  速度较慢，消耗流量
-  丢失来源信息

**适用场景：** 内容聚合、避免转发痕迹

##  配置选项

### 基础配置
| 配置项 | 说明 | 示例 |
|--------|------|------|
| TELEGRAM_API_ID | Telegram API ID | 123456 |
| TELEGRAM_API_HASH | Telegram API Hash | bcdef123... |
| TELEGRAM_PHONE | 国际格式手机号 | +8613800138000 |
| BOT_TOKEN | 机器人Token | 123456:ABC-DEF... |
| MONITOR_GROUPS | 监听群组ID列表 | -1001234567890 |

### 转发控制
| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| DOWNLOAD_AND_RESEND | alse | 转发模式选择 |
| MAX_DOWNLOAD_SIZE | 20 | 文件大小限制(MB) |
| FORWARD_DELAY | 1 | 转发间隔(秒) |

##  常见问题

### API凭据问题
- **API ID/Hash获取失败**：确保正确登录 my.telegram.org
- **机器人Token错误**：格式应为 数字:字母数字串
- **手机号验证失败**：使用国际格式 +8613800138000

### 机器人配置问题  
- **收不到群组消息**：发送 /setprivacy 给 @BotFather，选择 Disable
- **群组ID获取不到**：确保机器人已加入群组，ID为负数格式
- **没有发送权限**：检查机器人在目标群组的权限

### 功能问题
- **消息重复转发**：检查 ENABLE_DEDUPLICATION=true 设置
- **文件下载失败**：调整 MAX_DOWNLOAD_SIZE 参数
- **无法连接**：检查网络，可能需要代理或VPN

##  项目结构

`
TelegramGroupMessageForward/
  telegram_client.py    # 主程序入口
  config.py            # 配置管理模块  
  .env                 # 环境配置文件
  .env.example         # 配置文件模板
  requirements.txt     # Python依赖包
  SIMPLE_GUIDE.md      # 简化使用指南
  README.md            # 项目说明文档
`

##  开源协议

本项目采用 [MIT License](LICENSE) 开源协议

##  参与贡献

欢迎提交 Issue 和 Pull Request！

-  报告问题
-  提出建议  
-  贡献代码
-  完善文档

##  联系方式

-  提交 [Issue](https://github.com/tealun/TelegramGroupMessageForward/issues)
-  参与 [Discussions](https://github.com/tealun/TelegramGroupMessageForward/discussions)
-  如果觉得有用，请给个 Star！

---

**感谢使用 Telegram群组消息转发工具！**
