"""
export_session_string.py — Helper script to export your local Telethon session as a StringSession.
Copy the printed string and set it as TELEGRAM_SESSION_STRING in your Render environment variables.
"""

from __future__ import annotations

import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

from config import settings


async def main() -> None:
    print(f"Loading local session file: {settings.telegram_session_name}.session")
    client = TelegramClient(
        settings.telegram_session_name,
        settings.telegram_api_id,
        settings.telegram_api_hash,
    )
    await client.connect()
    if not await client.is_user_authorized():
        print("Local session is not authorized. Starting interactive login...")
        await client.start()

    session_str = StringSession.save(client.session)
    await client.disconnect()

    print()
    print("=" * 70)
    print("YOUR TELEGRAM_SESSION_STRING:")
    print("=" * 70)
    print(session_str)
    print("=" * 70)
    print()
    print("Copy the string above and set it as TELEGRAM_SESSION_STRING")
    print("in your Render dashboard (Environment -> Add Environment Variable).")


if __name__ == "__main__":
    asyncio.run(main())
