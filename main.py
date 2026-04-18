from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from datetime import datetime, timedelta
import os

# Configuration from environment variables
API_ID = int(os.environ.get("API_ID", 20284828))
API_HASH = os.environ.get("API_HASH", "a980ba25306901d5c9b899414d6a9ab7")
STRING_SESSION = os.environ.get("STRING_SESSION", "1BVtsOKEBu2mCSVteN-_nv6WDQAlB_GXOlriz-YHBGeJlZXgYENIyvTptkBrW-ZoBn_HDOAYPFfJCHSut9nJrhKJYmDa4i2oXuVhPNj5dY8_qCCT98PWlKVhRcMq_DJXK_uk2xhwcQn6MMpAwv2BwcMhgQkptNKnv0Dw5fpn-cFQ_62AeX3xSEAnpwHTv0jyjdkqOE4c3hb861_tBw2SmVR0YO_bIH-JyjN8q1uT8zztQW3NbQHBTZ84YM8HTwyONz46w3CCNLFG3KV-aMrb2RgmsbIxCNRXT4cSA68HuVX_cwLX_wVVfxtGQKo-34a_-Ls4eAOOGTeIe1IvfofF897ibxAf03aY=")

app = Client("userbot", api_id=API_ID, api_hash=API_HASH, session_string=STRING_SESSION)

# Dictionary to store active groups
active_groups = {}

@app.on_message(filters.group & filters.text)
async def auto_delete_messages(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if auto-delete is active for this group
    if chat_id not in active_groups or not active_groups[chat_id]:
        return
    
    # Check if message is older than 120 seconds
    current_time = datetime.now()
    message_time = message.date
    age = (current_time - message_time).total_seconds()
    
    if age >= 120:
        try:
            await message.delete()
            print(f"Deleted old message from {message.chat.title}")
        except Exception as e:
            print(f"Failed to delete message: {e}")

@app.on_message(filters.command("qwert") & filters.group)
async def start_auto_delete(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.reply("❌ You need to be an admin to use this command!")
            return
    except:
        await message.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = True
    await message.reply("✅ Auto-delete activated!\nAll messages older than 120 seconds will be deleted.\nSend .trewq to stop.")

@app.on_message(filters.command("trewq") & filters.group)
async def stop_auto_delete(client: Client, message: Message):
    chat_id = message.chat.id
    
    # Check if user is admin
    try:
        member = await client.get_chat_member(chat_id, message.from_user.id)
        if member.status not in ["administrator", "creator"]:
            await message.reply("❌ You need to be an admin to use this command!")
            return
    except:
        await message.reply("❌ Error checking admin status!")
        return
    
    active_groups[chat_id] = False
    await message.reply("⏹️ Auto-delete stopped!")

@app.on_message(filters.command("status") & filters.group)
async def check_status(client: Client, message: Message):
    chat_id = message.chat.id
    status = active_groups.get(chat_id, False)
    status_text = "🟢 Active" if status else "🔴 Inactive"
    await message.reply(f"Auto-delete status: {status_text}")

if __name__ == "__main__":
    print("🤖 UserBot Started!")
    print("Commands:")
    print("  .qwert - Start auto-delete")
    print("  .trewq - Stop auto-delete")
    print("  .status - Check status")
    app.run()
