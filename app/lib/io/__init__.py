import numpy as np
import csv
from http import HTTPStatus
from werkzeug.exceptions import BadRequest

from ...error_handlers import InvalidUsage, InternalError

# Family input file constants
FAMILY_FNAME_IDX = 0
FAMILY_LNAME_IDX = 1
FAMILY_SIZE_IDX = 2
FAMILY_EMAIL_IDX = 3

# Pew seating file constants
SECTION_COL_IDX = 0
ROW_NUM_IDX = 1
CAPACITY_IDX = 2

##########################################
####     Input parsing functions      ####
##########################################
def parse_family_file( family_file ):
    """
    Reads the CSV file containing family info. The file must be a CSV file,
    and have the following three columns: Family Name, Size of Family, E-mail

    Returns 3 (ordered) lists. Each index contains a piece of a households
    info, so it's important to keep them in this order when assigning to 
    populate the seating arrangement with the correct information.
    """
    family_names = []
    family_sizes = []
    family_emails = []

    # Discard the first row of column labels
    family_file.readline()

    # Parse the seating chart file
    for i, line in enumerate( family_file.readlines() ):
        try:
            row = line.split( "," )
            family_names.append( row[FAMILY_FNAME_IDX] + "," + row[FAMILY_LNAME_IDX] )
            family_sizes.append( int( row[FAMILY_SIZE_IDX] ) )
            family_emails.append( row[FAMILY_EMAIL_IDX] )

        except ValueError:
            message = "This line contains a non-parseable family size value. "\
                      "Please fix it and try submitting again."
            error = {
                'errors': [
                    {
                        'file': "Household Reservations",
                        'row': i + 1,
                        'col': FAMILY_SIZE_IDX + 1,
                        'text': line,
                    }
                ]
            }
            raise InvalidUsage( message, error )

        if '@' not in row[FAMILY_EMAIL_IDX]:
            message = "This line contains a non-parseable e-mail address. "\
                      "Please fix it and try submitting again."
            error = {
                'errors': [
                    {
                        'file': "Household Reservations",
                        'row': i + 1,
                        'col': FAMILY_EMAIL_IDX + 1,
                        'text': line,
                    }
                ]
            }
            raise InvalidUsage( message, error )

    return family_names, np.array( family_sizes ).astype(int), family_emails


def parse_seating_file( seating_file ):
    """
    Reads the CSV file containing pew information. The file must be a CSV file,
    and have the following three columns: Section, Row #, Capacity.

    Returns a tuple of parallel np.arrays of the pew's id and the pew's capacity, respectively.

        (pew_ids, capacities) = parse_seating_file(...)
    """
    pews = []

    # Discard the first row of column labels
    seating_file.readline()

    # Parse the seating chart file
    for i, line in enumerate( seating_file.readlines() ):
        try:
            row = line.split( "," )
            pews.append( [row[SECTION_COL_IDX], row[ROW_NUM_IDX], int( row[CAPACITY_IDX] )] )
        except ValueError:
            message = "This line contains a non-parseable pew capacity (size) value. "\
                      "Please fix it and try submitting again."
            error = {
                'errors': [
                    {
                        'file': "Pew Seating Info",
                        'row': i + 1,
                        'col': CAPACITY_IDX + 1,
                        'text': line,
                    }
                ]
            }
            raise InvalidUsage( message, error )

    pews = np.array( pews )

    return __get_pew_ids(pews), __get_pew_sizes(pews)


def __get_pew_ids( pew_info ):
    """
    Returns the section and row IDs
    """
    return pew_info[:, SECTION_COL_IDX], pew_info[:, ROW_NUM_IDX]


def __get_pew_sizes( pew_info ):
    """
    Returns a list of the pew sizes from the pew info matrix.
    """
    return pew_info[:, CAPACITY_IDX].astype(int)

##########################################
####         Output re-format         ####
##########################################
def transform_output( optimal_pew_groups, family_names, family_sizes ):
    """
    Transforms the optimal seating list into a printable list with family name
    assigned seating.

    Parameters:
        optimal_pew_groups will be formatted as a list of tuples, as follows:
        [ (pew_id, [family_size_1, family_size_2, ...]),
          ...
        ]

        Each tuple will have the pew ID and what family sizes can be seated there.
        The family size values to NOT include the +3 padding. Make sure to call this
        function after re-calculating the actual family sizes.

        family_names - list of family names
        family_sizes - corresponding list of size of families

    Returns:
        List of tuples with pews and families that can sit there
    """
    # Convert family and family sizes to an internal mapping.
    # Family names with size s will exist in a list at map[s - 1].
    family_name_size_map = [[] for _ in range( max( family_sizes ) )]
    for i, size in enumerate( family_sizes ):
        family_name_size_map[size - 1].append( family_names[i] )

    # Convert input into pew_id, list of family names tuple
    result = []
    for pew in optimal_pew_groups:
        # Convert the pew's group sizes to family names
        pew_family_names = []
        for size in pew[1]:
            pew_family_names.append( (family_name_size_map[size - 1].pop(0), size) )
        pew_assign = (pew[0], pew_family_names)

        result.append( pew_assign )

    return result


def get_section_row_str( arr_idx, pew_ids ):
    """
    Converts all the array index row IDs to real door, section and row #s.

    Parameters:
        assigned_seating - a list of tuples containing pew and family assignment
        pew_ids - tuple containing ordered lists of pew sections and row numbers
    """
    sections = pew_ids[0]
    rows = pew_ids[1]
    return sections[arr_idx], sections[arr_idx], rows[arr_idx]


def format_seat_assignments( assigned_seating, family_names, family_sizes, family_emails, pew_ids, pew_sizes, margin ):
    """
    Input looks like:
    [(row_idx, [('family1_name', family1_size), ...]), ...]
    """
    rows = []
    for pew in assigned_seating:
        next_open_seat = 0

        row_idx = pew[0]
        seating = pew[1]
        for family in seating:
            name = family[0].split(",")
            fname, lname = name[0], name[1]
            size = family[1]

            # Get the family's info to print
            idx = family_names.index( family[0] )

            row = ("N", fname, lname, family_sizes[idx], family_emails[idx])
            row += get_section_row_str( row_idx, pew_ids )

            curr_pew_size = pew_sizes[row_idx]
            seat_nos = []
            if next_open_seat < curr_pew_size:
                # Populate seat #s
                for i in range(size):
                    seat_nos.append( next_open_seat + 1 )
                    next_open_seat += 1

            row += (seat_nos,)
            rows.append( row )

            # If not the end of the pew, add padding
            if next_open_seat != curr_pew_size - 1:
                next_open_seat += margin

    return rows


def write_seat_assignments_csv( seat_assignments_file, formatted_rows ):
    """
    Writes out seat assignments to file.
      - seat_assignments_file: The file object to write the seat assignments to.
      - formatted_rows: A multi-dimensional list of rows to be written in a CSV format.
    """
    csv_out = csv.writer( seat_assignments_file )
    csv_out.writerow( ("Check-in", "First Name", "Last Name", "Size", "E-mail", "Door", "Section", "Row", "Seat #s") )
    csv_out.writerows( formatted_rows )

