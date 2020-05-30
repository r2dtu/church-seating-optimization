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

    # Try swapping between imperfect pews to find if there are people who might fit
    if len(imperfect_pews) > 1 and sum(family_counts.values()) > 0:
        print('imperfect before swap:', imperfect_pews)
        swap_families(pews, imperfect_pews, margin)
        print('imperfect after swap:', imperfect_pews)

        # This essentially becomes another subset problem, but now we're looking for the subset
        # of the remaining families that can sum to the leftover space we might have
        # aggregated by swapping.
        for pew_idx, matched_families in imperfect_pews:
            leftover = pew_leftover(pews[pew_idx], matched_families, margin)

            expanded = expand_counts(family_counts) + margin

            if len(expanded) == 0:
                break

            subset = subset_sum(expanded, leftover, mode='<=')

            if subset:
                subset = np.array(subset) - margin
                for fam in subset:
                    family_counts[fam] -= 1
                    matched_families.append(fam)
                
    return (matched_pews, unmatched_pews, family_counts)

def pew_leftover(pew_size, family_sizes, margin):
    """
    Returns the amount of leftover space within a pew that is not being
    used by the families currently sitting in it.
    A family "uses" the spaces to seat family members, plus the margin
    to one side needed to maintain distance.
    """
    return pew_size + margin - sum(f + margin for f in family_sizes)

def swap_families(pew_sizes, matched_pews, margin):
    """
    Performs best swap possible between all pews in matched_pews, until no more
    best swaps can be performed. Swaps are done in-place.
    """
    swap = True
    while swap:
        swap = False
        for a in range(len(matched_pews)):
            for b in range(a + 1, len(matched_pews)):
                (pew_idx_a, families_a) = matched_pews[a]
                pew_size_a = pew_sizes[pew_idx_a]
                (pew_idx_b, families_b) = matched_pews[b]
                pew_size_b = pew_sizes[pew_idx_b]

                (fa, fb) = best_swap(pew_size_a, families_a, pew_size_b, families_b, margin)

                if fa is None or fb is None:
                    continue

                families_a.remove(fa)
                families_a.append(fb)
                families_b.remove(fb)
                families_b.append(fa)
                
                swap = True

def best_swap(pew_size_a, families_a, pew_size_b, families_b, margin):
    """
    Finds the best swap between pews a and b which will increase the
    gradient between their leftover values.
    Returns the swap as a tuple (family_a, family_b) where family_a
    and family_b are the family sizes that should be swapped from
    pews a and b, respectively.
    If no such swap exists, returns (None, None).
    """
    leftover_a = pew_leftover(pew_size_a, families_a, margin)
    leftover_b = pew_leftover(pew_size_b, families_b, margin)
    curr_diff = abs(leftover_a - leftover_b)

    max_diff = curr_diff # Limit swaps to ones that will land us in a better situation than the current one
    max_pair = (None, None)

    # No swap if one of the leftovers is 0
    if leftover_a == 0 or leftover_b == 0:
        return max_pair

    for fa in families_a:
        for fb in families_b:
            swap = fa - fb # How much the leftover will change for pew a if we swap fa and fb

            # Skip invalid swaps, where the leftover would be negative (impossible) on either pew.
            if leftover_a + swap < 0 or leftover_b - swap < 0:
                continue

            # The difference between the two leftovers IF the swap were to take place:
            diff = abs((leftover_a + swap) - (leftover_b - swap))

            # Compare with best swap, replace if better.
            if diff > max_diff:
                max_diff = diff
                max_pair = (fa, fb)

    return max_pair
