import logging
import os
import re
import sqlite3
from pathlib import Path
from typing import Any, TypedDict

from dotenv import load_dotenv
from telethon import TelegramClient, errors, events


APP_DIR = Path(__file__).resolve().parent
REPLY_TEXT = "NMOD31 GARCIA - Case Discussion"
SLOT_OPEN_PATTERN = re.compile(
    r"\b(?:slots?\s+(?:are\s+)?open|open\s+slots?)\b",
    re.IGNORECASE,
)
LOGGER = logging.getLogger(__name__)

# TypedDict is only available in Python 3.8+, so we use a conditional import for older versions.
class Settings(TypedDict):
    api_id: int
    api_hash: str
    phone: str | None
    target_chat_id: int | None
    database_path: Path
    session_path: Path

 # Check if the message text matches the announcement pattern for open slots.
def matches_announcement(message_text: str | None) -> bool:
    return bool(message_text and SLOT_OPEN_PATTERN.search(message_text))

# Initialize the SQLite database for storing replied messages.
def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS replied_messages (
                chat_id INTEGER NOT NULL,
                message_id INTEGER NOT NULL,
                PRIMARY KEY (chat_id, message_id)
            )
            """
        )

# Claim a message in the database to prevent duplicate replies. Returns True if the claim was successful, False if the message was already claimed.
def claim_message(database_path: Path, chat_id: int, message_id: int) -> bool:
    with sqlite3.connect(database_path, timeout=5) as connection:
        cursor = connection.execute(
            "INSERT OR IGNORE INTO replied_messages (chat_id, message_id) VALUES (?, ?)",
            (chat_id, message_id),
        )
        return cursor.rowcount == 1

# Release a claimed message from the database, allowing it to be replied to again.
def release_message(database_path: Path, chat_id: int, message_id: int) -> None:
    with sqlite3.connect(database_path, timeout=5) as connection:
        connection.execute(
            "DELETE FROM replied_messages WHERE chat_id = ? AND message_id = ?",
            (chat_id, message_id),
        )

# Handle an incoming message event. If the message matches the announcement pattern and hasn't been replied to yet, send a reply.
async def handle_message(event: Any, settings: Settings) -> None:
    if not event.is_group or event.chat_id is None:
        return

    if settings["target_chat_id"] is not None and event.chat_id != settings["target_chat_id"]:
        return

    if not matches_announcement(event.raw_text):
        return

    database_path = settings["database_path"]
    if not claim_message(database_path, event.chat_id, event.id):
        return

    try:
        await event.respond(REPLY_TEXT)
    except errors.RPCError:
        release_message(database_path, event.chat_id, event.id)
        raise

    LOGGER.info("Posted a normal message from your account in chat %s", event.chat_id)

# Load settings from the .env file and validate them. Returns a Settings dictionary.
def load_settings() -> Settings:
    load_dotenv(APP_DIR / ".env")

    api_id_value = os.getenv("TELEGRAM_API_ID", "").strip()
    api_hash = os.getenv("TELEGRAM_API_HASH", "").strip()
    if not api_id_value or not api_hash:
        raise RuntimeError("Set TELEGRAM_API_ID and TELEGRAM_API_HASH in AutomatedReply/.env.")
    try:
        api_id = int(api_id_value)
    except ValueError as error:
        raise RuntimeError("TELEGRAM_API_ID must be an integer.") from error

    chat_id_value = os.getenv("TARGET_CHAT_ID", "").strip()
    target_chat_id = int(chat_id_value) if chat_id_value else None
    database_value = os.getenv("DATABASE_PATH", "replies.sqlite3")
    database_path = Path(database_value)
    if not database_path.is_absolute():
        database_path = APP_DIR / database_path
    session_value = os.getenv("SESSION_PATH", "telegram_user")
    session_path = Path(session_value)
    if not session_path.is_absolute():
        session_path = APP_DIR / session_path

    return {
        "api_id": api_id,
        "api_hash": api_hash,
        "phone": os.getenv("TELEGRAM_PHONE", "").strip() or None,
        "target_chat_id": target_chat_id,
        "database_path": database_path,
        "session_path": session_path,
    }

# Main entry point for the script. Sets up logging, loads settings, initializes the database, and starts the Telegram client to listen for messages.
def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    settings = load_settings()
    initialize_database(settings["database_path"])

    client = TelegramClient(
        str(settings["session_path"]),
        settings["api_id"],
        settings["api_hash"],
    )
    client.start(phone=settings["phone"])

    async def on_message(event: Any) -> None:
        await handle_message(event, settings)

    client.add_event_handler(on_message, events.NewMessage(incoming=True))
    LOGGER.info("Listening in groups for open-slot announcements")
    client.run_until_disconnected()


if __name__ == "__main__":
    main()