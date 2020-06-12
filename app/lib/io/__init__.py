import numpy as np
import csv
import re
from enum import IntEnum

from ...error_handlers import InvalidUsage
from .Family import FamilyFile, FamilyInfo, get_family_names, get_family_sizes, get_family_emails

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
    families = []

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
                err_obj = ErrorObj( "Family file: Expected 4 columns, but only found " + str( len(row) ) + " columns in this row. "\
                                    "Please fix it and try submitting again.",
                                    filename or "Household Reservations File",
                                    row_num,
                                    -1,
                                    line )
                raise InvalidUsage( err_obj.to_dict() )

            families.append( FamilyInfo( row[FamilyFile.FAMILY_FNAME_IDX], 
                                        row[FamilyFile.FAMILY_LNAME_IDX],
                                        int( row[FamilyFile.FAMILY_SIZE_IDX] ), 
                                        row[FamilyFile.FAMILY_EMAIL_IDX] ) )

        except ValueError:
            err_obj = ErrorObj( "This cell contains a non-numerical family size value. "\
                                "Please fix it and try submitting again.",
                                filename or "Household Reservations File",
                                row_num,
                                FamilyFile.FAMILY_SIZE_IDX + 1,
                                line )
            raise InvalidUsage( err_obj.to_dict() )

        # Needs to be able to handle subdomains
        EMAIL_REGEX = '^([\w\.\-]+)@([\w\-]+)((\.(\w){2,63}){1,3})$'
        if not re.search( EMAIL_REGEX, row[FamilyFile.FAMILY_EMAIL_IDX] ):
            err_obj = ErrorObj( "This cell contains an invalid e-mail address. "\
                                "Please fix it and try submitting again.",
                                filename or "Household Reservations File",
                                row_num,
                                FamilyFile.FAMILY_EMAIL_IDX + 1,
                                line )
            raise InvalidUsage( err_obj.to_dict() )

    return families


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

            if len(row) != len(PewFile):
                err_obj = ErrorObj( "PewFile - Expected 3 columns, but found " + str( len(row) ) + " columns in this row. "\
                                    "Please fix it and try submitting again.",
                                    filename or "Pew Seating Info File",
                                    row_num,
                                    -1,
                                    line )
                raise InvalidUsage( err_obj.to_dict() )

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
def transform_output( optimal_pew_groups, families_left, seatable_family_info ):
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

        seatable_family_info - list of families

    Returns:
        List of tuples with pews and families that can sit there
    """
    family_names = get_family_names( seatable_family_info )
    family_sizes = get_family_sizes( seatable_family_info )

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

    # Append families that could not fit in pews
    for size in families_left:
        if families_left[size] > 0:
            result.append( (-1, [(family_name_size_map[size - 1].pop(0), size)] ) )

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


def format_seat_assignments( assigned_seating, family_info, pew_ids, pew_sizes, margin ):
    """
    Input looks like:
    [(row_idx, [('family1_name', family1_size), ...]), ...]
    """
    family_names = get_family_names( family_info )
    family_emails = get_family_emails( family_info )
    family_sizes = get_family_sizes( family_info )

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
            # TODO hacky fix for now, will find a better/faster solution
            idx = family_names.index( family[0] )
            if family_sizes[idx] != size:
                for i in range(idx, len(family_names)):
                    if family_sizes[i] == size and family_names[i] == family[0]:
                       idx = i
                       break

            # If it's an unseated family, there's only one of them in the row
            if row_idx == -1:
                rows.append( ("N", fname, lname, size, family_emails[idx] ) )
                continue

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

