#from utils import *
#from PsSudoku import *

assignments = []

""" -------------------------------------------------------------------------"""

rows = 'ABCDEFGHI'
cols = '123456789'
boxes = [r + c for r in rows for c in cols]
history = {}  # history must be declared here so that it exists in the assign_values scope

def cross(a, b):
    return [s+t for s in a for t in b]

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]

# diagonal units defined
diagonal_unit1 = [[r+c for r,c in zip(rows,cols)]]
diagonal_unit2 = [[r+c for r,c in zip(rows,cols[::-1])]]

#Adding diagonal units to the unitlist
unitlist = row_units + column_units + square_units + diagonal_unit1 + diagonal_unit2
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

""" -------------------------------------------------------------------------"""

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

""" -------------------------------------------------------------------------"""

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

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
    """
    '''Find all instances of naked twins
    Eliminate the naked twins as possibilities for their peers'''
    
    right_boxes = [box for box in values.keys() if len(values[box]) == 2]

    # find those with the naked twins.
    naked_twins = []
    for rb in right_boxes:
        for pr in peers[rb]:
            if values[rb] == values[pr] and [pr, rb] not in naked_twins: 
                naked_twins.append([rb, pr])

    # Eliminate the naked twins for their peers 
    for twins in naked_twins:
        twn_box1 = twins[0]
        twn_box2 = twins[1]
        pr1 = peers[twn_box1]
        pr2 = peers[twn_box2]
        common_peers = pr1 & pr2

    # Delete the the naked twins from their common peers.
        for cpr in common_peers:
            if values[cpr] != values[twn_box1]:
                for val in values[twn_box1]:
                    values = assign_value(values, cpr, values[cpr].replace(val, ''))
    return values
    
""" -------------------------------------------------------------------------"""

def values2grid(values):
    """Convert the dictionary board representation to as string

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    """
    res = []
    for r in rows:
        for c in cols:
            v = values[r + c]
            res.append(v if len(v) == 1 else '.')
    return ''.join(res)


def grid2values(grid):
    """Convert grid into a dict of {square: char} with '123456789' for empties.

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    
    Returns
    -------
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value,
            then the value will be '123456789'.
    """
    sudoku_grid = {}
    for val, key in zip(grid, boxes):
        if val == '.':
            sudoku_grid[key] = '123456789'
        else:
            sudoku_grid[key] = val
    return sudoku_grid

""" -------------------------------------------------------------------------"""


def display(values):
    """Display the values as a 2-D grid.

    Parameters
    ----------
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print()

""" -------------------------------------------------------------------------"""

def reconstruct(values, history):
    """Returns the solution as a sequence of value assignments 

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    history(dict)
        a dictionary of the form {key: (key, (box, value))} encoding a linked
        list where each element points to the parent and identifies the value
        assignment that connects from the parent to the current state

    Returns
    -------
    list
        a list of (box, value) assignments that can be applied in order to the
        starting Sudoku puzzle to reach the solution
    """
    path = []
    prev = values2grid(values)
    while prev in history:
        prev, step = history[prev]
        path.append(step)
    return path[::-1]

""" -------------------------------------------------------------------------"""

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
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(digit,'')
    return values

""" -------------------------------------------------------------------------"""

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
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values

""" -------------------------------------------------------------------------"""

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
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Use the Eliminate Strategy
        values = eliminate(values)
        # Use the Only Choice Strategy
        values = only_choice(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

""" -------------------------------------------------------------------------"""

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
       # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

""" -------------------------------------------------------------------------"""

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

""" -------------------------------------------------------------------------"""

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
