import os
import asyncio
from telegram import Bot

async def main():
    token = os.getenv('TOKEN')
    chat_id = os.getenv('CHAT_ID')
    bot = Bot(token=token)
    
    print("--- Testing Connection ---")
    try:
        await bot.send_message(chat_id=chat_id, text="GitHub Action Connection Success! 🚀")
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
