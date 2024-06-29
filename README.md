# Rhombic Tiling SAT Solver

This program solves the problem of tiling a hexagonal grid with rhombic tiles using a SAT (Boolean Satisfiability) solver approach. It can generate all possible valid tilings for a given grid size.

## Description

The rhombic tiling problem involves covering a hexagonal grid with rhombic tiles without gaps or overlaps. This program uses two different constraint types to solve the problem:

1. Area-based constraints
2. Border-based constraints

The program generates a CNF (Conjunctive Normal Form) file that can be solved using a SAT solver, and then interprets the results to produce all valid tilings.

## Usage

To run the program, use the following command:

```sh
python rhombic_tiling_sat.py <n> [constraint_type]
```

Where:
- `<n>` is the size of the grid (must be a positive integer)
- `[constraint_type]` is optional and can be either 'area' or 'border'. Default is 'area'

Example:

```sh
python rhombic_tiling_sat.py 3 border
```

This will generate tilings for a 3x3 grid using border-based constraints.

## Output

The program generates two files:
1. A DIMACS CNF file: `rhombic-tiling-<n>x<n>-<constraint_type>.cnf`
2. A solution file: `rhombic<n>x<n>-<constraint_type>.csv`

The solution file contains all valid tilings found by the SAT solver.

## Requirements

- Python 3.6 or higher
- PySAT library

To install PySAT, run:

```bash
pip install python-sat
```

## Author

Tetsuji KUBOYAMA, Gakushuin University

## License

MIT License

Copyright (c) 2024 Tetsuji KUBOYAMA

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Acknowledgments

This work was partially supported by JSPS KAKENHI (grant numbers JP20K15181, JP23H03461, JP23K28151 and JP24K17619).

