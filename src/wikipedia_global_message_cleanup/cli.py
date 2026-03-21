import sys
import click
import logging
from .api_client import WikimediaAPIClient
from .analyzer import ContributionAnalyzer
from .output_writer import TSVWriter
from .processor import UserProcessor

# Configuration
USER_AGENT = "check-last-contribution.py (https://github.com/gaurav/wikipedia-global-message-cleanup)"
MAX_RETRIES = 5
SLEEP_BETWEEN_LINES = 1.5
BACKOFF_FACTOR = 2

logging.basicConfig(level=logging.INFO)


@click.command()
@click.argument("input_file", type=click.File("r"), nargs=-1)
@click.option(
    "--input-type",
    default="mediawiki",
    type=click.Choice(["mediawiki"]),
    help="Type of the input data. The only current supported type is 'mediawiki'.",
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
    "--threshold-active",
    type=int,
    help="Last edits after the active threshold year will be marked as active.",
)
@click.option(
    "--threshold-inactive",
    type=int,
    help="Last edits after the inactive threshold year but before the active threshold year will be marked as inactive.",
)
def main(
    input_type,
    input_file,
    output,
    additional_site,
    threshold_active,
    threshold_inactive,
):
    """
    This command-line utility processes user data from given INPUT_FILEs by looking for
    {{target}} templates in their content, which are used by MassMessage lists to find lists of
    users to send messages to. These are written out in TSV format, along with the last date on
    which the user contributed to the given site. If additional sites are specified, each user
    will be checked against them as well.

    Additionally, an active and inactive threshold year may be specified. Users who last contributed in the active
    threshold year or later will be marked as active, and users who last contributed in the inactive threshold year
    or later but not within the active period will be marked as inactive. Other users will be given a status of `none`.
    """
    api_client = WikimediaAPIClient(USER_AGENT, MAX_RETRIES, BACKOFF_FACTOR)
    analyzer = ContributionAnalyzer(threshold_active, threshold_inactive)
    output_writer = TSVWriter(output)
    processor = UserProcessor(api_client, analyzer, SLEEP_BETWEEN_LINES)

    processor.process_files(
        list(input_file), output_writer, list(additional_site), output.name
    )


if __name__ == "__main__":
    main()
