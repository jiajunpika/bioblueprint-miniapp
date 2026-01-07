"""Demo configuration."""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# API Configuration
DEFAULT_BASE_URL = os.getenv("PIKA_BASE_URL", "https://mnbvcxzlkjh9o4p.pika.art")
DEFAULT_API_KEY = os.getenv("PIKA_API_KEY", "")

# Default character ID to load
DEFAULT_CHARACTER_ID = os.getenv("DEFAULT_CHARACTER_ID", "7b061ad0-11f2-4421-9aaa-6c2686f20a05")

# Known test characters
KNOWN_CHARACTERS = [
    {"id": "7b061ad0-11f2-4421-9aaa-6c2686f20a05", "name": "Ke Wang (AI Researcher)"},
]
