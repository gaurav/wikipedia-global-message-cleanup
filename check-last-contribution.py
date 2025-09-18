import re
import sys
import time
from dataclasses import dataclass

import requests
import csv
import click
import logging

# Configuration
MAX_RETRIES = 5
SLEEP_BETWEEN_REQUESTS = 1.5  # seconds between successful requests
BACKOFF_FACTOR = 2  # exponential backoff multiplier

# Use Python logging to do logging.
logging.basicConfig(level=logging.INFO)

# Wikimedia GlobalMessage lists track usernames along with the site that username is from.
@dataclass(frozen=True)
class UsernameWithSite:
    username: str
    site: str = None


def parse_line(line):
    """Extract username and site from lines like {{target | user = Username | site = en.wikipedia.org}}"""

    # TODO: support {{target | site = ... | user = ...}}

    targets = re.findall(r"{{\s*target\s*\|\s*user\s*=\s*(.+?)\s*(?:\|\s*site\s*=\s*(.+?)\s*)?\s*}}", line)
    for target in targets:
        username = target[0].strip()
        site = target[1]
        if site:
            yield UsernameWithSite(username, site)
        else:
            yield UsernameWithSite(username)


def get_last_edit(username, site):
    """Get the last edit timestamp for a username from the given site using MediaWiki API with retries."""
    api_url = f"https://{site}/w/api.php"
    params = {
        "action": "query",
        "list": "usercontribs",
        "ucuser": username,
        "uclimit": 1,
        "ucprop": "timestamp",
        "format": "json",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(api_url, params=params, timeout=10, headers={
                'User-Agent': 'check-last-contribution.py (gaurav@ggvaidya.com)'
            })
            resp.raise_for_status()
            data = resp.json()
            contribs = data.get("query", {}).get("usercontribs", [])
            if contribs:
                return contribs[0]["timestamp"]
            return ""  # no contributions
        except Exception as e:
            if attempt == MAX_RETRIES:
                print(f"Failed to get data for {username}@{site} after {MAX_RETRIES} attempts: {e}")
                return ""
            sleep_time = BACKOFF_FACTOR ** (attempt - 1)
            print(f"Request failed for {username}@{site} ({resp}), retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    return ""


@click.command()
@click.option("--input-type",
              default="mediawiki",
              type=click.Choice(["mediawiki"], case_sensitive=False),
              help="The type of input file to read usernames from.")
@click.argument("input_file", type=click.File("r"), nargs=-1)
@click.option("--output", "-o", type=click.File("w"), default=sys.stdout)
def main(input_type, input_file, output):
    usernames = []
    usernames_processed = set()

    for file in input_file:
        line_count = 0
        username_count = 0
        for line in file:
            line_count += 1

            # Convert every line into a list of usernames.
            match input_type:
                case "mediawiki":
                    line_usernames = parse_line(line)
                    for username in line_usernames:
                        if username not in usernames_processed:
                            usernames.append(username)
                case _:
                    raise NotImplementedError(f"Input type {input_type} is not implemented")

        logging.info(f"Read {line_count} lines containing {username_count} unique usernames from {file.name}.")

    site_list = set(map(lambda username: username.site, usernames))
    logging.info(f"Found {len(usernames)} unique usernames across {len(site_list)} sites: sites={site_list}.")

    # TODO: add support for multiple sites.

    writer = csv.writer(output, delimiter="\t")
    writer.writerow(["username", "site", "last_contribution_in_utc"])

    results_count = 0
    for username in usernames:
        last_edit = get_last_edit(username.username, username.site)
        logging.info(f"Last edit for {username.username}@{username.site} found as {last_edit}.")
        writer.writerow([username.username, username.site, last_edit])
        results_count += 1
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    logging.info(f"Done. {results_count} results written to {output.name}.")


if __name__ == "__main__":
    main()
