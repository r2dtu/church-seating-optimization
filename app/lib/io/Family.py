"""
Classes relating to the family reservation file.
"""
from enum import IntEnum
import numpy as np

# Family input file constants
class FamilyFile(IntEnum):
    FAMILY_FNAME_IDX = 0
    FAMILY_LNAME_IDX = 1
    FAMILY_SIZE_IDX = 2
    FAMILY_EMAIL_IDX = 3

class FamilyInfo():

    def __init__(self, first_name, last_name, size, email):
        self.fname = first_name
        self.lname = last_name
        self.size = size
        self.email = email


def get_family_names( family_info_list ):
    return list( f.fname + "," + f.lname for f in family_info_list )


def get_family_sizes( family_info_list ):
    return np.array( [ f.size for f in family_info_list ] ).astype( int )


def get_family_emails( family_info_list ):
    return list( f.email for f in family_info_list )

