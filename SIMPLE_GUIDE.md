# 简化转发模式使用说明

## 🎯 核心概念

现在只有**一个开关**控制转发模式：`DOWNLOAD_AND_RESEND`

### 🔄 两种转发模式

| 模式 | 配置 | 特点 | 适用场景 |
|------|------|------|----------|
| **直接转发** | `DOWNLOAD_AND_RESEND=false` | ⚡ 快速、💾 节省流量、📱 原生格式 | 大部分日常使用 |
| **下载重发** | `DOWNLOAD_AND_RESEND=true` | 🎨 自定义格式、🔧 完全控制、📊 消耗流量 | 需要自定义格式时 |

## 📋 简化配置

### 基础配置 (.env文件)
```bash
# 转发模式（一个开关搞定）
DOWNLOAD_AND_RESEND=false       # false=直接转发, true=下载重发

# 下载重发模式的文件大小限制
MAX_DOWNLOAD_SIZE=20            # 超过20MB自动改为直接转发

# 要转发哪些类型的消息
FORWARD_MEDIA=true              # 图片/视频/文档等
FORWARD_STICKERS=true           # 贴纸
FORWARD_VOICE=true              # 语音消息
FORWARD_BOT_MESSAGES=true       # 机器人消息
```

## 🔧 推荐配置

### 新手推荐（默认）
```bash
DOWNLOAD_AND_RESEND=false
MAX_DOWNLOAD_SIZE=20
```
**特点**：最快速度，最节省流量，够用就行

### 进阶用户
```bash
DOWNLOAD_AND_RESEND=true
MAX_DOWNLOAD_SIZE=10
```
**特点**：自定义消息格式，小文件下载重发，大文件直接转发

## 🤖 智能转发逻辑

程序会自动处理：

1. **直接转发模式** (`DOWNLOAD_AND_RESEND=false`)：
   - 发送自定义前缀 → 直接转发原消息
   - 速度最快，流量最省

2. **下载重发模式** (`DOWNLOAD_AND_RESEND=true`)：
   - 检查文件大小
   - 如果 ≤ `MAX_DOWNLOAD_SIZE`：下载重发（自定义格式）
   - 如果 > `MAX_DOWNLOAD_SIZE`：自动改为直接转发

## 💡 使用建议

### 🎯 场景选择
- **日常聊天转发**：`DOWNLOAD_AND_RESEND=false`
- **重要消息备份**：`DOWNLOAD_AND_RESEND=true`
- **流量有限环境**：`DOWNLOAD_AND_RESEND=false`
- **需要自定义格式**：`DOWNLOAD_AND_RESEND=true`

### 📊 文件大小设置
- **移动网络**：`MAX_DOWNLOAD_SIZE=5`
- **WiFi环境**：`MAX_DOWNLOAD_SIZE=20`
- **服务器部署**：`MAX_DOWNLOAD_SIZE=50`

## 🛠️ 快速设置

1. **编辑 .env 文件**
2. **修改一个开关**：`DOWNLOAD_AND_RESEND=true/false`
3. **调整文件大小限制**：`MAX_DOWNLOAD_SIZE=20`
4. **运行程序**

就这么简单！🎉

## ❓ 常见问题

**Q: 想要自定义消息格式怎么办？**
A: 设置 `DOWNLOAD_AND_RESEND=true`

**Q: 想节省流量怎么办？**
A: 设置 `DOWNLOAD_AND_RESEND=false`

**Q: 大文件下载失败怎么办？**
A: 程序会自动改为直接转发，无需担心

**Q: 想要既自定义又节省流量？**
A: 设置 `DOWNLOAD_AND_RESEND=true` 和较小的 `MAX_DOWNLOAD_SIZE`

简单明了，一个开关解决所有问题！🚀
