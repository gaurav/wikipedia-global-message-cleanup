import time
import logging
from typing import Set, List, TextIO, Optional
from tqdm import tqdm
from tqdm.contrib.logging import logging_redirect_tqdm
from .models import UsernameWithSite
from .parsers import MediaWikiParser
from .api_client import WikimediaAPIClient
from .analyzer import ContributionAnalyzer
from .output_writer import TSVWriter


class UserProcessor:
    """Coordinates the processing pipeline for user contribution analysis."""

    def __init__(
        self,
        api_client: WikimediaAPIClient,
        analyzer: ContributionAnalyzer,
        sleep_between_lines: float = 1.5,
        deduplicate: bool = True,
    ):
        self.api_client = api_client
        self.analyzer = analyzer
        self.parser = MediaWikiParser()
        self.sleep_between_lines = sleep_between_lines
        self.deduplicate = deduplicate
        self.processed_users: Set[UsernameWithSite] = set()

    def process_files(
        self,
        input_files: List[TextIO],
        output_writer: TSVWriter,
        additional_sites: Optional[List[str]] = None,
        output_name: str = "output",
    ):
        """Process all input files and generate output with user contribution data."""
        total_lines = sum(sum(1 for _ in f) for f in input_files)
        for f in input_files:
            f.seek(0)

        line_count = 0
        start_time = time.monotonic()
        with logging_redirect_tqdm():
            with tqdm(total=total_lines, unit="line", desc="Processing") as pbar:
                for file in input_files:
                    for line in file:
                        line_count += 1
                        self._process_line(line, line_count, output_writer, additional_sites, pbar)
                        pbar.update(1)

        elapsed = time.monotonic() - start_time
        self._log_summary(line_count, output_name, elapsed)

    def _process_line(
        self,
        line: str,
        line_count: int,
        output_writer: TSVWriter,
        additional_sites: Optional[List[str]] = None,
        pbar: Optional[tqdm] = None,
    ):
        """Process a single line from input file, extracting and analyzing usernames."""
        stripped_line = line.rstrip("\n")
        usernames = list(self.parser.parse_line(line))
        usernames_output = 0

        for username in usernames:
            # Build sites list: original site + additional sites
            sites = {username.site} if username.site else set()
            if additional_sites:
                sites.update(additional_sites)

            for site in sites:
                user_site = UsernameWithSite(username.username, site)
                if self.deduplicate and user_site in self.processed_users:
                    output_writer.write_row(
                        {
                            "line_no": line_count,
                            "line": stripped_line,
                            "username": username.username,
                            "site": site,
                            "threshold_result": "duplicate",
                        }
                    )
                    usernames_output += 1
                    continue

                if pbar is not None:
                    pbar.set_postfix(user=f"{username.username}@{site}")
                self.processed_users.add(user_site)
                last_edit = self.api_client.get_last_edit(username.username, site)
                time.sleep(self.sleep_between_lines)
                last_edit_date = last_edit.split("T")[0] if last_edit else ""
                threshold_result = self.analyzer.analyze_contribution(last_edit)

                logging.info(
                    f"Last edit for {username.username}@{site} found as {last_edit} (threshold: {threshold_result})."
                )

                output_writer.write_row(
                    {
                        "line_no": line_count,
                        "line": stripped_line,
                        "username": username.username,
                        "site": site,
                        "last_edit_utc": last_edit,
                        "last_edit_date": last_edit_date,
                        "threshold_result": threshold_result,
                    }
                )
                usernames_output += 1

        if usernames_output == 0:
            output_writer.write_row({"line_no": line_count, "line": stripped_line})

    def _log_summary(self, line_count: int, output_name: str, elapsed: float = 0.0):
        """Log processing summary statistics."""
        usernames = {u.username for u in self.processed_users}
        sites = {u.site for u in self.processed_users}
        per_line = elapsed / line_count if line_count else 0.0
        per_user_site = elapsed / len(self.processed_users) if self.processed_users else 0.0
        logging.info(
            f"Done. {len(usernames)} unique usernames on {len(sites)} sites ({sites}) "
            f"from {line_count} lines written to {output_name}. "
            f"Elapsed: {elapsed:.1f}s ({per_line:.2f}s/line, {per_user_site:.2f}s/username-site)."
        )
