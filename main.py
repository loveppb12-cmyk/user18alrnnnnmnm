from pyrogram import Client, filters
from pyrogram.types import Message
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
STRING_SESSION = os.environ.get("STRING_SESSION", "1BVtsOKEBu2mCSVteN-_nv6WDQAlB_GXOlriz-YHBGeJlZXgYENIyvTptkBrW-ZoBn_HDOAYPFfJCHSut9nJrhKJYmDa4i2oXuVhPNj5dY8_qCCT98PWlKVhRcMq_DJXK_uk2xhwcQn6MMpAwv2BwcMhgQkptNKnv0Dw5fpn-cFQ_62AeX3xSEAnpwHTv0jyjdkqOE4c3hb861_tBw2SmVR0YO_bIH-JyjN8q1uT8zztQW3NbQHBTZ84YM8HTwyONz46w3CCNLFG3KV-aMrb2RgmsbIxCNRXT4cSA68HuVX_cwLX_wVVfxtGQKo-34a_-Ls4eAOOGTeIe1IvfofF897ibxAf03aY=")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# Dictionary to store active groups
active_groups = {}

# Keep track of processed messages to avoid double deletion
processed_messages = set()

@app.on_message(filters.group & ~filters.bot)
async def auto_delete_messages(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if auto-delete is active for this group
    if chat_id not in active_groups or not active_groups[chat_id]:
        return
    
    # Avoid processing same message twice
    if message.id in processed_messages:
        return
    
    processed_messages.add(message.id)
    
    # Calculate message age
    current_time = datetime.now()
    message_time = message.date
    age = (current_time - message_time).total_seconds()
    
    # Also delete bot messages if needed
    if age >= 120:
        try:
            await asyncio.sleep(1)  # Small delay to avoid rate limits
            await message.delete()
            logger.info(f"Deleted message {message.id} from {message.chat.title}")
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
    
    # Clean up processed_messages set occasionally
    if len(processed_messages) > 1000:
        processed_messages.clear()

@app.on_message(filters.command("qwert") & filters.group)
async def start_auto_delete(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.reply("❌ You need to be an admin to use this command!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        await message.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = True
    await message.reply("✅ **Auto-delete activated!**\n\n"
                       "📝 All messages older than 120 seconds will be deleted.\n"
                       "🛑 Send `.trewq` to stop.\n"
                       "📊 Send `.status` to check status.")

@app.on_message(filters.command("trewq") & filters.group)
async def stop_auto_delete(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.reply("❌ You need to be an admin to use this command!")
            return
    except Exception as e:
        logger.error(f"Error checking admin status: {e}")
        await message.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = False
    await message.reply("⏹️ **Auto-delete stopped!**\n\n"
                       "Messages will no longer be automatically deleted.")

@app.on_message(filters.command("status") & filters.group)
async def check_status(client: Client, message: Message):
    chat_id = message.chat.id
    status = active_groups.get(chat_id, False)
    
    if status:
        status_text = "🟢 **ACTIVE**"
        await message.reply(f"{status_text}\n\n"
                           f"📋 Messages older than 120 seconds are being deleted.\n"
                           f"🎯 Chat ID: `{chat_id}`")
    else:
        status_text = "🔴 **INACTIVE**"
        await message.reply(f"{status_text}\n\n"
                           f"⏸️ Auto-delete is not running.\n"
                           f"🚀 Send `.qwert` to activate.")

@app.on_message(filters.command("help") & filters.group)
async def help_command(client: Client, message: Message):
    await message.reply("📚 **Auto-Delete UserBot Commands**\n\n"
                       "🔹 `.qwert` - Start auto-deleting old messages\n"
                       "🔹 `.trewq` - Stop auto-deleting\n"
                       "🔹 `.status` - Check current status\n"
                       "🔹 `.help` - Show this help message\n\n"
                       "⚙️ **Features:**\n"
                       "• Deletes messages older than 120 seconds\n"
                       "• Works on all member messages\n"
                       "• Only admins can control the bot\n\n"
                       "⚠️ Make sure the bot has admin rights with 'Delete Messages' permission!")

@app.on_message(filters.command("start") & filters.private)
async def start_private(client: Client, message: Message):
    await message.reply("🤖 **Welcome to Auto-Delete UserBot!**\n\n"
                       "Add me to your group as an admin with 'Delete Messages' permission.\n"
                       "Then use these commands in the group:\n"
                       "• `.qwert` - Start auto-delete\n"
                       "• `.trewq` - Stop auto-delete\n"
                       "• `.status` - Check status")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 AUTO-DELETE USERBOT STARTED")
    print("=" * 50)
    print("📝 Commands available in groups:")
    print("   .qwert  - Start auto-delete")
    print("   .trewq  - Stop auto-delete")
    print("   .status - Check status")
    print("   .help   - Show help")
    print("=" * 50)
    print("✅ Bot is running...")
    print("=" * 50)
    
    app.run()
