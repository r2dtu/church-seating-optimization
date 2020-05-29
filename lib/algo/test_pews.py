from .pews import get_pews

def test_main():
    families = [6, 1, 3, 2, 1, 4, 4]
    pews = [6, 7, 8, 9]
    margin = 4

    (matched, unmatched, families_left) = get_pews(families, pews, margin)

    print(matched)
    print(families_left)

    assert matched == []
    assert unmatched == []
    assert families_left == []

    