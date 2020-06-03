import numpy as np
import csv
from http import HTTPStatus
from werkzeug.exceptions import BadRequest
from enum import IntEnum
import re

from ...error_handlers import InvalidUsage

# Family input file constants
class FamilyFile(IntEnum):
    FAMILY_FNAME_IDX = 0
    FAMILY_LNAME_IDX = 1
    FAMILY_SIZE_IDX = 2
    FAMILY_EMAIL_IDX = 3

# Pew seating file constants
class PewFile(IntEnum):
    SECTION_COL_IDX = 0
    ROW_NUM_IDX = 1
    CAPACITY_IDX = 2


##########################################
####     Error Message functions      ####
##########################################
class ErrorObj():

    def __init__(self, description, filename, row_num, col_num, line_text):
        self.description = description
        self.file = filename
        self.row = row_num
        self.col = col_num
        self.text = line_text
        self._dict = dict()

    def to_dict(self):
        loc = vars(self)
        errors = dict([(i, loc[i]) for i in ('description', 'file', 'row', 'col', 'text')])
        self._dict['errors'] = [ errors ]
        return self._dict


##########################################
####     Input parsing functions      ####
##########################################
def parse_family_file( family_file, filename=None ):
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
        # +1 for 1-indexed, and +1 since we skipped the header
        row_num = i + 2

        try:
            line = line.strip()
            row = line.split( "," )

            if len(row) < len(FamilyFile):
                err_obj = ErrorObj( "Expected 4 columns, but only found " + str( len(row) ) + " columns in this row. "\
                                    "Please fix it and try submitting again.",
                                    filename or "Household Reservations File",
                                    row_num,
                                    -1,
                                    line )
                raise InvalidUsage( err_obj.to_dict() )

            family_names.append( row[FamilyFile.FAMILY_FNAME_IDX] + "," + row[FamilyFile.FAMILY_LNAME_IDX] )
            family_sizes.append( int( row[FamilyFile.FAMILY_SIZE_IDX] ) )
            family_emails.append( row[FamilyFile.FAMILY_EMAIL_IDX] )

        except ValueError:
            err_obj = ErrorObj( "This cell contains a non-numerical family size value. "\
                                "Please fix it and try submitting again.",
                                filename or "Household Reservations File",
                                row_num,
                                FamilyFile.FAMILY_SIZE_IDX + 1,
                                line )
            raise InvalidUsage( err_obj.to_dict() )

        EMAIL_REGEX = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
        if not re.search( EMAIL_REGEX, row[FamilyFile.FAMILY_EMAIL_IDX] ):
            err_obj = ErrorObj( "This cell contains an invalid e-mail address. "\
                                "Please fix it and try submitting again.",
                                filename or "Household Reservations File",
                                row_num,
                                FamilyFile.FAMILY_EMAIL_IDX + 1,
                                line )
            raise InvalidUsage( err_obj.to_dict() )

    return family_names, np.array( family_sizes ).astype(int), family_emails


def parse_seating_file( seating_file, filename=None ):
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
        line = line.strip()
        # +1 for 1-indexed, and +1 since we skipped the header
        row_num = i + 2

        try:
            row = line.split( "," )

            if len(row) < len(PewFile):
                err_obj = ErrorObj( "Expected 3 columns, but only found " + str( len(row) ) + " columns in this row. "\
                                    "Please fix it and try submitting again.",
                                    filename or "Pew Seating Info File",
                                    row_num,
                                    -1,
                                    line )
                raise InvalidUsage( err_obj.to_dict() )

            if len(row) > len(PewFile) and row[len(PewFile) + 1] == 'R':
                # Ignore the pew
            else:
                pews.append( [row[PewFile.SECTION_COL_IDX], row[PewFile.ROW_NUM_IDX], int( row[PewFile.CAPACITY_IDX] )] )

        except ValueError:
            err_obj = ErrorObj( "This cell is empty or contains a non-numerical pew capacity (size) value. "\
                                "Please fix it and try submitting again.",
                                filename or "Pew Seating Info File",
                                row_num,
                                PewFile.CAPACITY_IDX + 1,
                                line )
            raise InvalidUsage( err_obj.to_dict() )

    pews = np.array( pews )

    return __get_pew_ids(pews), __get_pew_sizes(pews)


def __get_pew_ids( pew_info ):
    """
    Returns the section and row IDs
    """
    return pew_info[:, PewFile.SECTION_COL_IDX], pew_info[:, PewFile.ROW_NUM_IDX]


def __get_pew_sizes( pew_info ):
    """
    Returns a list of the pew sizes from the pew info matrix.
    """
    return pew_info[:, PewFile.CAPACITY_IDX].astype(int)

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

