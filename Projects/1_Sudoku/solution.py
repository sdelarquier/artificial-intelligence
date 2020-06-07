
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diag_right = list(''.join([r, c]) for r, c in zip(rows, cols))
diag_left = list(''.join([r, c]) for r, c in zip(rows[::-1], cols))
unitlist += [diag_right, diag_left]

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    new_values = values.copy()
    for bA in values:
        if len(values[bA]) == 2:
            for bB in peers[bA]:
                if values[bA] == values[bB]:
                    shared_peers = set(peers[bA]).intersection(set(peers[bB]))
                    for peer in shared_peers:
                        for d in values[bA]:
                            new_values[peer] = new_values[peer].replace(d, '')
#     # find all boxes with only two digits
#     unsolved_2digits = [b for b in boxes if len(values[b]) == 2]
#     for b in unsolved_2digits:
#         # find all peer boxes with the same 2 digits and no more (aka, "twins")
#         twins = [b_twin for b_twin in peers[b] if values[b] == values[b_twin]]
#         for b_twin in twins:
#             # for all twins, remove the 2 digits from all shared peers
#             shared_peers = set(peers[bA]).intersection(set(peers[bB]))
#             for b_peer in shared_peers:
#                 for d in values[b]:
#                     new_values[b_peer] = new_values[b_peer].replace(d, '')
    return new_values


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # TODO: Copy your code from the classroom to complete this function
    multi_boxes = [k for k, v in values.items() if len(v) > 1]
    for b in multi_boxes:
        b_peer_values = set(values[b_peer] for b_peer in peers[b] if len(values[b_peer]) == 1)
        b_uniq_values = set(values[b]).difference(b_peer_values)
        values[b] = ''.join(sorted(b_uniq_values))
    return values


def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # TODO: Copy your code from the classroom to complete this function
    multi_boxes = [k for k, v in values.items() if len(v) > 1]
    for b in multi_boxes:
        for unit in units[b]:
            b_unit_values = set(values[b_unit] for b_unit in unit)
            b_uniq_values = set(values[b]).difference(b_unit_values)
            if len(b_uniq_values) == 1:
                values[b] = b_uniq_values.pop()
                break
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # TODO: Copy your code from the classroom and modify it to complete this function
    stalled = False
    unsolved_boxes = lambda values: len([b for b in boxes if len(values[b]) > 1])
    unsolved_boxes_before = unsolved_boxes(values)
    while not stalled:
        values = eliminate(values)
        unsolved_boxes_after = unsolved_boxes(values)
        if unsolved_boxes_after == 0:
            stalled = True
        
        values = only_choice(values)
        unsolved_boxes_after = unsolved_boxes(values)
        if unsolved_boxes_after == 0:
            stalled = True
        
        values = naked_twins(values)
        unsolved_boxes_after = unsolved_boxes(values)
        if unsolved_boxes_after == 0:
            stalled = True
        
        # Make sure you stop when your stuck
        if unsolved_boxes_after == unsolved_boxes_before:
            stalled = True
        
        # Catch unsolvable cases
        if any(len(v) == 0 for v in values.values()):
            return False
        
        # Update number of unsolved boxes
        unsolved_boxes_before = unsolved_boxes_after
    
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # TODO: Copy your code from the classroom to complete this function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n, b = min((len(values[b]), b) for b in boxes if len(values[b]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[b]:
        new_sudoku = values.copy()
        new_sudoku[b] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
