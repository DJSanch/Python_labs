import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from app import (
    claim_message,
    handle_message,
    initialize_database,
    matches_announcement,
    release_message,
)


class MatchesAnnouncementTests(unittest.TestCase):
    def test_matches_slots_open_from_any_sender(self):
        self.assertTrue(matches_announcement("Slots OPEN now!"))

    def test_matches_open_slots_phrase(self):
        self.assertTrue(matches_announcement("Open Slots!"))

    def test_accepts_optional_are(self):
        self.assertTrue(matches_announcement("The slots are open"))

    def test_rejects_non_open_message_and_empty_message(self):
        self.assertFalse(matches_announcement("Slots are full"))
        self.assertFalse(matches_announcement(None))


class DuplicateProtectionTests(unittest.TestCase):
    def test_claim_prevents_duplicate_reply_and_can_be_released(self):
        with TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "replies.sqlite3"
            initialize_database(database_path)

            self.assertTrue(claim_message(database_path, -1001, 42))
            self.assertFalse(claim_message(database_path, -1001, 42))
            release_message(database_path, -1001, 42)
            self.assertTrue(claim_message(database_path, -1001, 42))


class HandleMessageTests(unittest.IsolatedAsyncioTestCase):
    async def test_posts_standalone_message_in_the_triggering_topic(self):
        class FakeMessage:
            reply_to = SimpleNamespace(
                reply_to_top_id=7,
                reply_to_msg_id=42,
                forum_topic=False,
            )

            async def get_input_chat(self):
                return "test-chat"

        class FakeClient:
            async def __call__(self, request):
                self.request = request

        class FakeEvent:
            is_group = True
            chat_id = -1001
            id = 42
            raw_text = "Slots are open"
            message = FakeMessage()
            client = FakeClient()

            async def respond(self, text):
                raise AssertionError(f"Forum topic post used standalone group send: {text}")

        with TemporaryDirectory() as temporary_directory:
            database_path = Path(temporary_directory) / "replies.sqlite3"
            initialize_database(database_path)
            settings = {
                "api_id": 1,
                "api_hash": "test",
                "phone": None,
                "target_chat_id": None,
                "database_path": database_path,
                "session_path": Path(temporary_directory) / "session",
            }
            event = FakeEvent()

            await handle_message(event, settings)

            self.assertEqual(
                event.client.request.message,
                "NMOD31 GARCIA - Case Discussion",
            )
            self.assertEqual(event.client.request.reply_to.reply_to_msg_id, 7)
            self.assertEqual(event.client.request.reply_to.top_msg_id, 7)


if __name__ == "__main__":
    unittest.main()