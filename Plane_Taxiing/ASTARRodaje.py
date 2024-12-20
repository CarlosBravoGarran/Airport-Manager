import heapq
import sys
import os
import time
from itertools import product

# Read the input file
def read_map(file):
    with open(file, 'r') as f:
        lines = f.readlines()

    num_planes = int(lines[0].strip())
    initial_positions = []
    goal_positions = []

    for i in range(1, num_planes + 1):
        start, goal = lines[i].strip().split()
        initial_positions.append(tuple(map(int, start.strip('()').split(','))))
        goal_positions.append(tuple(map(int, goal.strip('()').split(','))))

    map_grid = [line.strip().split(';') for line in lines[num_planes + 1:]]
    return num_planes, initial_positions, goal_positions, map_grid

# Check if a cell is passable
def is_passable_cell(map_grid, x, y):
    rows, cols = len(map_grid), len(map_grid[0])
    return 0 <= x < rows and 0 <= y < cols and map_grid[x][y] != 'G'

# Generate successors of a state
def generate_successors(map_grid, positions):
    directions = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1), 'W': (0, 0)}
    successors_per_plane = []

    for position in positions: # Generate successors per plane
        x, y = position
        successors = []
        for move, (dx, dy) in directions.items():
            nx, ny = x + dx, y + dy 
            if move == 'W' and map_grid[x][y] == 'A': 
                continue
            if is_passable_cell(map_grid, nx, ny):
                successors.append(((nx, ny), move))
        successors_per_plane.append(successors)

    # Generate all combinations of successors
    combinations = list(product(*successors_per_plane))
    valid_successors = [
        comb for comb in combinations if are_valid_moves(comb, positions)
    ]
    return valid_successors

# Check if the moves are valid
def are_valid_moves(moves, initial_positions):
    final_positions = [move[0] for move in moves]
    if len(final_positions) != len(set(final_positions)):
        return False
    # Check for collisions
    for i, final_pos in enumerate(final_positions):
        for j, initial_pos in enumerate(initial_positions):
            if i != j and final_pos == initial_positions[j] and final_positions[j] == initial_positions[i]:
                return False
    return True

# Manhattan heuristic
def manhattan_heuristic(positions, goals):
    return sum(
        abs(pos[0] - goal[0]) + abs(pos[1] - goal[1]) for pos, goal in zip(positions, goals)
    )

# Euclidean heuristic
def euclidean_heuristic(positions, goals):
    return sum(
        ((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)**0.5 for pos, goal in zip(positions, goals)
    )

# A* algorithm
def a_star(map_grid, initial_positions, goal_positions, heuristic):
    open_list = []
    heapq.heappush(open_list, (0 + heuristic(initial_positions, goal_positions), 0, initial_positions, []))
    closed_set = set()
    expanded_nodes = 0

    while open_list:
        _, g, positions, moves = heapq.heappop(open_list) 
        if positions == goal_positions: # Solution found
            return moves, expanded_nodes

        # Check if the state has already been expanded
        if tuple(positions) in closed_set:
            continue
        closed_set.add(tuple(positions))
        expanded_nodes += 1

        # Generate successors and add them to the open list
        successors = generate_successors(map_grid, positions)
        for successor in successors:
            new_positions = [s[0] for s in successor]
            action = [s[1] for s in successor]
            new_g = g + 1 # Uniform cost of 1 per move 
            h = heuristic(new_positions, goal_positions)
            heapq.heappush(open_list, (new_g + h, new_g, new_positions, moves + [action])) # f = g + h 

    return None, expanded_nodes

# Save the output
def save_output(map_name, moves, initial_positions, output_dir, h_num):
    directions = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1), 'W': (0, 0)}
    output = ""

    for plane in range(len(initial_positions)):
        x, y = initial_positions[plane]
        line = f"{initial_positions[plane]}"
        for move in moves:
            operand = directions[move[plane]]
            x += operand[0]
            y += operand[1]
            line += f" {move[plane]} {(x, y)}"
        output += f"{line}\n"

    output_file = f"{output_dir}/{map_name}-{h_num}.output"
    with open(output_file, "w") as f:
        f.write(output)

# Save the statistics
def save_statistics(map_name, total_time, moves, initial_heuristic, expanded_nodes, output_dir, h_num):
    stat_file = f"{output_dir}/{map_name}-{h_num}.stat"
    with open(stat_file, "w") as f:
        f.write(f"Total time: {total_time:.6f}s\n")
        f.write(f"Makespan: {len(moves)}\n")
        f.write(f"Initial heuristic: {initial_heuristic}\n")
        f.write(f"Expanded nodes: {expanded_nodes}\n")

# Main function
def main():
    if len(sys.argv) != 3:
        print("Usage: python ASTARRodaje.py <path map.csv> <h_num>")
        sys.exit(1)

    map_path = sys.argv[1]
    h_num = int(sys.argv[2])

    map_name = os.path.basename(map_path).split('.')[0]
    output_dir = os.path.dirname(map_path)

    num_planes, initial_positions, goal_positions, map_grid = read_map(map_path)

    # Select heuristic
    if h_num == 1:
        heuristic = manhattan_heuristic
    elif h_num == 2:
        heuristic = euclidean_heuristic
    else:
        print("Error: h_num must be 1 (Manhattan) or 2 (Euclidean).")
        sys.exit(1)

    start_time = time.time()
    moves, expanded_nodes = a_star(map_grid, initial_positions, goal_positions, heuristic)
    total_time = time.time() - start_time

    if moves is not None:
        save_output(map_name, moves, initial_positions, output_dir, h_num)
        save_statistics(map_name, total_time, moves, heuristic(initial_positions, goal_positions), expanded_nodes, output_dir, h_num)
    else:
        print("No solution found.")

if __name__ == "__main__":
    main()
