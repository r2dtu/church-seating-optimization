"""
Church seating optimization program.
"""

import os

from lib.constants import PEW_CSV_FILENAME, FAMILY_CSV_FILENAME, MARGIN, OUTPUT_FILE
from lib.io import parse_seating_file, parse_family_file, get_section_row_str, transform_output, format_seat_assignments, write_seat_assignments_csv
from lib.algo import expand_counts, get_pews


file_paths = { filename: os.path.join('data', filename) for filename in [PEW_CSV_FILENAME, FAMILY_CSV_FILENAME, OUTPUT_FILE] }

"""
MAIN PROGRAM DRIVER.
"""
if __name__ == '__main__':

    # Parse inputs
    with open(file_paths[PEW_CSV_FILENAME]) as pew_file, open(file_paths[FAMILY_CSV_FILENAME]) as family_file:
        pew_ids, pew_sizes = parse_seating_file( pew_file )
        family_names, family_sizes, family_emails = parse_family_file( family_file )

        # Optimize every pew
        matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes, MARGIN )

        print( 'Matched: ', matched_pews )
        print( 'Unmatched: ', unmatched_pews )
        print( 'Families left: ', expand_counts( families_left ) )
        print( 'Families seated: ', len(family_sizes) - len(expand_counts( families_left )) )

        for pew_id, pew_family_sizes in matched_pews:
            pew_str = get_section_row_str( pew_id, pew_ids )
        
        assigned_seating = transform_output( matched_pews, family_names, family_sizes )
        formatted_rows = format_seat_assignments( assigned_seating, family_names, family_emails, pew_ids, pew_sizes, MARGIN )

        # Write out the output
        with open( file_paths[OUTPUT_FILE], 'w' ) as out:
            write_seat_assignments_csv(out, formatted_rows)
