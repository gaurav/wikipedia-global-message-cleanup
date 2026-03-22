import pytest
from wikipedia_global_message_cleanup.analyzer import ContributionAnalyzer


class TestContributionAnalyzer:
    def test_no_thresholds(self):
        analyzer = ContributionAnalyzer()
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        assert result == "none"

    def test_active_user(self):
        analyzer = ContributionAnalyzer(active_from=2020, inactive_from=2015)
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        assert result == "active"

    def test_inactive_user(self):
        analyzer = ContributionAnalyzer(active_from=2020, inactive_from=2015)
        result = analyzer.analyze_contribution("2018-01-01T12:00:00Z")
        assert result == "inactive"

    def test_delete_user(self):
        analyzer = ContributionAnalyzer(active_from=2020, inactive_from=2015)
        result = analyzer.analyze_contribution("2010-01-01T12:00:00Z")
        assert result == "delete"

    def test_empty_timestamp(self):
        analyzer = ContributionAnalyzer(active_from=2020, inactive_from=2015)
        result = analyzer.analyze_contribution("")
        assert result == "none"

    def test_active_from_equal_to_inactive_from_raises(self):
        with pytest.raises(ValueError, match="active_from"):
            ContributionAnalyzer(active_from=2020, inactive_from=2020)

    def test_active_from_less_than_inactive_from_raises(self):
        with pytest.raises(ValueError, match="active_from"):
            ContributionAnalyzer(active_from=2015, inactive_from=2020)
