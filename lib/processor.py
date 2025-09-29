import time
import logging
from typing import Set, List, TextIO
from .models import UsernameWithSite
from .parsers import MediaWikiParser
from .api_client import WikimediaAPIClient
from .analyzer import ContributionAnalyzer
from .output_writer import TSVWriter

class UserProcessor:
    '''Coordinates the processing pipeline for user contribution analysis.'''
    
    def __init__(self, api_client: WikimediaAPIClient, analyzer: ContributionAnalyzer, 
                 sleep_between_lines: float = 1.5):
        self.api_client = api_client
        self.analyzer = analyzer
        self.parser = MediaWikiParser()
        self.sleep_between_lines = sleep_between_lines
        self.processed_users: Set[UsernameWithSite] = set()
    
    def process_files(self, input_files: List[TextIO], output_writer: TSVWriter, 
                     additional_sites: List[str] = None, output_name: str = "output"):
        '''Process all input files and generate output with user contribution data.'''
        total_lines = sum(len(f.readlines()) for f in input_files)
        for f in input_files:
            f.seek(0)
        
        line_count = 0
        for file in input_files:
            for line in file:
                line_count += 1
                self._process_line(line, line_count, total_lines, output_writer, additional_sites)
                time.sleep(self.sleep_between_lines)
        
        self._log_summary(line_count, output_name)
    
    def _process_line(self, line: str, line_count: int, total_lines: int, 
                     output_writer: TSVWriter, additional_sites: List[str]):
        '''Process a single line from input file, extracting and analyzing usernames.'''
        usernames = list(self.parser.parse_line(line))
        usernames_output = 0
        
        for username in usernames:
            if username in self.processed_users:
                continue
            
            # Build sites list: original site + additional sites
            sites = {username.site} if username.site else set()
            if additional_sites:
                sites.update(additional_sites)
            
            for site in sites:
                user_site = UsernameWithSite(username.username, site)
                if user_site in self.processed_users:
                    continue
                
                self.processed_users.add(user_site)
                last_edit = self.api_client.get_last_edit(username.username, site)
                last_edit_date = last_edit.split("T")[0] if last_edit else ""
                threshold_result = self.analyzer.analyze_contribution(last_edit)
                
                logging.info(f"Last edit for {username.username}@{site} found as {last_edit} (threshold: {threshold_result}) "
                           f"on line {line_count} out of {total_lines} ({line_count / total_lines * 100:.2f}%).")
                
                output_writer.write_row({
                    'line_no': line_count,
                    'line': line.rstrip('\n'),
                    'username': username.username,
                    'site': site,
                    'last_edit_utc': last_edit,
                    'last_edit_date': last_edit_date,
                    'threshold_result': threshold_result
                })
                usernames_output += 1
        
        if usernames_output == 0:
            output_writer.write_row({'line_no': line_count, 'line': line})
    
    def _log_summary(self, line_count: int, output_name: str):
        '''Log processing summary statistics.'''
        usernames = {u.username for u in self.processed_users}
        sites = {u.site for u in self.processed_users}
        logging.info(f"Done. {len(usernames)} unique usernames on {len(sites)} sites ({sites}) from {line_count} lines written to {output_name}.")