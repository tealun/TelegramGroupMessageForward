"""
配置文件加载模块
"""
import os
from dotenv import load_dotenv
import logging

# 加载环境变量
load_dotenv()

# 设置日志
logger = logging.getLogger(__name__)

class Config:
    """Telegram API配置"""
    
    # Telegram API配置
    API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
    API_HASH = os.getenv('TELEGRAM_API_HASH', '')
    PHONE_NUMBER = os.getenv('TELEGRAM_PHONE', '')
    
    # 会话文件名
    SESSION_NAME = 'telegram_session'
    
    # 代理配置
    ENABLE_PROXY = os.getenv('ENABLE_PROXY', 'false').lower() == 'true'
    HTTP_PROXY_HOST = os.getenv('HTTP_PROXY_HOST', '127.0.0.1')
    HTTP_PROXY_PORT = int(os.getenv('HTTP_PROXY_PORT', '8080'))
    SOCKS_PROXY_HOST = os.getenv('SOCKS_PROXY_HOST', '127.0.0.1')
    SOCKS_PROXY_PORT = int(os.getenv('SOCKS_PROXY_PORT', '1080'))
    
    # 群组转发功能配置
    ENABLE_GROUP_FORWARD = os.getenv('ENABLE_GROUP_FORWARD', 'false').lower() == 'true'
    BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    
    # 监听群组配置
    groups_str = os.getenv('MONITOR_GROUPS', '')
    MONITOR_GROUPS = [g.strip() for g in groups_str.split(',') if g.strip()]
    
    # 转发过滤配置
    FORWARD_MEDIA = os.getenv('FORWARD_MEDIA', 'true').lower() == 'true'
    FORWARD_STICKERS = os.getenv('FORWARD_STICKERS', 'true').lower() == 'true'
    FORWARD_VOICE = os.getenv('FORWARD_VOICE', 'true').lower() == 'true'
    FORWARD_FORWARDED = os.getenv('FORWARD_FORWARDED', 'false').lower() == 'true'
    FORWARD_BOT_MESSAGES = os.getenv('FORWARD_BOT_MESSAGES', 'true').lower() == 'true'
    
    # 消息格式配置
    MESSAGE_PREFIX = os.getenv('MESSAGE_PREFIX', '📢 [{chat_title}] {sender_name}:')
    SHOW_MESSAGE_TIME = os.getenv('SHOW_MESSAGE_TIME', 'true').lower() == 'true'
    TIME_FORMAT = os.getenv('TIME_FORMAT', '%Y-%m-%d %H:%M:%S')
    
    # 高级配置
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '4000'))
    ENABLE_DEDUPLICATION = os.getenv('ENABLE_DEDUPLICATION', 'true').lower() == 'true'
    DEDUP_WINDOW = int(os.getenv('DEDUP_WINDOW', '60'))
    FORWARD_DELAY = float(os.getenv('FORWARD_DELAY', '1'))
    
    @classmethod
    def validate(cls):
        """验证配置是否完整"""
        if not cls.API_ID or cls.API_ID == 0:
            raise ValueError("TELEGRAM_API_ID 未设置或无效")
        
        if not cls.API_HASH:
            raise ValueError("TELEGRAM_API_HASH 未设置")
        
        if not cls.PHONE_NUMBER:
            raise ValueError("TELEGRAM_PHONE 未设置")
        
        return True
    
    @classmethod
    def validate_forward_config(cls):
        """验证转发配置"""
        if not cls.ENABLE_GROUP_FORWARD:
            return True  # 未启用转发功能，跳过验证
            
        if not cls.BOT_TOKEN:
            raise ValueError("启用群组转发但未设置 BOT_TOKEN")
        
        if ':' not in cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN 格式错误，应为 '123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ' 格式")
        
        if not cls.MONITOR_GROUPS:
            raise ValueError("启用群组转发但未设置 MONITOR_GROUPS")
        
        return True
    
    @classmethod
    def format_message_prefix(cls, chat_title: str, sender_name: str, 
                            message_time: str = "", chat_id: str = "", 
                            message_id: str = "") -> str:
        """格式化消息前缀"""
        return cls.MESSAGE_PREFIX.format(
            chat_title=chat_title,
            sender_name=sender_name,
            message_time=message_time,
            chat_id=chat_id,
            message_id=message_id
        )
