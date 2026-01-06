"""Demo configuration."""

import os

# API Configuration
DEFAULT_BASE_URL = os.getenv("PIKA_BASE_URL", "https://mnbvcxzlkjh9o4p.pika.art")
DEFAULT_API_KEY = os.getenv("PIKA_API_KEY", "")

# Known test characters (temporary solution until list API is available)
# Format: {"id": "character-uuid", "name": "Display Name"}
KNOWN_CHARACTERS = [
    # Add your test character IDs here
    # {"id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx", "name": "Test Character 1"},
]
