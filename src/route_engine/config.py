"""Load project .env into process environment."""

from pathlib import Path

from dotenv import load_dotenv

# src/route_engine/config.py -> project root is two levels up from this file's parent
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


def load_env() -> None:
    """Load `.env` from the project root if present (does not override existing env)."""
    load_dotenv(_PROJECT_ROOT / ".env", override=False)
