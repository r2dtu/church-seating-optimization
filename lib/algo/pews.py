import collections
import numpy as np

from .subset_sum import subset_sum

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


def get_pews(families, pews, margin):
    """
    Returns the optimal seating group sizes for each pew, as well as any
    family sizes that aren't able to be seated (must go into overflow)
    """
    family_counts = collections.Counter(families)

    matched_pews = []
    unmatched_pews = []
    for pew_idx, pew in enumerate(pews):
        pew += margin # Extend pew artificially

        expanded = expand_counts(family_counts) + margin # Add margin to each family size

        if len(expanded) == 0:
            break # No more families to find a subset of!

        subset = subset_sum(expanded, pew, mode='<=')

        if not subset:
            unmatched_pews.append(pew_idx)
            continue

        subset = np.array(subset) - margin # Revert to original family sizes

        for fam in subset:
            family_counts[fam] -= 1

        matched_pews.append((pew_idx, list(subset)))

    # Isolate all imperfect pews: pews that hypothetically could fit more people while still distancing
    imperfect_pews = list(filter(lambda p: pew_leftover(pews[p[0]], p[1], margin) != 0, matched_pews))

    # Try swapping between imperfect pews to find a perfect one
    if len(imperfect_pews) > 1:
        # TODO(chris): write logic for swapping here
        pass

    return (matched_pews, unmatched_pews, family_counts)

def pew_leftover(pew_size, family_sizes, margin):
    """
    Returns the amount of leftover space within a pew that is not being used by the families currently sitting in it.
    A family "uses" the spaces to seat family members, plus the margin to one side needed to maintain distance.
    """
    return pew_size + margin - sum(f + margin for f in family_sizes)
