from datetime import datetime
from typing import Optional


class ContributionAnalyzer:
    """Analyzes user contributions against activity thresholds."""

    def __init__(
        self,
        active_from: Optional[int] = None,
        inactive_from: Optional[int] = None,
    ):
        self.active_from = active_from
        self.inactive_from = inactive_from
        if active_from is not None and inactive_from is not None:
            if active_from <= inactive_from:
                raise ValueError(
                    f"active_from ({active_from}) must be greater than "
                    f"inactive_from ({inactive_from})"
                )

    def analyze_contribution(self, last_edit: str) -> str:
        """Determine if user is active, inactive, or should be deleted based on last edit timestamp."""
        if not self.active_from or not self.inactive_from or not last_edit:
            return "none"

        year_str = last_edit[:4]
        if not year_str.isdigit():
            return "none"

        year = int(year_str)
        if year < 2001 or year > datetime.now().year:
            raise ValueError(f"Invalid year: '{year}' found in last edit timestamp: '{last_edit}'")
        if year >= self.active_from:
            return "active"
        elif year >= self.inactive_from:
            return "inactive"
        else:
            return "delete"
