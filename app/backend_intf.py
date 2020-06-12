"""
Main driver for backend functionality (parsing & seating).
"""
import math

from .lib.io import parse_seating_file, parse_family_file, get_section_row_str, transform_output, format_seat_assignments, write_seat_assignments_csv
from .lib.algo import expand_counts, get_pews
from .utils import trim_families
from .lib.io.Family import get_family_sizes 

# Main driver constants
INCHES_PER_FT = 12


def main_driver( site_info, output_file ):
    """
    Parses input, gets optimal seating arrangement, and writes to output_file
    """
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
    family_info_list = parse_family_file( family_file, family_filename )

    # Trim the number of families to capacity
    max_cap = max_cap - num_reserved
    seatable_families, unseatable_families = trim_families( family_info_list, max_cap )

    # Get optimal pew seating groups (per pew)
    family_sizes = get_family_sizes( seatable_families )
    matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes, margin )

    # TODO handle unmatched pews
    print( 'Unmatched pews: ', unmatched_pews )

    # Assign seating to specific families
    assigned_seating = transform_output( matched_pews, families_left, seatable_families )
    formatted_rows = format_seat_assignments( assigned_seating, seatable_families, pew_ids, pew_sizes, margin )

    # Append the unseated families to the end, no seat assignments
    unseated_families = [("N", f.fname, f.lname, f.size, f.email) 
                        for f in unseatable_families ]

    formatted_rows += unseated_families

    # Write out the output
    write_seat_assignments_csv( output_file, formatted_rows )

