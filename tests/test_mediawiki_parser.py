import pytest
from lib.parsers import MediaWikiParser


class TestMediaWikiParser:
    @pytest.fixture
    def mediawiki_parser(self):
        return MediaWikiParser()

    def test_parse_target_with_site(self, mediawiki_parser):
        line = "* {{target | user = TestUser | site = en.wikipedia.org}}"
        results = list(mediawiki_parser.parse_line(line))
        assert len(results) == 1
        assert results[0].username == "TestUser"
        assert results[0].site == "en.wikipedia.org"

    def test_parse_target_without_site(self, mediawiki_parser):
        line = "* {{target | user = TestUser}}"
        results = list(mediawiki_parser.parse_line(line))
        assert len(results) == 1
        assert results[0].username == "TestUser"
        assert results[0].site is None

    def test_parse_multiple_targets(self, mediawiki_parser):
        line = "* {{target | user = User1 | site = en.wikipedia.org}} {{target | user = User2}}"
        results = list(mediawiki_parser.parse_line(line))
        assert len(results) == 2
        assert results[0].username == "User1"
        assert results[1].username == "User2"

    def test_parse_no_targets(self, mediawiki_parser):
        line = "This is just regular text"
        results = list(mediawiki_parser.parse_line(line))
        assert len(results) == 0
