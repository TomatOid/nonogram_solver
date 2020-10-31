# Nonogram Solver
A Nonogram or Japaneese crossword is a logic puzzle with 3 simple rules:
- The numbers on the edges represent runs of filled squares.
- Each of these runs must have at least one space between each of them.
- The runs must be in the same order as the numbers on the edges.
<a/>
    This simple program is capible of both single and multi-line reasoning, and will come up with a solution for every valid puzzle.
## Features:
- A faster brute-force method for generating single-line overlaps compared to iterate-and-check.
- Keeps track of which rows / columns have been affected by a change so it only handles what it needs to.
- Backtracking for solving non-trivial puzzles.
- Optional detection of multiple solutions (On by default).
## Bugs:
- The code is ugly and somewhat difficult to understand.
