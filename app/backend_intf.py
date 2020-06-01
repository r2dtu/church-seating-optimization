import math
import traceback
from http import HTTPStatus

from .lib.io import parse_seating_file, parse_family_file, get_section_row_str, transform_output, format_seat_assignments, write_seat_assignments_csv
from .lib.algo import expand_counts, get_pews

# Main driver constants
INCHES_PER_FT = 12

def create_json_err_msg( err, inputs, http_status ):
    json_msg = {}
    if http_status == HTTPStatus.BAD_REQUEST:
        # 400 error
        json_msg['error'] = {
            'input': err,
            'description': "One of your input CSV files contains this un-parseable line."\
                           "Please fix it and try submitting again.",
        }

    else:
        # 500 error
        json_msg['error'] = {
            'trace': err,
            'inputs': inputs,
            'description': "A fatal server error has occurred. Please relay the entirety"\
                           "of this message to a developer",
        }

    return json_msg


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

        try:
            # Trim the number of families to capacity
            max_cap = max_cap - num_reserved

            curr_family_size = 0
            unseated_families = []
            last_family_seated_idx = 0

            for i, size in enumerate( family_sizes ):
                if curr_family_size <= max_cap:
                    curr_family_size += size
                else:
                    last_family_seated_idx = i
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
            with open( output_file, 'w' ) as out:
                write_seat_assignments_csv( out, formatted_rows )

        except:
            tb = traceback.format_exc()
            json_msg = create_json_err_msg( tb, None, HTTPStatus.INTERNAL_SERVER_ERROR )
            return "", HTTPStatus.INTERNAL_SERVER_ERROR.value

