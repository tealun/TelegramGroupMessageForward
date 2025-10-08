# TelegramGroupMessageForward

一个简洁高效的Telegram群组消息监听和转发工具，支持将指定群组的消息自动转发到机器人私聊。

## ✨ 核心功能

- 🎯 **精确群组监听** - 只监听配置的群组，过滤其他消息
- 🤖 **机器人转发** - 将群组消息转发到您的机器人私聊窗口
- 🔄 **智能过滤** - 支持媒体、贴纸、语音等多种消息类型过滤
- 🚀 **服务器部署** - 支持服务器环境部署
- 📱 **非交互式启动** - 支持环境变量提供验证码，适合自动化部署

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

复制配置文件并编辑：
```bash
cp .env.example .env
# 编辑 .env 文件，配置您的API参数
```

需要配置的参数：
```env
# Telegram API配置
TELEGRAM_API_ID=你的API_ID
TELEGRAM_API_HASH=你的API_HASH
TELEGRAM_PHONE=你的手机号

# 群组转发功能
ENABLE_GROUP_FORWARD=true
BOT_TOKEN=你的机器人Token
MONITOR_GROUPS=群组ID1,群组ID2
```

### 3. 启动程序

**本地启动：**
```bash
python telegram_client.py
```

**服务器启动：**
```bash
# 请求验证码
python request_code.py

# 设置验证码并启动
export TELEGRAM_CODE='您的验证码'
python telegram_client.py
```

## 📋 项目结构

```
TeleClient/
├── telegram_client.py    # 主程序
├── config.py            # 配置加载
├── request_code.py      # 验证码请求工具
├── server_start.sh      # 服务器启动脚本
├── .env                 # 配置文件
├── requirements.txt     # 依赖列表
├── README.md           # 项目说明
└── SERVER_DEPLOYMENT.md # 部署指南
```

## ⚙️ 配置说明

### 群组ID获取

群组ID格式通常为正整数，如：`3181064841`

### 转发过滤选项

```env
FORWARD_MEDIA=true          # 转发媒体文件
FORWARD_STICKERS=true       # 转发贴纸
FORWARD_VOICE=true          # 转发语音
FORWARD_FORWARDED=false     # 转发转发的消息
FORWARD_BOT_MESSAGES=true   # 转发机器人消息
```

### 消息格式配置

```env
MESSAGE_PREFIX=📢 [{chat_title}] {sender_name}:
SHOW_MESSAGE_TIME=true
TIME_FORMAT=%Y-%m-%d %H:%M:%S
```

## 🔧 服务器部署

详细的服务器部署指南请参考：[SERVER_DEPLOYMENT.md](SERVER_DEPLOYMENT.md)

**快速部署命令：**
```bash
# 使用启动脚本
chmod +x server_start.sh
./server_start.sh --request-code  # 请求验证码
export TELEGRAM_CODE='验证码'
./server_start.sh                 # 启动程序
```

## 📝 日志和监控

```bash
# 查看实时日志
tail -f telegram_client.log

# 检查程序状态
ps aux | grep telegram_client
```

## ❓ 常见问题

**1. "Cannot find entity" 错误**
- 检查群组ID格式，使用正整数格式
- 确认您的账号已加入目标群组

**2. "EOF when reading a line" 错误**
- 在服务器环境中使用环境变量提供验证码：
  ```bash
  export TELEGRAM_CODE='您的验证码'
  ```

**3. 转发不工作**
- 检查机器人Token是否正确
- 确认群组ID配置正确
- 验证您已与机器人开始对话

## 📄 许可证

MIT License
