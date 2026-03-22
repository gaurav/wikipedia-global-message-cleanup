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


class TestContributionAnalyzerSingleThreshold:
    def test_active_from_only_active(self):
        a = ContributionAnalyzer(active_from=2020)
        assert a.analyze_contribution("2023-01-01T00:00:00Z") == "active"

    def test_active_from_only_delete(self):
        a = ContributionAnalyzer(active_from=2020)
        assert a.analyze_contribution("2015-01-01T00:00:00Z") == "delete"

    def test_active_from_only_empty_timestamp(self):
        a = ContributionAnalyzer(active_from=2020)
        assert a.analyze_contribution("") == "none"

    def test_inactive_from_only_warns(self, caplog):
        import logging
        with caplog.at_level(logging.WARNING, logger="wikipedia_global_message_cleanup.analyzer"):
            ContributionAnalyzer(inactive_from=2015)
        assert "inactive-from" in caplog.text

    def test_inactive_from_only_inactive(self):
        a = ContributionAnalyzer(inactive_from=2015)
        assert a.analyze_contribution("2018-01-01T00:00:00Z") == "inactive"

    def test_inactive_from_only_delete(self):
        a = ContributionAnalyzer(inactive_from=2015)
        assert a.analyze_contribution("2010-01-01T00:00:00Z") == "delete"

    def test_inactive_from_only_empty_timestamp(self):
        a = ContributionAnalyzer(inactive_from=2015)
        assert a.analyze_contribution("") == "none"
