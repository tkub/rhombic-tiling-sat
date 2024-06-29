import sys
import itertools
from collections import defaultdict
from pysat.card import *
from pysat.formula import CNF
from pysat.solvers import Solver

def print_help():
    """Print help information for the program."""
    print("Usage: python script_name.py <n> [constraint_type]")
    print("  <n>: Size of the grid (must be a positive integer)")
    print("  [constraint_type]: Optional. Either 'area' or 'border'. Default is 'area'")
    print("\nExample: python script_name.py 3 border")

def generate_id():
    """Generate unique IDs for variables."""
    i = 0
    while True:
        i += 1
        yield i

def set_to_border_id(s):
    """Convert a set of border numbers to a border ID string."""
    return f"b{''.join(str(x) for x in sorted(s))}"

def enumerate_borders(border, inside):
    """Enumerate possible border configurations."""
    init = 2 - len(inside)
    borders = []
    
    if init == 2:  # Acute vertex
        borders = [[set_to_border_id({((l-1)+3)%6+1} | border) for l in border]]
    
    available_borders = set(range(1, 7)) - border - inside
    borders += [[set_to_border_id(border | set(s)) for s in itertools.combinations(available_borders, i)]
                for i in range(init, len(available_borders)+1)]
    
    return list(itertools.chain.from_iterable(borders))

def border_pattern(i, j, direction, di, dj, border, inside):
    """Generate border pattern constraints."""
    return [[-var[i,j,direction]] + 
            [var[(i+di)%N,(j+dj)%N,b] for b in enumerate_borders(border, inside)]]


def generate_tile_info():
    """Generate core positions and direction information for tiles in a skew coordinate system."""
    core_positions = [(0,-1), (1,-1), (1,0), (0,1), (-1,1), (-1,0)]

    dir_info = {
        '↑': {'positions': [(1,-2),(-1,2)], 'forbidden': [(0,-2,'↖'), (0,2,'↖'), (2,-2,'↗'), (-2,2,'↗')]},
        '↖': {'positions': [(-1,-1),(1,1)], 'forbidden': [(0,2,'↑'), (0,-2,'↑'), (-2,0,'↗'), (2,0,'↗')]},
        '↗': {'positions': [(2,-1),(-2,1)], 'forbidden': [(2,-2,'↑'), (-2,2,'↑'), (-2,0,'↖'), (2,0,'↖')]},
    }

    return core_positions, dir_info

def occupied_grids(i, j, d):
    """Calculate occupied grids and forbidden positions for a given tile."""
    # Hexagon around the center
    #
    #                     (1,-2)    <2,-2>
    #                    /      \  
    #     (-1,-1) -- [0,-1] -- [1,-1] -- (2,-1)
    #             \  /     \  /    \    /
    #          [-1,0]  -- {0,0}  -- [1,0]
    #             /  \     /  \     /  \
    #      (-2,1) -- [-1,1] -- [0,1] -- (1,1)
    #                    \      /
    #            <-2,2>   (-1,2)
    #
    # Base represented on a triangular grid
    core_positions, dir_info = generate_tile_info()
    positions = core_positions + dir_info[d]['positions']
    
    forbidden_core = [(dx, dy, other_d) for other_d, info in dir_info.items() if other_d != d
                      for dx, dy in info['positions']]
    forbidden_dir = dir_info[d]['forbidden']
    
    return ([((i+di)%N,(j+dj)%N) for di,dj in positions], 
            [((i+di)%N,(j+dj)%N,dd) for di,dj,dd in forbidden_core + forbidden_dir])


def generate_area_constraints():
    """Generate constraints for the area-based approach."""
    constraints = []
    for i, j in grid_positions:
        for di, direction in enumerate('↖↑↗'):
            occupied_area, occupied_margin = occupied_grids(i, j, direction)
            for oi, oj in occupied_area:
                for other_direction in '↖↑↗':
                    constraints.append([-var[i,j,direction], -var[oi,oj,other_direction]])
            for oi, oj, dd in occupied_margin:
                constraints.append([-var[i,j,direction], -var[oi,oj,dd]])
            for dj in range(di+1, 3):
                other_direction = '↖↑↗'[dj]
                constraints.append([-var[i,j,direction], -var[i,j,other_direction]])
    return constraints


def generate_border_constraints():
    """Generate constraints for the border-based approach."""
    # Hexagon around the center
    #   1     2
    #     \ /
    # 6 --ij  -- 3
    #     / \
    #   5     4
    # p(x,y,center) → p(x-1,y,edge point)
    # Define border patterns for each direction
    constraints = []
    border_patterns = {
        '↑': [
            (-1,  0, {2,4}, {3}),   # <  left
            (+1,  0, {1,5}, {6}),   # >  right
            ( 0, -1, {2,5}, {3,4}), # / top left
            ( 0, +1, {2,5}, {1,6}), # / bottom right
            (+1, -1, {1,4}, {6,5}), # \ top right
            (-1, +1, {1,4}, {2,3}), # \ bottom left
            (+1, -2, {5,4}, set()), # ^ top
            (-1, +2, {1,2}, set()), # V bottom
        ],
        '↖': [
            (-1, +1, {1,3}, {2}),   # < bottom left
            (+1, -1, {4,6}, {5}),   # > top right
            ( 0, -1, {3,6}, {4,5}), # / top
            ( 0, +1, {3,6}, {1,2}), # / bottom
            (-1,  0, {1,4}, {2,3}), # \ left
            (+1,  0, {1,4}, {5,6}), # \ right
            (-1, -1, {3,4}, set()), # ^ top left
            (+1, +1, {1,6}, set()), # V bottom right
        ],
        '↗': [
            ( 0, -1, {3,5}, {4}),   # < top left
            ( 0, +1, {2,6}, {1}),   # > bottom right
            (+1, -1, {3,6}, {4,5}), # / top
            (-1, +1, {3,6}, {1,2}), # / bottom
            (-1,  0, {2,5}, {3,4}), # \ left
            (+1,  0, {2,5}, {1,6}), # \ bottom
            (+2, -1, {6,5}, set()), # ^ top right
            (-2, +1, {2,3}, set()), # V bottom left
        ]
    }
    
    for i, j in grid_positions:
        for direction, patterns in border_patterns.items():
            for di, dj, border, inside in patterns:
                constraints.extend(border_pattern(i, j, direction, di, dj, border, inside))
    
    # Additional constraints (if any)
    border_pattern_ids = {b for (_, _, b), _ in var.items() if b.startswith('b')}
    for i, j in grid_positions:
        for b1, b2 in itertools.combinations(border_pattern_ids | {'↖','↑','↗'}, 2):
            constraints.append([-var[i,j, b1], -var[i,j, b2]])
    
    return constraints


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Error: Incorrect number of arguments.")
        print_help()
        sys.exit(1)

    try:
        n = int(sys.argv[1])
        if n <= 0:
            raise ValueError("n must be a positive integer")
    except ValueError as e:
        print(f"Error: Invalid value for n. {e}")
        print_help()
        sys.exit(1)

    N = 2 * n  # Side length of the grid for rhombic tile centers
    grid_positions = list(itertools.product(range(N), repeat=2))
    
    Ln = n**2  # Number of rhombic tiles to be placed
    
    constraint_type = sys.argv[2] if len(sys.argv) > 2 else 'area'
    if constraint_type not in ['area', 'border']:
        print(f"Error: Invalid constraint type '{constraint_type}'. Must be either 'area' or 'border'.")
        print_help()
        sys.exit(1)

    dimacs_file = f'rhombic-tiling-{n}x{n}-{constraint_type}.cnf'
    solution_file = f'rhombic{n}x{n}-{constraint_type}.csv'
    
    next_id = generate_id()
    var = defaultdict(lambda: next(next_id))
    
    if constraint_type == 'area':
        cnf = generate_area_constraints()
    else:
        cnf = generate_border_constraints()
    
    # Extract variables for rhombic tile positions
    rhombic_vars = [id for (i,j,b), id in var.items() if b in '↖↑↗']
    top_id = max(var.values())
    
    id_to_var = {id: (i,j,b) for (i,j,b), id in var.items() if b in '↖↑↗'}
    
    # Cardinality constraint: exactly Ln panels
    cnf_card = CardEnc.equals(lits=rhombic_vars, bound=Ln,
                              top_id=top_id, encoding=EncType.kmtotalizer)
    
    cnf.extend(cnf_card)
    
    with open(dimacs_file, "w") as f:
        f.write(CNF(from_clauses=cnf).to_dimacs())
    
    print(f"DIMACS CNF file written to {dimacs_file}")
    
    solutions = []
    with Solver(bootstrap_with=cnf) as s:
        for literals in s.enum_models():
            solutions.append([id_to_var[vid] for vid in literals if vid > 0 and vid in id_to_var])
    
    with open(solution_file, "w") as f:
        for n, patterns in enumerate(sorted(solutions)):
            print(f"{n+1}:", ",".join(f"{i}{j}{d}" for (i,j,d) in sorted(patterns)), file=f)
    print(f"Solution file written to {solution_file}")

