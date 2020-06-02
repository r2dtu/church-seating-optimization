from .pews import get_pews, swap_families, best_swap, pew_leftover

def unordered(matches):
    return list(map(to_unordered_match, matches))

def to_unordered_match(match):
    pew_idx, families = match
    return pew_idx, set(families)

def test_best_swap():
    (fa, fb) = best_swap(14, [3, 2, 1], 8, [5], margin=3)

    # The best swap would swap 3 and 5.
    # The leftover for pew a would be 0, and the leftover for pew b would
    # be 5 (enough to fit another small family group).
    assert fa == 3
    assert fb == 5

    assert pew_leftover(14, [5, 2, 1], margin=3) == 0
    assert pew_leftover(8, [3], margin=3) == 5

def test_swap_families():
    pews = [14, 8]
    matched = [
        (0, [3, 2, 1]),
        (1, [5])
    ]
    margin = 3

    swap_families(pews, matched, margin)

    assert unordered(matched) == unordered([
        (0, [5, 2, 1]),
        (1, [3])
    ])

def test_main():
    families = [6, 1, 3, 2, 1, 4, 4]
    pews = [6, 7, 7, 7]
    margin = 4

    (matched, unmatched, families_left) = get_pews(families, pews, margin)

    print(matched)
    print(unmatched)
    print(families_left)

    # assert 1 == 0
    # assert unmatched == []
    # assert sum(families_left.values()) == 0

    