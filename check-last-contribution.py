import re
import sys
import time
from collections import defaultdict
from dataclasses import dataclass

import requests
import csv
import click
import logging

# Configuration
USER_AGENT = 'check-last-contribution.py (gaurav@ggvaidya.com)'
MAX_RETRIES = 5
SLEEP_BETWEEN_LINES = 1.5  # seconds between successful requests
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
    """Get the last edit timestamp for a username from the given site using MediaWiki API with retries.

    Mostly written by ChatGPT.
    """
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
        resp = None
        try:
            resp = requests.get(api_url, params=params, timeout=10, headers={
                'User-Agent': USER_AGENT,
            })
            resp.raise_for_status()
            data = resp.json()
            contribs = data.get("query", {}).get("usercontribs", [])
            if contribs:
                return contribs[0]["timestamp"]
            return ""  # no contributions
        except Exception as e:
            if attempt == MAX_RETRIES:
                logging.error(f"Failed to get data for {username}@{site} after {MAX_RETRIES} attempts: {e}")
                return ""
            sleep_time = BACKOFF_FACTOR ** (attempt - 1)
            logging.info(f"Request failed for {username}@{site} ({resp}), retrying in {sleep_time} seconds...")
            time.sleep(sleep_time)
    return ""


@click.command()
@click.option("--input-type",
              default="mediawiki",
              type=click.Choice(["mediawiki"], case_sensitive=False),
              help="The type of input file to read usernames from.")
@click.argument("input_file", type=click.File("r"), nargs=-1)
@click.option("--output", "-o", type=click.File("w"), default=sys.stdout)
@click.option('--additional-site', '-s', multiple=True, help='Additional sites to check, e.g. "wikidata.org"')
def main(input_type, input_file, output, additional_site):
    usernames_processed = set()

    # Count the lines so we can track progress.
    total_lines = 0
    for file in input_file:
        total_lines += len(file.readlines())
        file.seek(0)

    # Write output.
    writer = csv.DictWriter(output, delimiter="\t", fieldnames=[
        "line_no", "line", "username", "site", "last_edit_utc", "last_edit_date"
    ])
    writer.writeheader()

    for file in input_file:
        line_count = 0
        for line in file:
            line_count += 1

            # Convert every line into a list of usernames.
            match input_type:
                case "mediawiki":
                    # TODO: should probably move this into its own function.
                    line_usernames = parse_line(line)
                    usernames_output_on_line = 0
                    for username in line_usernames:
                        if username in usernames_processed:
                            # Note that this means that a particular username/site combination won't be processed twice.
                            continue

                        # We may need to expand the list of sites we've processed for this username.
                        sites = {username.site}
                        if additional_site:
                            sites.update(additional_site)

                        # Go through all the sites, and keep adding them to usernames_processed as we go to avoid duplicates.
                        for site in sites:
                            username_to_process = UsernameWithSite(username.username, site)
                            if username_to_process in usernames_processed:
                                continue
                            usernames_processed.add(username_to_process)
                            last_edit = get_last_edit(username.username, site)
                            logging.info(f"Last edit for {username.username}@{site} found as {last_edit} " +
                                         f"on line {line_count} out of {total_lines} ({line_count / total_lines * 100:.2f}%).")
                            writer.writerow({
                                'line_no': line_count,
                                'line': line,
                                'username': username.username,
                                'site': site,
                                'last_edit_utc': last_edit,
                                'last_edit_date': last_edit.split("T")[0]
                            })
                            usernames_output_on_line += 1

                    # If we haven't written out anything, write out an empty line with just the line number and line.
                    if usernames_output_on_line == 0:
                        writer.writerow({
                            'line_count': line_count,
                            'line': line
                        })

                    # Sleep between lines.
                    time.sleep(SLEEP_BETWEEN_LINES)
                case _:
                    raise NotImplementedError(f"Input type {input_type} is not implemented")

    usernames = set(map(lambda uname: uname.username, usernames_processed))
    sites = set(map(lambda uname: uname.site, usernames_processed))
    logging.info(f"Done. {len(usernames)} unique usernames on {len(sites)} ({sites}) from {line_count} lines written to {output.name}.")


if __name__ == "__main__":
    main()
