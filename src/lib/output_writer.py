import csv
from typing import TextIO, Dict, Any

class TSVWriter:
    '''Writes output in TSV format with predefined columns.'''
    
    def __init__(self, output_file: TextIO):
        self.fieldnames = [
            "line_no", "line", "username", "site", 
            "last_edit_utc", "last_edit_date", "threshold_result"
        ]
        self.writer = csv.DictWriter(output_file, delimiter="\t", fieldnames=self.fieldnames)
        self.writer.writeheader()
    
    def write_row(self, data: Dict[str, Any]):
        '''Write a single row to the TSV output.'''
        self.writer.writerow(data)