import os
from collections.abc import AsyncIterator
from typing import Any

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.messages import GetForumTopicsRequest
from telethon.tl.types import ForumTopic


async def iter_forum_topics(
    client: TelegramClient,
    entity: Any,
) -> AsyncIterator[ForumTopic]:
    offset_date = None
    offset_id = 0
    offset_topic = 0
    seen_topic_ids: set[int] = set()
    previous_cursor = None

    while True:
        page = await client(
            GetForumTopicsRequest(
                peer=entity,
                offset_date=offset_date,
                offset_id=offset_id,
                offset_topic=offset_topic,
                limit=100,
            )
        )
        topics = page.topics
        for topic in topics:
            if topic.id not in seen_topic_ids:
                seen_topic_ids.add(topic.id)
                yield topic

        if not topics or len(seen_topic_ids) >= page.count:
            return

        last_topic = topics[-1]
        last_message = next(
            (message for message in page.messages if message.id == last_topic.top_message),
            None,
        )
        if last_message is None:
            raise RuntimeError(
                f"Could not find the last message for forum topic {last_topic.id}."
            )

        cursor = (last_message.date, last_message.id, last_topic.id)
        if cursor == previous_cursor:
            raise RuntimeError("Telegram returned the same forum-topic page twice.")
        previous_cursor = cursor
        offset_date, offset_id, offset_topic = cursor

load_dotenv()


def main() -> None:
    client = TelegramClient(
        "telegram_user",
        int(os.environ["TELEGRAM_API_ID"]),
        os.environ["TELEGRAM_API_HASH"],
    )

    with client:
        client.loop.run_until_complete(list_groups(client))


async def list_groups(client: TelegramClient) -> None:
    await client.start(phone=os.getenv("TELEGRAM_PHONE") or None)
    async for dialog in client.iter_dialogs():
        if not dialog.is_group:
            continue

        print(f"Group: {dialog.name} (ID: {dialog.id})")
        if getattr(dialog.entity, "forum", False):
            async for topic in iter_forum_topics(client, dialog.entity):
                print(f"  Topic: {topic.title} (ID: {topic.id})")


if __name__ == "__main__":
    main()