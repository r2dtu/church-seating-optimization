"""
Church seating optimization program.
"""

# Imports
import numpy as np
import collections

# Family input file constants
FAMILY_CSV_FILENAME = 'sample_family_input.csv'
FAMILY_NAME_IDX = 0
FAMILY_SIZE_IDX = 1
FAMILY_EMAIL_IDX = 2

# Pew seating info file constaints
PEW_CSV_FILENAME = 'covid19_newman_pew_seating.csv'
SECTION_COL_IDX = 0
ROW_NUM_IDX = 1
CAPACITY_IDX = 2

# User-defined Constraints
MARGIN = 4 # Amount of separation space measured in people (each person takes 18")

# Output constants
OUTPUT_FILE = 'newman_seating_arrangements.csv'


##########################################
####     Input parsing functions      ####
##########################################
def parse_reservations( household_reservation_filename ):
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

    # Parse the seating chart file
    with open( household_reservation_filename, 'r' ) as family_file:
        for line in family_file.readlines():
            row = line.split( "," )
            family_names.append( row[FAMILY_NAME_IDX] )
            family_sizes.append( row[FAMILY_SIZE_IDX] )
            family_emails.append( row[FAMILY_EMAIL_IDX] )

    # Discard the first row of column labels
    family_names.pop( 0 )
    family_sizes.pop( 0 )
    family_emails.pop( 0 )

    return family_names, np.array( family_sizes ).astype(int), family_emails


def parse_seating_file( seating_filename ):
    """
    Reads the CSV file containing pew information. The file must be a CSV file,
    and have the following three columns: Section, Row #, Capacity.

    Returns a 2D NumPy Array, each row is [Section, Row #, Capacity]
    """
    pews = []
    # Parse the seating chart file
    with open( seating_filename, 'r' ) as seating_file:
        for line in seating_file.readlines():
            row = line.split( "," )
            pews.append( [row[SECTION_COL_IDX], row[ROW_NUM_IDX], row[CAPACITY_IDX]] )

    # Discard the first row of column labels
    pews.pop( 0 )

    return np.array( pews )


def get_pew_ids( pew_info ):
    """
    Returns the section and row IDs
    """
    return pew_info[:, SECTION_COL_IDX], pew_info[:, ROW_NUM_IDX]


def get_pew_sizes( pew_info ):
    """
    Returns a list of the pew sizes from the pew info matrix.
    """
    return pew_info[:, CAPACITY_IDX].astype(int)


##########################################
####       Subset sum algorithm       ####
##########################################
def subset_sum(numbers, target, mode='=='):
    """
    Finds a subset of the numbers which sum to the target.
    """
    N = len(numbers)
    F = sum(numbers)

    Q = np.full((N, F + 1), False) # Query Array
    B = np.full((N, F + 1), None) # Backpointer Array

    # Loop across the first row of the arrays. This handles the case of when
    # the first index of the numbers happens to equal the target sum.
    for s in range(0, F + 1):
        if numbers[0] == s:
            Q[0, s] = True
            B[0, s] = ('stop', (0, s))

    # Recursive step: loop across each row of the array and use the previous row
    # to deduce whether a subset sum exists.
    for i in range(1, N):
        for s in range(0, F + 1):
            Q[i, s] = True
            if Q[i - 1, s]:
                # If the previous row could achieve this sum, then my row can
                # achieve the sum. Set the backpointer so that we should just
                # skip this element by "follow"ing the pointer.
                B[i, s] = ('follow', (i - 1, s))
            elif numbers[i] == s:
                # If the number at index i happens to equal the sum, then we
                # can achieve the sum alone. We should "stop" following
                # backpointers and append this index to the subset.
                B[i, s] = ('stop', (i, s))
            elif 0 <= s - numbers[i] < F + 1 and Q[i - 1, s - numbers[i]]:
                # If we subtract the number at index i from the desired sum, and
                # a previous prefix can achieve that partial sum, then a subset
                # is possible. We want to "add" this number to the subset when
                # following backpointers.
                B[i, s] = ('add', (i - 1, s - numbers[i]))
            else:
                Q[i, s] = False


    # Initialize the backpointers based on what mode we are using.
    if mode == '==':
        # Handle impossible case where the target is larger than the sum of all
        # families, or if the sum is just not possible.
        if not (0 <= target < F + 1 and Q[N - 1, target]):
            return None
        i, s = N - 1, target
    elif mode == '<=':
        # Check for sums that are less than or equal to the target in the bottom row.
        if target < 0:
            return None

        valid_sums = np.where(B[N - 1, :target + 1] != None)[0]
        if len(valid_sums) == 0:
            return None

        i, s = N - 1, valid_sums[-1]

    # Follow backpointers, using rules to decide when to append to subset
    # or just to follow.
    subset = []
    while True:
        rule, (pi, ps) = B[i, s]
        if rule == 'stop':
            subset.append(numbers[i])
            break
        elif rule == 'follow':
            i, s = pi, ps
        elif rule == 'add':
            subset.append(numbers[i])
            i, s = pi, ps

    return subset

##########################################
####         Seating functions        ####
##########################################
def expand_counts(counts):
    """
    Helper function to convert family size to an array with a length equal to
    the number of seats they take up.
    """
    expanded = []
    for size, count in counts.items():
        expanded.extend([size] * count)
    return np.array(expanded)


def get_pews(families, pews):
    """
    Returns the optimal seating group sizes for each pew, as well as any
    family sizes that aren't able to be seated (must go into overflow)
    """
    family_counts = collections.Counter(families)

    perfect_pews = []
    unmatched_pews = []
    for pew_idx, pew in enumerate(pews):
        pew += MARGIN # Extend pew artificially

        expanded = expand_counts(family_counts) + MARGIN # Add margin to each family size

        if len(expanded) == 0:
            break # No more families to find a subset of!

        subset = subset_sum(expanded, pew, mode='<=')

        if not subset:
            unmatched_pews.append(pew_idx)
            continue

        subset = np.array(subset) - MARGIN # Revert to original family sizes

        for fam in subset:
            family_counts[fam] -= 1

        perfect_pews.append((pew_idx, list(subset)))

    return (perfect_pews, unmatched_pews, family_counts)


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
    Converts all the array index row IDs to real section and row #s.

    Parameters:
        assigned_seating - a list of tuples containing pew and family assignment
        pew_ids - tuple containing ordered lists of pew sections and row numbers
    """
    sections = pew_ids[0]
    rows = pew_ids[1]
    return sections[arr_idx], rows[arr_idx]


def format_seat_assignments( assigned_seating, family_names, family_emails, pew_ids, pew_sizes ):
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
            name = family[0]
            size = family[1]

            # Get the family's info to print
            idx = family_names.index( family[0] )

            row = ("N", name, family_emails[idx])
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
                next_open_seat += MARGIN

    return rows

"""
MAIN PROGRAM DRIVER.
"""
if __name__ == '__main__':

    # Parse inputs
    seating_file_cts = parse_seating_file( PEW_CSV_FILENAME )
    family_names, family_sizes, family_emails = parse_reservations( FAMILY_CSV_FILENAME )

    # Extract pew specific info
    pew_ids = get_pew_ids( seating_file_cts )
    pew_sizes = get_pew_sizes( seating_file_cts )

    # Optimize every pew
    matched_pews, unmatched_pews, families_left = get_pews( family_sizes, pew_sizes )

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
    with open( OUTPUT_FILE, 'w' ) as out:
        csv_out = csv.writer( out )
        csv_out.writerow( ("Check-in", "Family Name", "E-mail", "Section", "Row", "Seat #s") )
        csv_out.writerows( formatted_rows )
