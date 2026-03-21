import csv
import io
from unittest.mock import MagicMock, patch

from wikipedia_global_message_cleanup.analyzer import ContributionAnalyzer
from wikipedia_global_message_cleanup.output_writer import TSVWriter
from wikipedia_global_message_cleanup.processor import UserProcessor


def _make_processor():
    api_client = MagicMock()
    analyzer = ContributionAnalyzer()
    return UserProcessor(api_client, analyzer), api_client


def _run(processor, lines, additional_sites=None):
    buf = io.StringIO()
    writer = TSVWriter(buf)
    input_file = io.StringIO("".join(lines))
    with patch("wikipedia_global_message_cleanup.processor.time.sleep"):
        processor.process_files([input_file], writer, additional_sites=additional_sites)
    buf.seek(0)
    return list(csv.DictReader(buf, delimiter="\t"))


class TestUserProcessor:
    def test_non_target_line_writes_fallback_row(self):
        processor, api_client = _make_processor()
        rows = _run(processor, ["Just a comment\n"])
        assert len(rows) == 1
        assert rows[0]["line_no"] == "1"
        assert rows[0]["line"] == "Just a comment"
        assert rows[0]["username"] == ""
        api_client.get_last_edit.assert_not_called()

    def test_target_line_writes_full_row(self):
        processor, api_client = _make_processor()
        api_client.get_last_edit.return_value = "2023-05-01T12:00:00Z"
        rows = _run(processor, ["* {{target | user = Alice | site = en.wikipedia.org}}\n"])
        assert len(rows) == 1
        assert rows[0]["username"] == "Alice"
        assert rows[0]["site"] == "en.wikipedia.org"
        assert rows[0]["last_edit_date"] == "2023-05-01"
        assert rows[0]["threshold_result"] == "none"

    def test_duplicate_user_skipped_second_occurrence_is_fallback(self):
        processor, api_client = _make_processor()
        api_client.get_last_edit.return_value = "2023-05-01T12:00:00Z"
        line = "* {{target | user = Alice | site = en.wikipedia.org}}\n"
        rows = _run(processor, [line, line])
        assert api_client.get_last_edit.call_count == 1
        assert len(rows) == 2
        assert rows[0]["username"] == "Alice"
        assert rows[1]["username"] == ""

    def test_additional_sites_writes_multiple_rows(self):
        processor, api_client = _make_processor()
        api_client.get_last_edit.return_value = "2023-05-01T12:00:00Z"
        rows = _run(
            processor,
            ["* {{target | user = Alice | site = en.wikipedia.org}}\n"],
            additional_sites=["commons.wikimedia.org"],
        )
        assert len(rows) == 2
        assert api_client.get_last_edit.call_count == 2
        sites = {r["site"] for r in rows}
        assert sites == {"en.wikipedia.org", "commons.wikimedia.org"}

    def test_additional_site_dedup_with_original_site(self):
        processor, api_client = _make_processor()
        api_client.get_last_edit.return_value = "2023-05-01T12:00:00Z"
        rows = _run(
            processor,
            ["* {{target | user = Alice | site = en.wikipedia.org}}\n"],
            additional_sites=["en.wikipedia.org"],
        )
        assert len(rows) == 1
        assert api_client.get_last_edit.call_count == 1
