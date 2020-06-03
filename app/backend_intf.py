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
    pew_file, pew_filename = site_info['pewFile']
    family_file, family_filename = site_info['familyFile']

    # Calculate margin and total reserved seating available
    margin = int( math.ceil( (sep_rad * INCHES_PER_FT) / seat_width ) )

    # Parse input files
    pew_ids, pew_sizes = parse_seating_file( pew_file, pew_filename )
    family_names, family_sizes, family_emails = parse_family_file( family_file, family_filename )

    # Trim the number of families to capacity
    max_cap = max_cap - num_reserved

    curr_family_size = 0
    unseated_families = []
    last_family_seated_idx = 0

    # Stop at the one just before it goes past capacity
    for i, size in enumerate( family_sizes ):
        if curr_family_size <= max_cap:
            curr_family_size += size
        else:
            last_family_seated_idx = i - 1
            break

    # Record unseated families, starting at the last family that can
    # potentially be seated
    unseated_families = [("N", family_names[i].split(",")[0],
                        family_names[i].split(",")[1], family_sizes[i], 
                        family_emails[i]) 
                        for i in range( last_family_seated_idx + 1, len( family_sizes ) )]

    family_names = family_names[:last_family_seated_idx + 1]
    family_sizes = family_sizes[:last_family_seated_idx + 1]
    family_emails = family_emails[:last_family_seated_idx + 1]

    # Get optimal pew seating groups (per pew)
    matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes, margin )

    # Convert each row idx to section/row
    for pew_id, pew_family_sizes in matched_pews:
        pew_str = get_section_row_str( pew_id, pew_ids )

    # Assign seating to specific families
    assigned_seating = transform_output( matched_pews, family_names, family_sizes )
    formatted_rows = format_seat_assignments( assigned_seating, family_names, family_sizes, family_emails, pew_ids, pew_sizes, margin )

    # Append the unseated families to the end, no seat assignments
    formatted_rows += unseated_families

    # Write out the output
    write_seat_assignments_csv( output_file, formatted_rows )

