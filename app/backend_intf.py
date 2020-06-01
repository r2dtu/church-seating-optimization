import math

from .lib.io import parse_seating_file, parse_family_file, get_section_row_str, transform_output, format_seat_assignments, write_seat_assignments_csv
from .lib.algo import expand_counts, get_pews

# Main driver constants
INCHES_PER_FT = 12

def main_driver( site_info, output_file ):

    # Extract inputs
    max_cap = site_info['maxCapacity']
    num_reserved = site_info['numReservedSeating']
    sep_rad = site_info['sepRad'] # (in feet)
    seat_width = site_info['seatWidth'] # (in inches)

    # Calculate margin and total reserved seating available
    margin = int( math.ceil( (sep_rad * INCHES_PER_FT) / seat_width ) )

    with open( site_info['pewFile'] ) as pew_file, open( site_info['familyFile'] ) as family_file:
        # Parse input files
        pew_ids, pew_sizes = parse_seating_file( pew_file )
        family_names, family_sizes, family_emails = parse_family_file( family_file )

        # Get optimal pew seating groups (per pew)
        matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes, margin )

        # Convert each row idx to section/row
        for pew_id, pew_family_sizes in matched_pews:
            pew_str = get_section_row_str( pew_id, pew_ids )

        # Assign seating to specific families
        assigned_seating = transform_output( matched_pews, family_names, family_sizes )
        formatted_rows = format_seat_assignments( assigned_seating, family_names, family_emails, pew_ids, pew_sizes, margin )

        # Write out the output
        write_seat_assignments_csv( output_file, formatted_rows )

