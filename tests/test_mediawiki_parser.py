import pytest
from wikipedia_global_message_cleanup.parsers import MediaWikiParser


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


class TestMediaWikiParserMalformed:
    @pytest.fixture
    def mediawiki_parser(self):
        return MediaWikiParser()

    def test_target_without_user_field(self, mediawiki_parser):
        results = list(mediawiki_parser.parse_line("{{target}}"))
        assert len(results) == 0

    def test_target_with_site_but_no_user(self, mediawiki_parser):
        results = list(mediawiki_parser.parse_line("{{target | site = en.wikipedia.org}}"))
        assert len(results) == 0

    def test_target_with_empty_user_value(self, mediawiki_parser):
        results = list(mediawiki_parser.parse_line("{{target | user = }}"))
        assert len(results) == 0

    def test_unclosed_target_template(self, mediawiki_parser):
        results = list(mediawiki_parser.parse_line("* {{target | user = Alice | site = en.wikipedia.org"))
        assert len(results) == 0

    def test_target_keyword_case_sensitive(self, mediawiki_parser):
        results = list(mediawiki_parser.parse_line("{{TARGET | user = Alice | site = en.wikipedia.org}}"))
        assert len(results) == 0
