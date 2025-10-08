#!/usr/bin/env python3
"""
验证码请求工具
专门用于在服务器环境中请求Telegram验证码
"""

import asyncio
import sys
from telethon import TelegramClient
from config import Config

async def request_verification_code():
    """请求验证码"""
    try:
        print("📱 正在请求Telegram验证码...")
        print(f"📞 目标手机号: {Config.PHONE_NUMBER}")
        
        # 创建客户端
        proxy = None
        if hasattr(Config, 'ENABLE_PROXY') and Config.ENABLE_PROXY:
            proxy = (Config.SOCKS_PROXY_HOST, Config.SOCKS_PROXY_PORT)
        
        client = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH,
            proxy=proxy
        )
        
        await client.connect()
        
        # 检查是否已经登录
        if await client.is_user_authorized():
            print("✅ 您已经登录，无需验证码")
            me = await client.get_me()
            print(f"👤 当前用户: {me.first_name} {me.last_name or ''} (@{me.username or 'None'})")
            print("🚀 可以直接运行主程序: python3 telegram_client.py")
            return
        
        # 发送验证码
        sent = await client.send_code_request(Config.PHONE_NUMBER)
        
        print("\n✅ 验证码已发送成功!")
        print(f"📱 请查收手机 {Config.PHONE_NUMBER} 的短信")
        print(f"📧 验证码类型: {sent.type}")
        
        print("\n💡 获取验证码后，请运行以下命令:")
        print("   export TELEGRAM_CODE='您收到的验证码'")
        print("   python3 telegram_client.py")
        
        print("\n🔄 或者使用一行命令:")
        print("   TELEGRAM_CODE='您的验证码' python3 telegram_client.py")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ 请求验证码失败: {e}")
        print("\n🔍 可能的原因:")
        print("1. 网络连接问题")
        print("2. API配置错误")
        print("3. 手机号格式错误")
        print("4. Telegram服务器问题")
        
        print("\n💡 解决方案:")
        print("1. 检查网络连接")
        print("2. 确认.env文件中的API_ID、API_HASH、PHONE配置正确")
        print("3. 手机号格式应为: +8613812345678")
        
        sys.exit(1)

def main():
    """主函数"""
    print("🔑 Telegram验证码请求工具")
    print("=" * 40)
    
    try:
        # 验证配置
        if not Config.API_ID or not Config.API_HASH or not Config.PHONE_NUMBER:
            print("❌ 配置不完整")
            print("💡 请检查.env文件中的以下配置:")
            print("   TELEGRAM_API_ID")
            print("   TELEGRAM_API_HASH") 
            print("   TELEGRAM_PHONE")
            sys.exit(1)
        
        print(f"📋 配置信息:")
        print(f"   API_ID: {Config.API_ID}")
        print(f"   PHONE: {Config.PHONE_NUMBER}")
        print()
        
        # 运行请求
        asyncio.run(request_verification_code())
        
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
