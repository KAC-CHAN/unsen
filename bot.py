import asyncio
import aiohttp
import json
from pyrogram import Client, filters, enums

# ------------------------------------------------------------------
# CONFIGURATION
# Paste your credentials here inside the quotes
# ------------------------------------------------------------------
API_ID = 26788480  
API_HASH = "858d65155253af8632221240c535c314"
BOT_TOKEN = "7810310232:AAFQTXco4XhiB1oZrS9fcsxgxPpdYd8s0eA"

# OpenRouter Configuration
OPENROUTER_API_KEY = "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"
MODEL_NAME = "cognitivecomputations/dolphin-mistral-24b-venice-edition:free"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# ------------------------------------------------------------------
# BOT SETUP
# ------------------------------------------------------------------

# Initialize the Pyrogram Client
app = Client(
    "pro_dev_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# System instruction to define the "Super Pro Developer" persona
SYSTEM_PROMPT = (
    "You are a Super Pro Developer and Expert Programmer AI. "
    "You possess deep knowledge of software engineering, algorithms, system design, and modern tech stacks. "
    "Your answers are precise, high-quality, and follow best practices. "
    "When providing code, ensure it is clean, efficient, and well-commented. "
    "Avoid verbose fluff; focus on technical accuracy and solving the user's problem."
)

async def get_ai_response(user_message):
    """
    Sends the user message to OpenRouter and retrieves the AI's response.
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://telegram.org", # Required by OpenRouter for ranking
        "X-Title": "ProDevTelegramBot"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7, # Adjust for creativity vs precision
        "top_p": 1,
        "repetition_penalty": 1.1
    }

    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(OPENROUTER_URL, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    # Extract the content from the response
                    return data['choices'][0]['message']['content']
                else:
                    error_text = await response.text()
                    print(f"API Error: {error_text}")
                    return f"⚠️ Error from AI Provider: {response.status}"
        except Exception as e:
            print(f"Connection Error: {e}")
            return "⚠️ A connection error occurred while contacting the AI."

@app.on_message(filters.text & filters.private)
async def handle_message(client, message):
    """
    Handles incoming text messages from private chats.
    """
    user_text = message.text

    # Send a "Typing..." action so the user knows the bot is thinking
    await client.send_chat_action(chat_id=message.chat.id, action=enums.ChatAction.TYPING)

    # Get response from OpenRouter
    ai_reply = await get_ai_response(user_text)

    # Reply to the user (using Markdown parsing for code blocks)
    try:
        await message.reply_text(ai_reply)
    except Exception as e:
        # Fallback if markdown parsing fails due to unclosed tags
        await message.reply_text(ai_reply, quote=True, parse_mode=enums.ParseMode.DISABLED)

# ------------------------------------------------------------------
# RUN THE BOT
# ------------------------------------------------------------------
if __name__ == "__main__":
    print("🤖 Super Pro Developer Bot is starting...")
    app.run()
