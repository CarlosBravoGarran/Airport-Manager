import sys
import os
import random
from constraint import Problem

def read_data(file):
    with open(file, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    # Number of time slots
    time_slots = int(lines[0].split(":")[1].strip())

    # Matrix size
    matrix_size = lines[1]

    # Workshops and parkings
    std_workshops = [tuple(map(int, pos.strip("()").split(","))) for pos in lines[2].split(":")[1].strip().split()]
    spc_workshops = [tuple(map(int, pos.strip("()").split(","))) for pos in lines[3].split(":")[1].strip().split()]
    parkings = [tuple(map(int, pos.strip("()").split(","))) for pos in lines[4].split(":")[1].strip().split()]

    # Planes
    planes = []
    for plane in lines[5:]:
        id_, type_, restr, t1, t2 = plane.split("-")
        planes.append({
            "id": id_,
            "type": type_,
            "restr": restr == "T",  # Convert to boolean
            "t1": int(t1),
            "t2": int(t2),
        })

    return time_slots, matrix_size, std_workshops, spc_workshops, parkings, planes


def solve_problem(time_slots, std_workshops, spc_workshops, parkings, planes, solution_limit=None):
    
    problem = Problem()

    # Generate domain
    domain = std_workshops + spc_workshops + parkings

    # Check that there are no more tasks than time slots
    for plane in planes:
        total_tasks = plane["t1"] + plane["t2"]
        if total_tasks > time_slots:
            raise ValueError(f"The plane {plane['id']} has more tasks ({total_tasks}) than available time slots ({time_slots}).")

    # Create variables for each plane and each time slot
    for plane in planes:
        for slot in range(0, time_slots):
            key = f"{plane['id']}_s{slot}"
            problem.addVariable(key, domain)

    # Constraint: Maximum planes per workshop
    def workshop_capacity(*assignments):
        occupations = {}
        for plane, assignment in zip(planes, assignments):
            if assignment not in occupations:
                occupations[assignment] = {"JMB": 0, "STD": 0}
            if plane["type"] == "JMB":
                occupations[assignment]["JMB"] += 1
            else:
                occupations[assignment]["STD"] += 1

        for count in occupations.values():
            if count["JMB"] > 1 or (count["JMB"] == 1 and count["STD"] > 0):
                return False
            if count["STD"] > 2:
                return False
        return True


    for slot in range(time_slots):
        slot_variables = [f"{plane['id']}_s{slot}" for plane in planes]
        problem.addConstraint(workshop_capacity, slot_variables)

    # Constraint: Specialist tasks in specialist workshops
    def specialist_tasks(*assignments):
        return all(assignment in spc_workshops for assignment in assignments)

    for plane in planes:
        if plane["t2"] > 0:
            t2_variables = [f"{plane['id']}_s{slot}" for slot in range(plane["t2"])]
            problem.addConstraint(specialist_tasks, t2_variables)

    # Constraint: Order of specialist tasks before standard
    def task_order(*assignments):
        spc_slots = [i for i, assignment in enumerate(assignments) if assignment in spc_workshops]
        std_slots = [i for i, assignment in enumerate(assignments) if assignment in std_workshops]
        if spc_slots and std_slots:
            return max(spc_slots) < min(std_slots)
        return True

    for plane in planes:
        if plane["t2"] > 0 and plane["t1"] > 0 and plane["restr"]:
            plane_variables = [f"{plane['id']}_s{slot}" for slot in range(time_slots)]
            problem.addConstraint(task_order, plane_variables)

    # Constraint: Plane maneuverability
    def maneuverability(*assignments):
        occupied = set(assignments)
        for pos in occupied:
            adjacent = {(pos[0] + dx, pos[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]}
            if all(adj in occupied for adj in adjacent):
                return False
        return True


    for slot in range(time_slots):
        slot_variables = [f"{plane['id']}_s{slot}" for plane in planes]
        problem.addConstraint(maneuverability, slot_variables)

    # Constraint: JUMBO separation
    def jumbo_separation(*assignments):
        jumbo_positions = [
            assignment for plane, assignment in zip(planes, assignments) if plane["type"] == "JMB"
        ]
        jumbo_positions_set = set(jumbo_positions)
        for pos in jumbo_positions:
            adjacent = [(pos[0] + dx, pos[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            if any(adj in jumbo_positions_set for adj in adjacent):
                return False
        return True

    # Select variables only for JUMBO planes
    jumbo_variables = [
        f"{plane['id']}_s{slot}" for plane in planes if plane["type"] == "JMB" for slot in range(time_slots)
    ]
    problem.addConstraint(jumbo_separation, jumbo_variables)


    # Solution limit
    solutions = []
    for solution in problem.getSolutionIter():
        solutions.append(solution)
        if solution_limit and len(solutions) >= solution_limit:
            break
    return solutions

def save_results(output_file, solutions, planes, std_workshops, spc_workshops, parkings):
    def format_position(pos):
        if pos in std_workshops:
            return f"STD{pos}"
        elif pos in spc_workshops:
            return f"SPC{pos}"
        elif pos in parkings:
            return f"PRK{pos}"
        else:
            raise ValueError(f"Invalid position: {pos}")

    # Select a random number of solutions to save (at least 1)
    if solutions:
        num_solutions = random.randint(1, len(solutions))
        solutions_to_save = solutions[:num_solutions]  # Select the first `num_solutions`
    else:
        solutions_to_save = []

    with open(output_file, 'w') as f:
        # Write the total number of generated solutions
        f.write(f"N. Sol: {len(solutions)}\n")

        for solution in solutions_to_save:
            index = solutions.index(solution)
            f.write(f"Solution {index+1}:\n")
            for plane in planes:
                positions = []
                for slot in range(time_slots):
                    key = f"{plane['id']}_s{slot}"
                    if key in solution:
                        positions.append(format_position(solution[key]))
                f.write(f"{plane['id']}-{plane['type']}-{'T' if plane['restr'] else 'F'}-{plane['t1']}-{plane['t2']}: {', '.join(positions)}\n")


if __name__ == "__main__":
    input_file = sys.argv[1]

    # Create the output file name based on the input file
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    
    # Output file within the same input directory
    output_file = f"{os.path.dirname(input_file)}/{base_name}.csv"

    try:
        # Read data and solve the problem
        time_slots, matrix_size, std_workshops, spc_workshops, parkings, planes = read_data(input_file)
        solutions = solve_problem(time_slots, std_workshops, spc_workshops, parkings, planes, None)
        save_results(output_file, solutions, planes, std_workshops, spc_workshops, parkings)

        print(f"Results saved in {output_file}")

    # Error handling
    except ValueError as e:
        print(e)
