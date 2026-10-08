# Telegram Automated Reply

This client watches Telegram groups for a message containing `slot open`,
`slots open`, `slots are open`, `open slot`, or `open slots`, then replies to
that message from your personal Telegram account. In groups with topics, the
reply stays in the topic where the matching message was posted. Any sender can
trigger the reply. Replies are visible as your account. It uses Telegram's
client API through Telethon, not a bot account.

## Setup

1. Get your Telegram API ID and API hash from `my.telegram.org` under API
   development tools.
2. Make sure your personal account is already a member of the target group.
3. Copy `.env.example` to `.env` and set `TELEGRAM_API_ID` and
   `TELEGRAM_API_HASH`. Set `TELEGRAM_PHONE` to your account's phone number.
   `TARGET_CHAT_ID` is optional; when set, the client listens only to that group.
4. Install dependencies and start the client from this folder:

   ```sh
   python -m pip install -r requirements.txt
   python app.py
   ```

To list groups and, for groups with topics enabled, their topic names and IDs,
run `python list_chats.py` from this folder after setup.

On first start, Telegram will send a login code to your account. Enter it in
the terminal; enter your two-step verification password there too if prompted.
Do not share these values. Telethon stores an authenticated session in
`telegram_user.session`, which grants access to your account and must remain
private. The `.gitignore` excludes it. Keep the process running for replies.
The local SQLite database
prevents replying twice to the same Telegram message, including after a restart.
The client cannot respond to messages sent before it was running or while it was
offline.

## Test

Run the focused matcher and duplicate-protection tests from this folder:

```sh
python -m unittest discover -s tests
```

## Important Telegram behavior

The client can only monitor groups your account has joined. If `TARGET_CHAT_ID`
is unset, matching messages in any group your account has joined can trigger a
reply. Automatic replies are sent from your account, so use the client only
where automated replies are permitted.