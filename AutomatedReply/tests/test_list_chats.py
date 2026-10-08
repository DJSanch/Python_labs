import unittest
import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

from list_chats import iter_forum_topics


class ForumTopicListingTests(unittest.TestCase):
    def test_fetches_all_topic_pages(self):
        first_topic = SimpleNamespace(id=10, top_message=101, title="First")
        second_topic = SimpleNamespace(id=20, top_message=202, title="Second")
        first_page = SimpleNamespace(
            count=2,
            topics=[first_topic],
            messages=[
                SimpleNamespace(
                    id=101,
                    date=datetime(2026, 1, 1, tzinfo=timezone.utc),
                )
            ],
        )
        second_page = SimpleNamespace(
            count=2,
            topics=[second_topic],
            messages=[
                SimpleNamespace(
                    id=202,
                    date=datetime(2026, 1, 2, tzinfo=timezone.utc),
                )
            ],
        )

        class FakeClient:
            def __init__(self):
                self.pages = [first_page, second_page]
                self.requests = []

            async def __call__(self, request):
                self.requests.append(request)
                return self.pages.pop(0)

        client = FakeClient()

        async def collect_topics():
            return [topic async for topic in iter_forum_topics(client, object())]

        topics = asyncio.run(collect_topics())

        self.assertEqual([topic.title for topic in topics], ["First", "Second"])
        self.assertEqual(len(client.requests), 2)
        self.assertEqual(client.requests[1].offset_id, 101)
        self.assertEqual(client.requests[1].offset_topic, 10)


if __name__ == "__main__":
    unittest.main()
