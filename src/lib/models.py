from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class UsernameWithSite:
    '''Represents a Wikipedia username with its associated site.'''
    username: str
    site: Optional[str] = None

@dataclass
class ContributionResult:
    '''Stores the result of analyzing a user's last contribution.'''
    username: str
    site: str
    last_edit_utc: str
    last_edit_date: str
    threshold_result: str