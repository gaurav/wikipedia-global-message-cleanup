import unittest
from lib.models import UsernameWithSite
from lib.parsers import MediaWikiParser
from lib.analyzer import ContributionAnalyzer

class TestModels(unittest.TestCase):
    def test_username_with_site_creation(self):
        user = UsernameWithSite("TestUser", "en.wikipedia.org")
        self.assertEqual(user.username, "TestUser")
        self.assertEqual(user.site, "en.wikipedia.org")
    
    def test_username_without_site(self):
        user = UsernameWithSite("TestUser")
        self.assertEqual(user.username, "TestUser")
        self.assertIsNone(user.site)

class TestMediaWikiParser(unittest.TestCase):
    def setUp(self):
        self.parser = MediaWikiParser()
    
    def test_parse_target_with_site(self):
        line = "* {{target | user = TestUser | site = en.wikipedia.org}}"
        results = list(self.parser.parse_line(line))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, "TestUser")
        self.assertEqual(results[0].site, "en.wikipedia.org")
    
    def test_parse_target_without_site(self):
        line = "* {{target | user = TestUser}}"
        results = list(self.parser.parse_line(line))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].username, "TestUser")
        self.assertIsNone(results[0].site)
    
    def test_parse_multiple_targets(self):
        line = "* {{target | user = User1 | site = en.wikipedia.org}} {{target | user = User2}}"
        results = list(self.parser.parse_line(line))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].username, "User1")
        self.assertEqual(results[1].username, "User2")
    
    def test_parse_no_targets(self):
        line = "This is just regular text"
        results = list(self.parser.parse_line(line))
        self.assertEqual(len(results), 0)

class TestContributionAnalyzer(unittest.TestCase):
    def test_no_thresholds(self):
        analyzer = ContributionAnalyzer()
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        self.assertEqual(result, "none")
    
    def test_active_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2023-01-01T12:00:00Z")
        self.assertEqual(result, "active")
    
    def test_inactive_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2018-01-01T12:00:00Z")
        self.assertEqual(result, "inactive")
    
    def test_delete_user(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("2010-01-01T12:00:00Z")
        self.assertEqual(result, "delete")
    
    def test_empty_timestamp(self):
        analyzer = ContributionAnalyzer(threshold_active=2020, threshold_inactive=2015)
        result = analyzer.analyze_contribution("")
        self.assertEqual(result, "none")

if __name__ == "__main__":
    unittest.main()