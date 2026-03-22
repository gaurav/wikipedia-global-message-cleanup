import sys
import click
import logging
from .api_client import WikimediaAPIClient
from .analyzer import ContributionAnalyzer
from .output_writer import TSVWriter
from .processor import UserProcessor

# Configuration
USER_AGENT = "check-last-contribution (https://github.com/gaurav/wikipedia-global-message-cleanup)"
MAX_RETRIES = 5
BACKOFF_FACTOR = 2

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("input_file", type=click.File("r"), nargs=-1)
@click.option(
    "--input-type",
    default="mediawiki",
    type=click.Choice(["mediawiki"]),
    help="Format of the input data. Currently only 'mediawiki' is supported; other formats may be added in the future.",
)
@click.option(
    "--output",
    "-o",
    type=click.File("w"),
    default=sys.stdout,
    help="Output file to write processed results in TSV format. Defaults to sys.stdout.",
)
@click.option(
    "--additional-site",
    "-s",
    multiple=True,
    help='Additional sites to check, e.g. "wikidata.org"',
)
@click.option(
    "--active-from",
    type=int,
    help=(
        "Minimum year of last edit to be classified as active "
        "(last_edit_year >= YEAR → active)."
    ),
)
@click.option(
    "--inactive-from",
    type=int,
    help=(
        "Minimum year of last edit to be classified as inactive "
        "(YEAR <= last_edit_year < --active-from → inactive; "
        "last_edit_year < YEAR → delete)."
    ),
)
@click.option(
    "--allow-duplicates",
    is_flag=True,
    default=False,
    help=(
        "Re-process duplicate (username, site) pairs instead of skipping them. "
        "By default, duplicates produce a row with username and site populated, "
        "last_edit_utc and last_edit_date empty, and threshold_result set to 'duplicate'."
    ),
)
@click.option(
    "--delay",
    type=float,
    default=1.5,
    show_default=True,
    help="Seconds to wait between Wikimedia API calls (courtesy rate-limiting).",
)
def main(
    input_type,
    input_file,
    output,
    additional_site,
    active_from,
    inactive_from,
    allow_duplicates,
    delay,
):
    """
    This command-line utility processes user data from given INPUT_FILEs by looking for
    {{target}} templates in their content, which are used by MassMessage to find lists of
    users to send messages to. These are written out in TSV format, along with the last date on
    which the user contributed to the given site. If additional sites are specified, each user
    will be checked against them as well.

    If --active-from and --inactive-from are supplied, users are classified as:
      active   — last edit year >= --active-from
      inactive — --inactive-from <= last edit year < --active-from
      delete   — last edit year < --inactive-from
    (--active-from must be strictly greater than --inactive-from; an error is raised otherwise)

    When deduplication is active (the default), each (username, site) pair is
    looked up only once. Subsequent occurrences produce a row with line_no, line,
    username, and site populated, last_edit_utc and last_edit_date left empty, and
    threshold_result set to "duplicate". Use --allow-duplicates to re-query every
    occurrence instead.
    """
    api_client = WikimediaAPIClient(USER_AGENT, MAX_RETRIES, BACKOFF_FACTOR)
    analyzer = ContributionAnalyzer(active_from, inactive_from)
    output_writer = TSVWriter(output)
    processor = UserProcessor(api_client, analyzer, delay, deduplicate=not allow_duplicates)

    processor.process_files(
        list(input_file), output_writer, list(additional_site), output.name
    )


if __name__ == "__main__":
    main()
