import asyncio
import aiohttp
from pyrogram import Client, filters, enums

# --- CONFIGURATION ---
API_ID = 26788480  
API_HASH = "858d65155253af8632221240c535c314"
BOT_TOKEN = "7810310232:AAFQTXco4XhiB1oZrS9fcsxgxPpdYd8s0eA"

OPENROUTER_API_KEY = "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"
MODEL_NAME = "nvidia/nemotron-3-nano-30b-a3b:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- BOT SETUP ---
app = Client("pro_dev_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

SYSTEM_PROMPT = (
    "You are a Super Pro Developer AI. Provide expert-level, efficient code and technical advice. "
    "Be direct and precise."
)

def split_text(text, limit=4000):
    """
    Splits a long string into chunks without breaking words or code blocks where possible.
    """
    if len(text) <= limit:
        return [text]
    
    chunks = []
    while text:
        if len(text) <= limit:
            chunks.append(text)
            break
        
        # Try to find the last newline within the limit to keep formatting clean
        split_at = text.rfind("\n", 0, limit)
        
        # If no newline, try to find the last space
        if split_at == -1:
            split_at = text.rfind(" ", 0, limit)
            
        # If still no space, just hard cut at the limit
        if split_at == -1:
            split_at = limit
            
        chunks.append(text[:split_at].strip())
        text = text[split_at:].strip()
        
    return chunks

async def get_ai_response(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/KAC-CHAN/unsen",
        "X-Title": "ProDevBot"
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
                elif response.status == 429:
                    return "⚠️ Error: The AI is rate-limited. Please wait a moment."
                else:
                    return f"⚠️ API Error: {response.status}"
        except Exception as e:
            return f"⚠️ Connection Failed: {str(e)}"

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    user_text = message.text
    await client.send_chat_action(message.chat.id, enums.ChatAction.TYPING)

    ai_reply = await get_ai_response(user_text)
    
    # SPLIT THE MESSAGE BEFORE SENDING
    parts = split_text(ai_reply)

    for part in parts:
        try:
            # Try sending with Markdown
            await message.reply_text(part, parse_mode=enums.ParseMode.MARKDOWN)
        except Exception:
            # Fallback to plain text if Markdown is broken (e.g. unclosed backticks)
            await message.reply_text(part, parse_mode=enums.ParseMode.DISABLED)
        
        # Short delay between parts to avoid Telegram's flood limits
        await asyncio.sleep(0.5)

if __name__ == "__main__":
    print("🤖 Bot is active. Handling long messages enabled.")
    app.run()
