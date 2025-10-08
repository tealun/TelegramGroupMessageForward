# 服务器部署指南

本指南专门用于在宝塔面板等服务器环境中部署Telegram客户端。

## 🚀 快速启动

### 1. 首次部署

```bash
# 1. 上传文件到服务器
# 将所有项目文件上传到 /www/wwwroot/teleclient/

# 2. 进入项目目录
cd /www/wwwroot/teleclient

# 3. 安装依赖
pip3 install telethon python-telegram-bot python-dotenv

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入您的API配置

# 5. 请求验证码
python3 request_code.py

# 6. 设置验证码并启动
export TELEGRAM_CODE='您收到的验证码'
python3 telegram_client.py
```

### 2. 使用启动脚本（推荐）

```bash
# 给脚本执行权限
chmod +x server_start.sh

# 请求验证码
./server_start.sh --request-code

# 启动程序
export TELEGRAM_CODE='您的验证码'
./server_start.sh
```

## 📋 详细步骤

### 步骤1: 环境准备

1. **上传文件**
   - 将所有项目文件上传到服务器目录，如：`/www/wwwroot/teleclient/`

2. **安装Python依赖**
   ```bash
   cd /www/wwwroot/teleclient
   pip3 install -r requirements.txt
   ```

3. **配置文件**
   ```bash
   cp .env.example .env
   nano .env  # 或使用其他编辑器
   ```

   需要配置的参数：
   ```env
   TELEGRAM_API_ID=你的API_ID
   TELEGRAM_API_HASH=你的API_HASH
   TELEGRAM_PHONE=+8613812345678
   
   ENABLE_GROUP_FORWARD=true
   BOT_TOKEN=你的机器人Token
   MONITOR_GROUPS=-1003181064841,-1004796061339
   ```

### 步骤2: 验证码认证

#### 方法1: 使用验证码请求工具

```bash
# 请求验证码
python3 request_code.py
```

程序会发送验证码到您的手机，然后：

```bash
# 设置验证码环境变量
export TELEGRAM_CODE='12345'  # 替换为实际收到的验证码

# 启动程序
python3 telegram_client.py
```

#### 方法2: 一行命令启动

```bash
TELEGRAM_CODE='12345' python3 telegram_client.py
```

### 步骤3: 后台运行

#### 使用nohup

```bash
export TELEGRAM_CODE='12345'
nohup python3 telegram_client.py > telegram_client.log 2>&1 &
```

#### 使用screen

```bash
screen -S telegram_client
export TELEGRAM_CODE='12345'
python3 telegram_client.py
# 按 Ctrl+A, D 离开screen
```

#### 使用systemd服务

创建服务文件：
```bash
sudo nano /etc/systemd/system/telegram-client.service
```

内容：
```ini
[Unit]
Description=Telegram Client
After=network.target

[Service]
Type=simple
User=www
WorkingDirectory=/www/wwwroot/teleclient
Environment=TELEGRAM_CODE=12345
ExecStart=/usr/bin/python3 telegram_client.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable telegram-client
sudo systemctl start telegram-client
```

## 🔧 故障排除

### 1. 验证码相关问题

**问题**: `EOF when reading a line`
**原因**: 程序在非交互式环境中尝试读取验证码输入
**解决**: 使用环境变量提供验证码

```bash
export TELEGRAM_CODE='您的验证码'
python3 telegram_client.py
```

**问题**: `PhoneCodeInvalidError`
**原因**: 验证码错误或过期
**解决**: 重新请求验证码

```bash
python3 request_code.py
export TELEGRAM_CODE='新的验证码'
python3 telegram_client.py
```

### 2. 网络连接问题

**问题**: `Connection timeout`
**原因**: 服务器无法直接连接Telegram
**解决**: 
1. 检查服务器网络
2. 配置代理（如果需要）

```env
ENABLE_PROXY=true
SOCKS_PROXY_HOST=127.0.0.1
SOCKS_PROXY_PORT=1080
```

### 3. 两步验证问题

**问题**: `SessionPasswordNeededError`
**原因**: 账号启用了两步验证
**解决**: 设置密码环境变量

```bash
export TELEGRAM_PASSWORD='您的两步验证密码'
python3 telegram_client.py
```

### 4. 群组ID问题

**问题**: 接收到不相关的群组消息
**原因**: 群组ID配置错误
**解决**: 使用群组ID检测工具

```bash
python3 detect_group_ids.py
# 在目标群组发送测试消息，获取正确的群组ID
```

## 📊 监控和管理

### 查看日志

```bash
# 实时日志
tail -f telegram_client.log

# 最近日志
tail -n 50 telegram_client.log

# 搜索错误
grep -i error telegram_client.log
```

### 进程管理

```bash
# 查看进程
ps aux | grep telegram_client

# 停止程序
pkill -f telegram_client.py

# 重启程序
pkill -f telegram_client.py
sleep 2
export TELEGRAM_CODE='如果需要'
nohup python3 telegram_client.py > telegram_client.log 2>&1 &
```

### 系统资源监控

```bash
# CPU和内存使用
top -p $(pgrep -f telegram_client.py)

# 网络连接
netstat -tulpn | grep python3
```

## 📝 配置参考

### 完整的.env配置示例

```env
# Telegram API配置
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=abcdef1234567890abcdef1234567890
TELEGRAM_PHONE=+8613812345678

# 代理配置（可选）
ENABLE_PROXY=false
SOCKS_PROXY_HOST=127.0.0.1
SOCKS_PROXY_PORT=1080

# 群组转发功能
ENABLE_GROUP_FORWARD=true
BOT_TOKEN=123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ
MONITOR_GROUPS=-1003181064841,-1004796061339

# 转发过滤配置
FORWARD_MEDIA=true
FORWARD_STICKERS=true
FORWARD_VOICE=true
FORWARD_FORWARDED=false
FORWARD_BOT_MESSAGES=true

# 消息格式配置
MESSAGE_PREFIX=📢 [{chat_title}] {sender_name}:
SHOW_MESSAGE_TIME=true
TIME_FORMAT=%Y-%m-%d %H:%M:%S

# 高级配置
MAX_MESSAGE_LENGTH=4000
ENABLE_DEDUPLICATION=true
DEDUP_WINDOW=60
FORWARD_DELAY=1
```

## 🔄 自动化部署

如果需要完全自动化部署，可以创建部署脚本：

```bash
#!/bin/bash
# deploy.sh

# 1. 下载代码
git clone https://github.com/your-repo/teleclient.git
cd teleclient

# 2. 安装依赖
pip3 install -r requirements.txt

# 3. 配置环境
cp .env.example .env
echo "请编辑 .env 文件配置API参数"

# 4. 请求验证码
python3 request_code.py

# 5. 提示用户设置验证码
echo "请设置验证码: export TELEGRAM_CODE='您的验证码'"
echo "然后运行: python3 telegram_client.py"
```

这样您就可以在服务器环境中稳定运行Telegram客户端了！
