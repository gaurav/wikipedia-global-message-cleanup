import logging
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
        if inactive_from is not None and active_from is None:
            logging.warning(
                "--inactive-from is set without --active-from; "
                "users will be classified as inactive or delete, never active"
            )

    def analyze_contribution(self, last_edit: str) -> str:
        """Determine if user is active, inactive, or should be deleted based on last edit timestamp."""
        if not self.active_from and not self.inactive_from:
            return "none"
        if not last_edit:
            return "none"

        year_str = last_edit[:4]
        if not year_str.isdigit():
            return "none"

        year = int(year_str)
        if year < 2001 or year > datetime.now().year:
            raise ValueError(f"Invalid year: '{year}' found in last edit timestamp: '{last_edit}'")

        if self.active_from is not None and self.inactive_from is not None:
            if year >= self.active_from:
                return "active"
            elif year >= self.inactive_from:
                return "inactive"
            else:
                return "delete"
        elif self.active_from is not None:
            return "active" if year >= self.active_from else "delete"
        else:  # inactive_from only
            return "inactive" if year >= self.inactive_from else "delete"
