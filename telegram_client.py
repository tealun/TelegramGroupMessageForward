"""
Telegram客户端程序 - 用于接收消息和群组转发
"""
import asyncio
import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, Set, Optional, List
from collections import defaultdict

from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, FloodWaitError, PhoneCodeInvalidError
from telethon.tl.types import User, Chat, Channel
from config import Config

# 设置日志
logging.basicConfig(
    level=logging.DEBUG,  # 临时改为DEBUG级别
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('telegram_client.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TelegramMessageReceiver:
    """Telegram消息接收器（集成群组转发功能）"""
    
    def __init__(self):
        """初始化客户端"""
        # 验证配置
        Config.validate()
        
        # 创建客户端
        self.client = TelegramClient(
            Config.SESSION_NAME,
            Config.API_ID,
            Config.API_HASH
        )
        
        # 初始化转发功能
        self.init_forward_feature()
        
        # 注册事件处理器
        self.register_handlers()
        
    def init_forward_feature(self):
        """初始化群组转发功能"""
        # 检查是否启用转发功能
        if Config.ENABLE_GROUP_FORWARD:
            try:
                # 验证转发配置
                Config.validate_forward_config()
                
                # 创建机器人客户端
                self.bot_client = TelegramClient(
                    'bot_session',
                    Config.API_ID,
                    Config.API_HASH
                )
                
                # 消息去重缓存
                self.message_cache: Dict[str, float] = {}
                
                # 群组信息缓存
                self.group_cache: Dict[str, str] = {}
                
                # 统计信息
                self.forward_stats = {
                    'messages_received': 0,
                    'messages_forwarded': 0,
                    'messages_filtered': 0,
                    'errors': 0
                }
                
                self.forward_enabled = True
                logger.info("✅ 群组转发功能初始化完成")
                
            except Exception as e:
                logger.error(f"❌ 群组转发功能初始化失败: {e}")
                self.forward_enabled = False
        else:
            self.forward_enabled = False
            logger.info("ℹ️ 群组转发功能未启用")
        
    def register_handlers(self):
        """注册消息事件处理器"""
        
        @self.client.on(events.NewMessage)
        async def message_handler(event):
            """处理新消息"""
            # 如果启用了转发功能，先检查是否来自监听群组
            if self.forward_enabled:
                # 添加调试日志
                try:
                    chat = await event.get_chat()
                    chat_title = getattr(chat, 'title', 'Unknown')
                    logger.debug(f"🔍 收到消息 - 群组: {chat_title}, ID: {event.chat_id}, 配置的群组: {Config.MONITOR_GROUPS}")
                except:
                    logger.debug(f"🔍 收到消息 - 无法获取群组信息, chat_id: {event.chat_id}")
                
                is_monitored = await self.is_monitored_group(event)
                if is_monitored:
                    # 只有监听的群组才处理和显示消息
                    await self.handle_new_message(event)
                    await self.handle_forward_message(event)
                else:
                    logger.debug(f"⏭️ 跳过非监听群组消息: {event.chat_id}")
            else:
                # 如果未启用转发，处理所有消息（可选择性记录）
                await self.handle_new_message(event)
            
        @self.client.on(events.MessageEdited)
        async def edited_message_handler(event):
            """处理编辑的消息"""
            # 同样只处理监听的群组
            if self.forward_enabled:
                is_monitored = await self.is_monitored_group(event)
                if is_monitored:
                    await self.handle_edited_message(event)
            else:
                await self.handle_edited_message(event)
    
    async def is_monitored_group(self, event):
        """检查是否为监听的群组"""
        if not self.forward_enabled:
            return False
            
        try:
            # 获取聊天ID和群组信息
            chat_id = event.chat_id
            chat = await event.get_chat()
            
            # 添加详细调试日志
            chat_title = getattr(chat, 'title', 'Unknown')
            logger.debug(f"🔍 检查群组匹配 - 当前: {chat_title} (ID: {chat_id}), 配置: {Config.MONITOR_GROUPS}")
            
            # 检查群组ID是否匹配（支持多种格式）
            for monitor_group in Config.MONITOR_GROUPS:
                monitor_group = str(monitor_group).strip()
                
                # 方式1: 直接匹配chat_id（最常见）
                if str(monitor_group) == str(chat_id):
                    logger.debug(f"✅ 群组ID直接匹配: {monitor_group} == {chat_id}")
                    return True
                
                # 方式2: 匹配绝对值（处理正负号差异）
                if str(monitor_group) == str(abs(chat_id)):
                    logger.debug(f"✅ 群组ID绝对值匹配: {monitor_group} == {abs(chat_id)}")
                    return True
                
                # 方式3: 超级群组格式匹配 (-100 前缀)
                if str(chat_id).startswith('-100'):
                    # 提取超级群组的原始ID (移除-100前缀)
                    original_id = str(chat_id)[4:]  # 移除-100前缀
                    if str(monitor_group) == original_id:
                        logger.debug(f"✅ 超级群组ID匹配: {monitor_group} == {original_id} (来自 {chat_id})")
                        return True
                
                # 方式4: 反向超级群组格式匹配
                # 如果配置的是超级群组格式，提取原始ID进行匹配
                if monitor_group.startswith('-100'):
                    config_original_id = monitor_group[4:]  # 移除-100前缀
                    if str(config_original_id) == str(abs(chat_id)):
                        logger.debug(f"✅ 配置超级群组格式匹配: {monitor_group} -> {config_original_id} == {abs(chat_id)}")
                        return True
                
                # 方式5: 匹配用户名格式
                if (monitor_group.startswith('@') and 
                    hasattr(chat, 'username') and 
                    chat.username and 
                    monitor_group == f"@{chat.username}"):
                    logger.debug(f"✅ 群组用户名匹配: {monitor_group} == @{chat.username}")
                    return True
            
            logger.debug(f"❌ 群组不匹配: {chat_title} (ID: {chat_id}) 不在监听列表中")
            return False
            
        except Exception as e:
            logger.error(f"检查监听群组时出错: {e}")
            return False
    
    async def handle_new_message(self, event):
        """处理新消息"""
        try:
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            # 获取发送者信息
            sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
            if hasattr(sender, 'last_name') and sender.last_name:
                sender_name += f" {sender.last_name}"
            
            # 获取聊天信息
            chat_title = getattr(chat, 'title', '') or getattr(chat, 'first_name', 'Private Chat')
            
            # 消息时间
            message_time = event.date.strftime('%Y-%m-%d %H:%M:%S')
            
            # 打印消息信息
            print(f"\n{'='*50}")
            print(f"时间: {message_time}")
            print(f"聊天: {chat_title}")
            print(f"发送者: {sender_name}")
            print(f"消息ID: {event.message.id}")
            
            # 处理不同类型的消息
            if event.message.text:
                print(f"文本消息: {event.message.text}")
            
            if event.message.media:
                media_type = type(event.message.media).__name__
                print(f"媒体类型: {media_type}")
                
                # 如果是照片
                if hasattr(event.message.media, 'photo'):
                    print("包含照片")
                    
                # 如果是文档
                if hasattr(event.message.media, 'document'):
                    document = event.message.media.document
                    if hasattr(document, 'attributes'):
                        for attr in document.attributes:
                            if hasattr(attr, 'file_name'):
                                print(f"文件名: {attr.file_name}")
            
            print(f"{'='*50}")
            
            # 记录到日志
            logger.info(
                f"新消息 - 聊天: {chat_title}, 发送者: {sender_name}, "
                f"消息: {event.message.text[:50] if event.message.text else '[媒体消息]'}"
            )
            
        except Exception as e:
            logger.error(f"处理新消息时出错: {e}")
    
    async def handle_forward_message(self, event):
        """处理群组消息转发"""
        try:
            # 此函数调用前已经确认是监听的群组，直接处理转发
            self.forward_stats['messages_received'] += 1
            
            # 应用过滤规则
            if not await self.should_forward_message(event):
                self.forward_stats['messages_filtered'] += 1
                return
            
            # 转发消息
            await self.forward_message_to_bot(event)
            
        except Exception as e:
            logger.error(f"❌ 处理转发消息时出错: {e}")
            self.forward_stats['errors'] += 1
    
    async def should_forward_message(self, event) -> bool:
        """判断是否应该转发消息（简化版）"""
        try:
            message = event.message
            
            # 检查消息去重
            if Config.ENABLE_DEDUPLICATION:
                message_hash = hashlib.md5(
                    f"{event.chat_id}_{message.id}_{message.message or ''}".encode()
                ).hexdigest()
                
                current_time = time.time()
                if (message_hash in self.message_cache and 
                    current_time - self.message_cache[message_hash] < Config.DEDUP_WINDOW):
                    logger.debug(f"⏭️ 跳过重复消息: {message_hash}")
                    return False
                
                self.message_cache[message_hash] = current_time
            
            # 检查是否为转发消息
            if message.fwd_from and not Config.FORWARD_FORWARDED:
                logger.debug("⏭️ 跳过转发消息")
                return False
            
            # 检查是否为机器人消息
            sender = await event.get_sender()
            if isinstance(sender, User) and sender.bot and not Config.FORWARD_BOT_MESSAGES:
                logger.debug("⏭️ 跳过机器人消息")
                return False
            
            # 检查媒体类型
            if message.media:
                if message.photo and not Config.FORWARD_PHOTOS:
                    logger.debug("⏭️ 跳过图片消息")
                    return False
                
                if message.video and not Config.FORWARD_VIDEOS:
                    logger.debug("⏭️ 跳过视频消息")
                    return False
                
                if message.document and not Config.FORWARD_DOCUMENTS:
                    logger.debug("⏭️ 跳过文档消息")
                    return False
                
                if (message.voice or message.audio) and not Config.FORWARD_AUDIO:
                    logger.debug("⏭️ 跳过音频消息")
                    return False
                
                if message.sticker and not Config.FORWARD_STICKERS:
                    logger.debug("⏭️ 跳过贴纸消息")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 过滤消息时出错: {e}")
            return False
    
    async def forward_message_to_bot(self, event):
        """转发消息到机器人（简化版：一个开关控制模式）"""
        try:
            message = event.message
            
            # 获取发送者和群组信息
            sender = await event.get_sender()
            sender_name = "Unknown"
            if isinstance(sender, User):
                sender_name = sender.first_name or ""
                if sender.last_name:
                    sender_name += f" {sender.last_name}"
                if not sender_name.strip():
                    sender_name = sender.username or f"User_{sender.id}"
            elif hasattr(sender, 'title'):
                sender_name = sender.title
            
            chat = await event.get_chat()
            chat_title = getattr(chat, 'title', 'Unknown Group')
            
            # 确保机器人实体已初始化
            await self.ensure_bot_entity()
            
            # 简单的模式选择：下载重发 vs 直接转发
            if Config.DOWNLOAD_AND_RESEND:
                # 下载重发模式：自定义格式
                success = await self.download_and_resend_message(event, sender_name, chat_title)
                if not success:
                    # 如果下载失败（如文件太大），回退到直接转发
                    await self.direct_forward_message(event, sender_name, chat_title)
            else:
                # 直接转发模式：快速转发
                await self.direct_forward_message(event, sender_name, chat_title)
            
            # 记录成功转发
            self.forward_stats['messages_forwarded'] += 1
            
            mode_text = "下载重发" if Config.DOWNLOAD_AND_RESEND else "直接转发"
            logger.info(f"📤 {mode_text}: {chat_title} -> {sender_name}: {message.text[:50] if message.text else '[媒体消息]'}...")
            
            # 转发延迟
            if Config.FORWARD_DELAY > 0:
                await asyncio.sleep(Config.FORWARD_DELAY)
                
        except Exception as e:
            logger.error(f"❌ 转发消息失败: {e}")
            self.forward_stats['errors'] += 1
    
    async def download_and_resend_message(self, event, sender_name, chat_title):
        """下载重发模式：自定义格式，支持文件大小检查"""
        try:
            message = event.message
            
            # 检查文件大小（如果是媒体消息）
            if message.media and hasattr(message.media, 'document') and message.media.document:
                file_size_mb = message.media.document.size / (1024 * 1024)
                if file_size_mb > Config.MAX_DOWNLOAD_SIZE:
                    logger.info(f"📄 文件过大({file_size_mb:.1f}MB > {Config.MAX_DOWNLOAD_SIZE}MB)，使用直接转发")
                    return False
            
            # 生成自定义前缀
            message_time = ""
            if Config.SHOW_MESSAGE_TIME:
                message_time = event.date.strftime(Config.TIME_FORMAT)
            
            prefix = Config.format_message_prefix(
                chat_title=chat_title,
                sender_name=sender_name,
                message_time=message_time,
                chat_id=str(event.chat_id),
                message_id=str(message.id)
            )
            
            # 下载并重发消息内容
            await self.send_message_content_to_bot(event, sender_name, chat_title)
            return True
            
        except Exception as e:
            logger.error(f"❌ 下载重发失败: {e}")
            return False
    
    async def direct_forward_message(self, event, sender_name, chat_title):
        """直接转发模式：快速转发，带简单前缀"""
        try:
            # 生成简单前缀
            message_time = ""
            if Config.SHOW_MESSAGE_TIME:
                message_time = event.date.strftime(Config.TIME_FORMAT)
            
            prefix = Config.format_message_prefix(
                chat_title=chat_title,
                sender_name=sender_name,
                message_time=message_time,
                chat_id=str(event.chat_id),
                message_id=str(event.message.id)
            )
            
            # 先发送前缀信息
            await self.client.send_message(self.bot_entity, prefix)
            
            # 然后直接转发原消息
            await self.client.forward_messages(self.bot_entity, event.message)
            
        except Exception as e:
            logger.error(f"❌ 直接转发失败: {e}")
            raise
    
    async def ensure_bot_entity(self):
        """确保机器人实体已初始化"""
        if not hasattr(self, 'bot_entity'):
            try:
                # 方法1：通过token中的bot ID获取
                bot_id = Config.BOT_TOKEN.split(':')[0]
                self.bot_entity = await self.client.get_entity(int(bot_id))
                logger.info(f"✅ 获取到机器人实体: @{self.bot_entity.username} (ID: {bot_id})")
            except Exception as e1:
                try:
                    # 方法2：通过bot客户端获取自己的信息
                    if hasattr(self, 'bot_client') and self.bot_client:
                        me = await self.bot_client.get_me()
                        self.bot_entity = await self.client.get_entity(me.id)
                        logger.info(f"✅ 通过bot客户端获取到机器人实体: @{me.username}")
                    else:
                        raise Exception("无法获取机器人实体")
                except Exception as e2:
                    logger.error(f"❌ 获取机器人实体失败: {e1}, {e2}")
                    raise Exception("无法获取机器人实体，请检查BOT_TOKEN配置")
    
    async def send_message_content_to_bot(self, event, sender_name, chat_title):
        """根据消息类型发送内容到机器人（下载重发模式 - 纯净内容）"""
        try:
            message = event.message
            
            # 下载重发模式：直接发送原始内容，不添加前缀
            # 这样既没有转发标记，又保持内容的原始性
            
            # 文本消息 - 直接发送原文
            if message.text and not message.media:
                # 检查消息长度
                text_content = message.text
                if len(text_content) > Config.MAX_MESSAGE_LENGTH:
                    text_content = text_content[:Config.MAX_MESSAGE_LENGTH-3] + "..."
                
                await self.client.send_message(self.bot_entity, text_content)
                return
            
            # 图片消息 - 下载重发，保留原始说明文字
            elif message.photo:
                caption = message.text if message.text else None
                if caption and len(caption) > 1024:  # Telegram caption limit
                    caption = caption[:1021] + "..."
                
                # 下载并重新发送图片
                photo_bytes = await message.download_media(bytes)
                await self.client.send_file(
                    self.bot_entity, 
                    photo_bytes, 
                    caption=caption
                )
            
            # 文档/文件消息 - 下载重发
            elif message.document:
                caption = message.text if message.text else None
                if caption and len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                # 检查文件大小
                file_size_mb = message.document.size / (1024 * 1024)
                if file_size_mb > Config.MAX_DOWNLOAD_SIZE:
                    # 文件太大，发送提示信息
                    size_info = f"📄 文档过大({file_size_mb:.1f}MB)，无法下载"
                    await self.client.send_message(self.bot_entity, size_info)
                    return
                
                # 获取文件信息
                file_name = "document"
                if hasattr(message.document, 'attributes'):
                    for attr in message.document.attributes:
                        if hasattr(attr, 'file_name') and attr.file_name:
                            file_name = attr.file_name
                            break
                
                # 下载并重新发送文档
                file_bytes = await message.download_media(bytes)
                await self.client.send_file(
                    self.bot_entity,
                    file_bytes,
                    caption=caption,
                    file_name=file_name
                )
            
            # 视频消息 - 下载重发
            elif message.video:
                caption = message.text if message.text else None
                if caption and len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                # 检查文件大小
                file_size_mb = message.video.size / (1024 * 1024)
                if file_size_mb > Config.MAX_DOWNLOAD_SIZE:
                    size_info = f"🎥 视频过大({file_size_mb:.1f}MB)，无法下载"
                    await self.client.send_message(self.bot_entity, size_info)
                    return
                
                # 下载并重新发送视频
                video_bytes = await message.download_media(bytes)
                await self.client.send_file(
                    self.bot_entity,
                    video_bytes,
                    caption=caption
                )
            
            # 音频/语音消息 - 下载重发
            elif message.voice or message.audio:
                caption = message.text if message.text else None
                if caption and len(caption) > 1024:
                    caption = caption[:1021] + "..."
                
                # 下载并重新发送音频
                audio_bytes = await message.download_media(bytes)
                await self.client.send_file(
                    self.bot_entity,
                    audio_bytes,
                    caption=caption
                )
            
            # 贴纸 - 下载重发
            elif message.sticker:
                # 下载并重新发送贴纸，不添加任何文字说明
                sticker_bytes = await message.download_media(bytes)
                await self.client.send_file(self.bot_entity, sticker_bytes)
            
            # 位置消息 - 转换为简洁文本
            elif message.geo:
                location_text = f"📍 位置: {message.geo.lat}, {message.geo.long}"
                await self.client.send_message(self.bot_entity, location_text)
            
            # 联系人信息 - 转换为简洁文本
            elif message.contact:
                contact = message.contact
                contact_text = f"👤 {contact.first_name} {contact.last_name or ''} {contact.phone_number}"
                await self.client.send_message(self.bot_entity, contact_text)
            
            # 投票 - 转换为简洁文本
            elif message.poll:
                poll = message.poll
                poll_text = f"📊 {poll.question}\n"
                for i, answer in enumerate(poll.answers, 1):
                    poll_text += f"{i}. {answer.text}\n"
                await self.client.send_message(self.bot_entity, poll_text)
            
            # 其他类型消息
            else:
                # 发送简单提示
                await self.client.send_message(self.bot_entity, "[不支持的消息类型]")
                
        except Exception as e:
            logger.error(f"❌ 下载重发失败: {e}")
            # 发送错误提示
            try:
                await self.client.send_message(self.bot_entity, f"❌ 消息处理失败: {str(e)}")
            except:
                pass  # 避免二次错误
    
    async def validate_forward_groups(self):
        """验证群组转发配置"""
        if not self.forward_enabled:
            return
            
        logger.info("🔍 验证群组转发配置...")
        
        valid_groups = []
        for group_id in Config.MONITOR_GROUPS:
            group_id = group_id.strip()
            logger.info(f"🔍 验证群组: {group_id}")
            
            try:
                entity = None
                tested_formats = []
                
                # 准备要尝试的ID格式列表
                id_formats_to_try = []
                
                if group_id.startswith('@'):
                    # 用户名格式，直接尝试
                    id_formats_to_try.append(('username', group_id))
                else:
                    # 数字ID，尝试多种格式
                    base_id = group_id.strip('-')  # 移除可能的负号
                    
                    # 尝试所有可能的格式
                    id_formats_to_try.extend([
                        ('original', group_id),
                        ('positive', base_id),
                        ('negative', f'-{base_id}'),
                        ('bot_api_super', f'-100{base_id}'),
                    ])
                    
                    # 如果原始ID是Bot API格式，也尝试移除前缀
                    if group_id.startswith('-100'):
                        client_api_id = group_id[4:]
                        id_formats_to_try.extend([
                            ('client_api', client_api_id),
                            ('client_api_neg', f'-{client_api_id}')
                        ])
                
                # 逐一尝试每种格式
                for format_name, test_id in id_formats_to_try:
                    try:
                        tested_formats.append(f"{format_name}({test_id})")
                        
                        if test_id.startswith('@'):
                            entity = await self.client.get_entity(test_id)
                            logger.info(f"✅ 通过{format_name}格式获取成功: @{entity.username}")
                        else:
                            entity = await self.client.get_entity(int(test_id))
                            logger.info(f"✅ 通过{format_name}格式获取成功: {entity.title} (ID: {entity.id})")
                        
                        break  # 成功获取，跳出循环
                        
                    except Exception as e:
                        logger.debug(f"{format_name}格式({test_id})失败: {e}")
                        continue
                
                # 验证是否为群组/频道
                if entity and isinstance(entity, (Chat, Channel)):
                    group_title = entity.title
                    actual_id = entity.id
                    
                    valid_groups.append(actual_id)  # 使用实际的ID
                    self.group_cache[str(actual_id)] = group_title
                    
                    logger.info(f"✅ 群组验证成功: {group_title} (实际ID: {actual_id})")
                    
                    # 如果配置的ID与实际ID不同，给出提示
                    if str(actual_id) != group_id:
                        logger.info(f"💡 建议配置使用实际ID: {actual_id} 而不是 {group_id}")
                        
                elif entity:
                    logger.warning(f"⚠️ {group_id} 不是群组/频道类型，跳过")
                else:
                    logger.error(f"❌ 无法获取群组实体: {group_id}")
                    logger.info(f"� 已尝试的格式: {', '.join(tested_formats)}")
                    logger.info(f"�💡 可能的原因: 1)未加入此群组 2)群组ID错误 3)群组已删除")
                    
            except Exception as e:
                logger.error(f"❌ 验证群组 {group_id} 时出错: {e}")
        
        if valid_groups:
            # 更新配置为实际有效的ID
            Config.MONITOR_GROUPS = [str(gid) for gid in valid_groups]
            logger.info(f"📊 共验证了 {len(valid_groups)} 个有效群组")
            logger.info(f"📋 有效群组ID: {Config.MONITOR_GROUPS}")
        else:
            logger.warning("⚠️ 没有可访问的群组，转发功能将被禁用")
            logger.info("💡 请检查:")
            logger.info("   1. 确认您的账号已加入这些群组")
            logger.info("   2. 检查群组ID是否正确")
            logger.info("   3. 尝试使用群组用户名（@username）代替ID")
            self.forward_enabled = False
    
    async def start_forward_cleanup_task(self):
        """启动转发功能的定期清理任务"""
        if not self.forward_enabled:
            return
            
        async def cleanup_task():
            while True:
                try:
                    await asyncio.sleep(300)  # 每5分钟执行一次
                    
                    # 清理过期的消息缓存
                    current_time = time.time()
                    expired_keys = [
                        key for key, timestamp in self.message_cache.items()
                        if current_time - timestamp > Config.DEDUP_WINDOW
                    ]
                    
                    for key in expired_keys:
                        del self.message_cache[key]
                    
                    # 输出统计信息
                    logger.info(f"📊 转发统计: 接收 {self.forward_stats['messages_received']}, "
                              f"转发 {self.forward_stats['messages_forwarded']}, "
                              f"过滤 {self.forward_stats['messages_filtered']}, "
                              f"错误 {self.forward_stats['errors']}")
                    
                except Exception as e:
                    logger.error(f"❌ 定期清理出错: {e}")
        
        asyncio.create_task(cleanup_task())
    async def handle_edited_message(self, event):
        """处理编辑的消息"""
        try:
            sender = await event.get_sender()
            chat = await event.get_chat()
            
            sender_name = getattr(sender, 'first_name', '') or getattr(sender, 'title', 'Unknown')
            chat_title = getattr(chat, 'title', '') or getattr(chat, 'first_name', 'Private Chat')
            
            print(f"\n[编辑消息] {chat_title} - {sender_name}: {event.message.text}")
            logger.info(f"消息编辑 - 聊天: {chat_title}, 发送者: {sender_name}")
            
        except Exception as e:
            logger.error(f"处理编辑消息时出错: {e}")
    
    async def _custom_start(self):
        """自定义启动流程，支持环境变量验证码"""
        import os
        import sys
        
        try:
            # 如果已经有有效session，直接连接
            await self.client.connect()
            if await self.client.is_user_authorized():
                print("✅ 使用已有session登录成功")
                return
            
            # 需要重新认证
            print("📱 需要进行身份验证...")
            
            # 发送验证码
            sent = await self.client.send_code_request(Config.PHONE_NUMBER)
            
            # 尝试从环境变量获取验证码
            verification_code = os.getenv('TELEGRAM_CODE')
            if verification_code:
                print(f"🔑 使用环境变量中的验证码: {verification_code}")
                try:
                    await self.client.sign_in(Config.PHONE_NUMBER, verification_code)
                    print("✅ 验证码验证成功")
                    return
                except PhoneCodeInvalidError:
                    print("❌ 环境变量中的验证码无效")
                    # 清除无效的验证码
                    if 'TELEGRAM_CODE' in os.environ:
                        del os.environ['TELEGRAM_CODE']
            
            # 如果没有环境变量或验证码无效，检查是否为交互式环境
            if sys.stdin.isatty():
                # 交互式环境，提示用户输入
                verification_code = input("请输入验证码: ")
                await self.client.sign_in(Config.PHONE_NUMBER, verification_code)
            else:
                # 非交互式环境，提示如何设置环境变量
                print("❌ 非交互式环境，无法输入验证码")
                print("💡 请设置环境变量 TELEGRAM_CODE='您的验证码' 然后重新运行")
                print("   例如: export TELEGRAM_CODE='12345' && python telegram_client.py")
                raise RuntimeError("需要验证码但无法在非交互式环境中获取")
                
        except SessionPasswordNeededError:
            # 需要两步验证密码
            password = os.getenv('TELEGRAM_PASSWORD')
            if password:
                print("🔐 使用环境变量中的两步验证密码")
                await self.client.sign_in(password=password)
            elif sys.stdin.isatty():
                password = input("请输入两步验证密码: ")
                await self.client.sign_in(password=password)
            else:
                print("❌ 需要两步验证密码但无法在非交互式环境中获取")
                print("💡 请设置环境变量 TELEGRAM_PASSWORD='您的密码' 然后重新运行")
                raise RuntimeError("需要两步验证密码但无法在非交互式环境中获取")
    
    async def start(self):
        """启动客户端"""
        try:
            print("正在连接到Telegram...")
            
            # 自定义启动流程，支持环境变量验证码
            await self._custom_start()
            
            # 获取当前用户信息
            me = await self.client.get_me()
            print(f"成功登录! 用户: {me.first_name} {me.last_name or ''}")
            print(f"用户名: @{me.username or 'None'}")
            print(f"电话: {me.phone}")
            
            # 如果启用了转发功能，启动机器人客户端
            if self.forward_enabled:
                print("\n🤖 启动群组转发功能...")
                try:
                    await self.bot_client.start(bot_token=Config.BOT_TOKEN)
                    bot_me = await self.bot_client.get_me()
                    print(f"✅ 机器人登录成功: {bot_me.first_name} (@{bot_me.username})")
                    
                    # 初始化机器人实体
                    await self.ensure_bot_entity()
                    
                    # 验证群组配置
                    await self.validate_forward_groups()
                    
                    if self.forward_enabled:
                        print(f"📡 开始监听 {len(Config.MONITOR_GROUPS)} 个群组的消息转发...")
                        # 启动定期清理任务
                        await self.start_forward_cleanup_task()
                    
                except Exception as e:
                    logger.error(f"❌ 机器人启动失败: {e}")
                    self.forward_enabled = False
                    print("⚠️ 转发功能已禁用，仅运行消息接收功能")
            
            print(f"\n开始监听消息... (按 Ctrl+C 退出)")
            if self.forward_enabled:
                print("💡 群组转发功能已启用")
            
            # 保持客户端运行
            await self.client.run_until_disconnected()
            
        except Exception as e:
            logger.error(f"启动客户端时出错: {e}")
            raise
    
    async def stop(self):
        """停止客户端"""
        if self.client.is_connected():
            await self.client.disconnect()
            print("客户端已断开连接")
        
        if self.forward_enabled and hasattr(self, 'bot_client') and self.bot_client.is_connected():
            await self.bot_client.disconnect()
            print("机器人客户端已断开连接")

async def main():
    """主函数"""
    receiver = None
    try:
        receiver = TelegramMessageReceiver()
        await receiver.start()
    except KeyboardInterrupt:
        print("\n\n收到退出信号...")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
    finally:
        if receiver:
            await receiver.stop()

if __name__ == "__main__":
    # 运行客户端
    asyncio.run(main())
