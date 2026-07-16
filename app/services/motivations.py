"""Loads and serves motivational quotes from motivations.json."""
import json
import random
from pathlib import Path

from loguru import logger

from app.core.config import settings


def _load_quotes() -> list[str]:
    """Load quotes from motivations.json next to font files (FONT_DIR) or project root."""
    candidates = [
        settings.font_dir / "motivations.json",
        Path(__file__).parent.parent.parent / "motivations.json",
    ]
    for path in candidates:
        if path.exists():
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list) and data:
                    logger.info("Loaded {} motivational quotes from {}", len(data), path)
                    return data
            except Exception as exc:
                logger.warning("Could not load {}: {}", path, exc)
    logger.warning("motivations.json not found — motivational quotes disabled")
    return []


_QUOTES: list[str] = _load_quotes()


def get_random_quote() -> str | None:
    """Return a random quote, or None if no quotes are available."""
    if not _QUOTES:
        return None
    return random.choice(_QUOTES)
