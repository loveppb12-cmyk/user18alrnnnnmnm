from telethon import TelegramClient, events, Button
from telethon.tl.types import MessageEntityMentionName
import asyncio
from datetime import datetime, timedelta
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration from environment variables
API_ID = int(os.environ.get("API_ID", 20284828))
API_HASH = os.environ.get("API_HASH", "a980ba25306901d5c9b899414d6a9ab7")
STRING_SESSION = os.environ.get("STRING_SESSION", "1BVtsOKEBu8JXufWBkIppw4YfMJidZE5hJQRijwRMx9Bm9pKE9E9J4ulEpDm6Z9tE5bBffZ3whvsa5-DRy83fIGBBTJD_q5hSPNHLrqVNpJrQS3iYn4DZa_7mv8mmG33MDaQXnyq2GFaoTCUcqOvAGNnunaWrTuD-2hivZGjn_SbeX7GW7XbJOwxrSaaeXqANvZIHxij1XBSjIobmzGOib7Hn9ulPA7dML-gw35bQZk4ZbudlXSGkpSKqtnCugRkR-dN-gLw1di-MLdVy85qk1baPcAUMLtOb3oAFewe4wVgnN5227iRL96NrqqWRwy3HVmxf2_Qjs09QGd-BlFsuEGkIRtqZzFE=")

# Create client with string session
client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)

# Dictionary to store active groups
active_groups = {}

@client.on(events.NewMessage(pattern=r'\.qwert$'))
async def start_auto_delete(event):
    chat_id = event.chat_id
    
    # Check if user is admin
    try:
        sender = await event.get_sender()
        participant = await event.client.get_permissions(event.chat_id, sender.id)
        
        if not participant.is_admin and not participant.is_creator:
            await event.reply("❌ You need to be an admin to use this command!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        await event.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = True
    await event.reply("✅ **Auto-delete activated!**\n\n"
                     "📝 All messages older than 120 seconds will be deleted.\n"
                     "🛑 Send `.trewq` to stop.\n"
                     "📊 Send `.status` to check status.")

@client.on(events.NewMessage(pattern=r'\.trewq$'))
async def stop_auto_delete(event):
    chat_id = event.chat_id
    
    # Check if user is admin
    try:
        sender = await event.get_sender()
        participant = await event.client.get_permissions(event.chat_id, sender.id)
        
        if not participant.is_admin and not participant.is_creator:
            await event.reply("❌ You need to be an admin to use this command!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        await event.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = False
    await event.reply("⏹️ **Auto-delete stopped!**\n\n"
                     "Messages will no longer be automatically deleted.")

@client.on(events.NewMessage(pattern=r'\.status$'))
async def check_status(event):
    chat_id = event.chat_id
    status = active_groups.get(chat_id, False)
    
    if status:
        await event.reply(f"🟢 **AUTO-DELETE ACTIVE**\n\n"
                         f"📋 Messages older than 120 seconds are being deleted.\n"
                         f"🎯 Chat ID: `{chat_id}`")
    else:
        await event.reply(f"🔴 **AUTO-DELETE INACTIVE**\n\n"
                         f"⏸️ Auto-delete is not running.\n"
                         f"🚀 Send `.qwert` to activate.")

@client.on(events.NewMessage(pattern=r'\.help$'))
async def help_command(event):
    await event.reply("📚 **Auto-Delete UserBot Commands**\n\n"
                     "🔹 `.qwert` - Start auto-deleting old messages\n"
                     "🔹 `.trewq` - Stop auto-deleting\n"
                     "🔹 `.status` - Check current status\n"
                     "🔹 `.help` - Show this help message\n\n"
                     "⚙️ **Features:**\n"
                     "• Deletes messages older than 120 seconds\n"
                     "• Works on all messages (members & bots)\n"
                     "• Only admins can control the bot\n\n"
                     "⚠️ **Setup:**\n"
                     "1. Add this bot as admin\n"
                     "2. Grant 'Delete Messages' permission\n"
                     "3. Send `.qwert` to start")

# Background task to delete old messages
@client.on(events.NewMessage)
async def delete_old_messages(event):
    chat_id = event.chat_id
    
    # Skip if not a group or auto-delete not active
    if not event.is_group:
        return
    
    if chat_id not in active_groups or not active_groups[chat_id]:
        return
    
    # Don't delete command messages immediately
    if event.raw_text and event.raw_text.startswith('.'):
        return
    
    # Check message age
    current_time = datetime.now(event.message.date.tzinfo)
    message_age = (current_time - event.message.date).total_seconds()
    
    if message_age >= 120:
        try:
            await asyncio.sleep(0.5)  # Small delay to avoid rate limits
            await event.delete()
            logger.info(f"Deleted old message from chat {chat_id}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")

# Periodic cleanup for messages that were already old when bot started
async def periodic_cleanup():
    while True:
        await asyncio.sleep(60)  # Check every minute
        
        for chat_id in active_groups:
            if not active_groups[chat_id]:
                continue
                
            try:
                # Get recent messages
                async for message in client.iter_messages(chat_id, limit=100):
                    if message.date:
                        current_time = datetime.now(message.date.tzinfo)
                        age = (current_time - message.date).total_seconds()
                        
                        if age >= 120 and not (message.raw_text and message.raw_text.startswith('.')):
                            try:
                                await message.delete()
                                await asyncio.sleep(0.3)
                            except:
                                pass
            except Exception as e:
                logger.error(f"Periodic cleanup error in {chat_id}: {e}")

@client.on(events.NewMessage(pattern=r'\.start$', func=lambda e: e.is_private))
async def start_private(event):
    await event.reply("🤖 **Welcome to Auto-Delete UserBot!**\n\n"
                     "Add me to your group as an admin with 'Delete Messages' permission.\n\n"
                     "**Quick Setup:**\n"
                     "1️⃣ Add me to your group\n"
                     "2️⃣ Make me admin with delete rights\n"
                     "3️⃣ Send `.qwert` in the group to start\n\n"
                     "**Commands:**\n"
                     "• `.qwert` - Start auto-delete\n"
                     "• `.trewq` - Stop auto-delete\n"
                     "• `.status` - Check status\n"
                     "• `.help` - Show help")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AUTO-DELETE USERBOT (TELETHON) STARTED")
    print("=" * 50)
    print("📝 Commands available in groups:")
    print("   .qwert  - Start auto-delete")
    print("   .trewq  - Stop auto-delete")
    print("   .status - Check status")
    print("   .help   - Show help")
    print("=" * 50)
    print("✅ Bot is running...")
    print("=" * 50)
    
    # Start periodic cleanup task
    loop = asyncio.get_event_loop()
    loop.create_task(periodic_cleanup())
    
    # Run client
    client.run_until_disconnected()
