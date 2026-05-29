#!/usr/bin/env python3
"""Main entry point for the emotion-aware AI simulator."""
import os
import sys

from dotenv import load_dotenv
from openai import OpenAI

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from cli import ConversationUI

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not API_KEY:
    raise SystemExit("Set OPENAI_API_KEY in environment or .env")

client = OpenAI(api_key=API_KEY)


def main() -> None:
    profiles_dir = "profiles"
    ui = ConversationUI(client=client, model=MODEL, profiles_dir=profiles_dir)
    ui.select_or_create_profile()
    ui.conversation_loop()


if __name__ == "__main__":
    main()