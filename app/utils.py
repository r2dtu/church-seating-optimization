"""
Driver helper functions.
"""
from .lib.io.Family import get_family_sizes


def trim_families( family_info_list, max_cap ):
    """
    Separates the list of families into seatable and non-seatable, and returns
    both as a tuple (seatable, non-seatable).
    """
    curr_family_size = 0

    # If curr_family_size never reaches max_cap, then we can seat all families
    last_family_seated_idx = len( family_info_list ) - 1

    # Stop at the one just before it goes past capacity
    family_sizes = get_family_sizes( family_info_list )
    for i, size in enumerate( family_sizes ):
        if curr_family_size <= max_cap:
            curr_family_size += size
        else:
            last_family_seated_idx = i - 1
            break

    return family_info_list[:last_family_seated_idx + 1], family_info_list[last_family_seated_idx + 1:]

