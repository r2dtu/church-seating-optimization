import numpy as np

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