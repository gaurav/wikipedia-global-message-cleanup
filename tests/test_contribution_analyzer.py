from lib.analyzer import ContributionAnalyzer


class TestContributionAnalyzer:
    def test_no_thresholds(self):
        analyzer = ContributionAnalyzer()
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        assert result == "none"

    def test_active_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        assert result == "active"

    def test_inactive_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2018-01-01T12:00:00Z")
        assert result == "inactive"

    def test_delete_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2010-01-01T12:00:00Z")
        assert result == "delete"

    def test_empty_timestamp(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("")
        assert result == "none"
