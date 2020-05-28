"""
Church seating optimization program.
"""

import os

from lib.constants import PEW_CSV_FILENAME, FAMILY_CSV_FILENAME, MARGIN, OUTPUT_FILE
from lib.io import parse_seating_file, parse_reservations, get_pew_sizes, get_pew_ids, get_section_row_str, transform_output, format_seat_assignments
from lib.algo import expand_counts, get_pews

"""
MAIN PROGRAM DRIVER.
"""
if __name__ == '__main__':

    # Parse inputs
    seating_file_cts = parse_seating_file( os.path.join('data', PEW_CSV_FILENAME) )
    family_names, family_sizes, family_emails = parse_reservations( os.path.join('data', FAMILY_CSV_FILENAME) )

    # Extract pew specific info
    pew_ids = get_pew_ids( seating_file_cts )
    pew_sizes = get_pew_sizes( seating_file_cts )

    # Optimize every pew
    matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes, MARGIN )

    print( 'Matched: ', matched_pews )
    print( 'Unmatched: ', unmatched_pews )
    print( 'Families left: ', expand_counts( families_left ) )
    print( 'Families seated: ', len(family_sizes) - len(expand_counts( families_left )) )

    for pew_id, pew_family_sizes in matched_pews:
        pew_str = get_section_row_str( pew_id, pew_ids )
    
    assigned_seating = transform_output( matched_pews, family_names, family_sizes )
    formatted_rows = format_seat_assignments( assigned_seating, family_names, family_emails, pew_ids, pew_sizes )

    # Write out the output
    import csv
    with open( os.path.join('data', OUTPUT_FILE), 'w' ) as out:
        csv_out = csv.writer( out )
        csv_out.writerow( ("Check-in", "Family Name", "E-mail", "Section", "Row", "Seat #s") )
        csv_out.writerows( formatted_rows )
