import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from app import claim_message, initialize_database, matches_announcement, release_message


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


if __name__ == "__main__":
    unittest.main()