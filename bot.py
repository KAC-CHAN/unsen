import asyncio
import aiohttp
import io
import re
from pyrogram import Client, filters, enums

# --- CONFIGURATION ---
API_ID = 26788480  
API_HASH = "858d65155253af8632221240c535c314"
BOT_TOKEN = "7810310232:AAFQTXco4XhiB1oZrS9fcsxgxPpdYd8s0eA"

OPENROUTER_API_KEY = "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"
MODEL_NAME = "nvidia/nemotron-3-nano-30b-a3b:free"
OPENROUTER_URL = "[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)"

app = Client("pro_dev_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SYSTEM_PROMPT = (
    "You are a Super Pro Developer AI. Provide expert-level code. "
    "Always wrap code in backticks like this: ```python code here ```."
)

async def get_ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "[https://github.com/KAC-CHAN/unsen](https://github.com/KAC-CHAN/unsen)"
    }
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ]
    }
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(OPENROUTER_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    return data['choices'][0]['message']['content']
                return f"⚠️ API Error: {response.status}"
        except Exception as e:
            return f"⚠️ Connection Failed: {str(e)}"

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)
    ai_reply = await get_ai_response(message.text)

    # 1. Check if response is very long (> 3000 chars) OR contains code blocks
    if len(ai_reply) > 3000 or "```" in ai_reply:
        # Create an in-memory file to avoid saving to disk
        doc = io.BytesIO(ai_reply.encode())
        doc.name = "ai_response.txt"
        
        caption = "📄 **Response generated!**\nThe output was too long or contained code, so I've sent it as a file to preserve formatting."
        
        await message.reply_document(
            document=doc,
            caption=caption,
            parse_mode=enums.ParseMode.MARKDOWN
        )
    else:
        # 2. For short text-only replies, send as normal message
        await message.reply_text(ai_reply, parse_mode=enums.ParseMode.MARKDOWN)

if __name__ == "__main__":
    print("🤖 Bot started. Long responses will be sent as files.")
    app.run()
