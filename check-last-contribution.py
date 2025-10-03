import sys
import click
import logging
from lib.api_client import WikimediaAPIClient
from lib.analyzer import ContributionAnalyzer
from lib.output_writer import TSVWriter
from lib.processor import UserProcessor

# Configuration
USER_AGENT = 'check-last-contribution.py (gaurav@ggvaidya.com)'
MAX_RETRIES = 5
SLEEP_BETWEEN_LINES = 1.5
BACKOFF_FACTOR = 2

logging.basicConfig(level=logging.INFO)

@click.command()
@click.option("--input-type", default="mediawiki", type=click.Choice(["mediawiki"]))
@click.argument("input_file", type=click.File("r"), nargs=-1)
@click.option("--output", "-o", type=click.File("w"), default=sys.stdout)
@click.option('--additional-site', '-s', multiple=True)
@click.option('--threshold-active', type=int)
@click.option('--threshold-inactive', type=int)
def main(input_type, input_file, output, additional_site, threshold_active, threshold_inactive):
    if input_type != "mediawiki":
        raise NotImplementedError(f"Input type {input_type} is not implemented")
    
    api_client = WikimediaAPIClient(USER_AGENT, MAX_RETRIES, BACKOFF_FACTOR)
    analyzer = ContributionAnalyzer(threshold_active, threshold_inactive)
    output_writer = TSVWriter(output)
    processor = UserProcessor(api_client, analyzer, SLEEP_BETWEEN_LINES)
    
    processor.process_files(list(input_file), output_writer, list(additional_site), output.name)

if __name__ == "__main__":
    main()