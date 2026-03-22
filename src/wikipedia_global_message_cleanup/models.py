from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UsernameWithSite:
    """Represents a Wikipedia username with its associated site."""

    username: str
    site: Optional[str] = None

