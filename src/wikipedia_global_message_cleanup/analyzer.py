from typing import Optional


class ContributionAnalyzer:
    """Analyzes user contributions against activity thresholds."""

    def __init__(
        self,
        threshold_active: Optional[int] = None,
        threshold_inactive: Optional[int] = None,
    ):
        self.threshold_active = threshold_active
        self.threshold_inactive = threshold_inactive

    def analyze_contribution(self, last_edit: str) -> str:
        """Determine if user is active, inactive, or should be deleted based on last edit timestamp."""
        if not self.threshold_active or not self.threshold_inactive or not last_edit:
            return "none"

        year_str = last_edit[:4]
        if not year_str.isdigit():
            return "none"

        year = int(year_str)
        if year >= self.threshold_active:
            return "active"
        elif year >= self.threshold_inactive:
            return "inactive"
        else:
            return "delete"
