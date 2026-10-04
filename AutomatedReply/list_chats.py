import os

from dotenv import load_dotenv
from telethon import TelegramClient

load_dotenv()

client = TelegramClient(
    "telegram_user",
    int(os.environ["TELEGRAM_API_ID"]),
    os.environ["TELEGRAM_API_HASH"],
)

with client:
    client.start(phone=os.getenv("TELEGRAM_PHONE") or None)
    for dialog in client.iter_dialogs():
        if dialog.is_group:
            print(f"{dialog.name}: {dialog.id}")