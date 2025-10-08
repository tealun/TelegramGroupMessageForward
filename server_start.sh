#!/bin/bash
"""
服务器启动脚本
用于在宝塔等服务器环境中启动Telegram客户端
"""

# 检查验证码环境变量
check_verification_code() {
    if [ -z "$TELEGRAM_CODE" ]; then
        echo "❌ 未设置验证码环境变量"
        echo "💡 请先在Telegram中获取验证码，然后运行:"
        echo "   export TELEGRAM_CODE='您的验证码'"
        echo "   $0"
        echo ""
        echo "🔍 如果您需要获取验证码，请在另一个终端运行:"
        echo "   python3 request_code.py"
        exit 1
    fi
    
    echo "✅ 检测到验证码: $TELEGRAM_CODE"
}

# 检查Python环境
check_python_env() {
    echo "🐍 检查Python环境..."
    
    if ! command -v python3 &> /dev/null; then
        echo "❌ 未找到Python3"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python版本: $PYTHON_VERSION"
    
    # 检查依赖
    echo "📦 检查依赖包..."
    python3 -c "import telethon, telegram" 2>/dev/null || {
        echo "❌ 缺少依赖包，正在安装..."
        pip3 install telethon python-telegram-bot python-dotenv
    }
    
    echo "✅ 依赖包检查完成"
}

# 检查配置文件
check_config() {
    echo "📋 检查配置文件..."
    
    if [ ! -f ".env" ]; then
        echo "❌ 未找到.env配置文件"
        echo "💡 请先复制.env.example为.env并配置正确的参数"
        exit 1
    fi
    
    # 检查必要配置
    source .env
    
    if [ -z "$TELEGRAM_API_ID" ] || [ -z "$TELEGRAM_API_HASH" ] || [ -z "$TELEGRAM_PHONE" ]; then
        echo "❌ Telegram API配置不完整"
        echo "💡 请检查.env文件中的 TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE"
        exit 1
    fi
    
    if [ "$ENABLE_GROUP_FORWARD" = "true" ]; then
        if [ -z "$BOT_TOKEN" ] || [ -z "$MONITOR_GROUPS" ]; then
            echo "❌ 群组转发功能配置不完整"
            echo "💡 请检查.env文件中的 BOT_TOKEN, MONITOR_GROUPS"
            exit 1
        fi
        echo "✅ 群组转发功能已启用"
    fi
    
    echo "✅ 配置文件检查完成"
}

# 启动程序
start_client() {
    echo "🚀 启动Telegram客户端..."
    echo "📝 如果需要停止程序，请使用: kill -TERM \$(pgrep -f telegram_client.py)"
    echo ""
    
    # 设置日志输出
    export PYTHONUNBUFFERED=1
    
    # 启动程序
    nohup python3 telegram_client.py > telegram_client.log 2>&1 &
    CLIENT_PID=$!
    
    echo "✅ 程序已在后台启动，PID: $CLIENT_PID"
    echo "📋 日志文件: telegram_client.log"
    echo ""
    echo "🔍 查看实时日志: tail -f telegram_client.log"
    echo "🛑 停止程序: kill $CLIENT_PID"
    
    # 等待几秒检查程序状态
    sleep 3
    if kill -0 $CLIENT_PID 2>/dev/null; then
        echo "✅ 程序运行正常"
        echo ""
        echo "📊 程序状态检查:"
        echo "   ps aux | grep telegram_client.py"
        echo ""
        echo "📋 最新日志:"
        tail -n 10 telegram_client.log
    else
        echo "❌ 程序启动失败，请检查日志:"
        tail -n 20 telegram_client.log
        exit 1
    fi
}

# 显示帮助信息
show_help() {
    echo "Telegram客户端服务器启动脚本"
    echo ""
    echo "用法:"
    echo "  $0                 # 启动客户端（需要设置TELEGRAM_CODE环境变量）"
    echo "  $0 --help         # 显示帮助信息"
    echo "  $0 --check       # 只检查环境，不启动"
    echo "  $0 --request-code # 请求验证码"
    echo ""
    echo "环境变量:"
    echo "  TELEGRAM_CODE     # Telegram验证码"
    echo "  TELEGRAM_PASSWORD # 两步验证密码（如果启用了两步验证）"
    echo ""
    echo "示例:"
    echo "  # 1. 请求验证码"
    echo "  $0 --request-code"
    echo ""
    echo "  # 2. 设置验证码并启动"
    echo "  export TELEGRAM_CODE='12345'"
    echo "  $0"
}

# 请求验证码
request_verification_code() {
    echo "📱 请求验证码..."
    python3 -c "
import asyncio
from config import Config
from telethon import TelegramClient

async def request_code():
    client = TelegramClient(Config.SESSION_NAME, Config.API_ID, Config.API_HASH)
    await client.connect()
    if not await client.is_user_authorized():
        sent = await client.send_code_request(Config.PHONE_NUMBER)
        print('✅ 验证码已发送到您的手机: ' + Config.PHONE_NUMBER)
        print('💡 请查收短信验证码，然后运行:')
        print('   export TELEGRAM_CODE=\"您的验证码\"')
        print('   $0')
    else:
        print('✅ 已经登录，无需验证码')
    await client.disconnect()

asyncio.run(request_code())
"
}

# 主程序
main() {
    case "$1" in
        --help|-h)
            show_help
            ;;
        --check)
            echo "🔍 环境检查模式"
            check_python_env
            check_config
            echo "✅ 环境检查完成"
            ;;
        --request-code)
            check_python_env
            check_config
            request_verification_code
            ;;
        "")
            echo "🚀 宝塔Telegram客户端启动脚本"
            echo "==============================================="
            check_verification_code
            check_python_env
            check_config
            start_client
            ;;
        *)
            echo "❌ 未知参数: $1"
            show_help
            exit 1
            ;;
    esac
}

# 运行主程序
main "$@"
