# Plane Maintainence and Taxiing
## Constraint Satisfaction and Heuristic Search

This repository contains the implementation of **Constraint Satisfaction and Heuristic Search** for the course **Heuristic and Optimization** at Universidad Carlos III de Madrid.

## Overview

The practice focuses on solving two main optimization problems for an airline company:

1. **Aircraft Fleet Maintenance**  
   Modeled as a Constraint Satisfaction Problem (CSP) to allocate workshops and parking spots to aircraft while meeting specific operational constraints.

2. **Aircraft Taxi Planning**  
   Solved using the A* algorithm to minimize the total time required for aircraft to reach their assigned runways without collisions.

Both problems are solved using Python, with optimized models and heuristic techniques.

---

## Repository Structure

```
.
├── Plane_Maintenance/                 # Scripts and data for the maintenance problem
│   ├── CSPMaintenance.py   # Python solution for the maintenance problem
│   ├── CSP-calls.sh        # Script to automate test case execution
│   └── CSP-tests/          # Directory containing input files for test cases
├── Plane_Taxiing/                 # Scripts and data for the taxi planning problem
│   ├── ASTARRodaje.py      # Python solution for the taxi planning problem
│   ├── ASTAR-calls.sh      # Script to automate test case execution
│   └── ASTAR-tests/       # Directory containing input files for test cases
└── README.md               # This file
```

---

## Installation and Requirements

### System Requirements

- Python 3.X
- Additional package: `python-constraint`

### Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/CarlosBravoGarran/Airport-Manager.git  # HTTPS
   git clone git@github.com:CarlosBravoGarran/Airport-Manager.git      # SSH
   cd Airport-Manager
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

   *Optional*: Create a virtual environment to avoid conflicts:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

---

## Execution

### Part 1: Aircraft Fleet Maintenance

1. Navigate to the `Plane_Maintenance` directory:

   ```bash
   cd Plane_Maintenance
   ```

2. Grant execution permissions to the test script:

   ```bash
   chmod +x CSP-calls.sh
   ```

3. Run the test cases:

   ```bash
   ./CSP-calls.sh
   ```

4. Results will be saved in `CSP-tests/` in CSV format.

### Part 2: Aircraft Taxi Planning

1. Navigate to the `Plane_Taxiing` directory:

   ```bash
   cd Plane_Taxiing
   ```

2. Grant execution permissions to the test script:

   ```bash
   chmod +x ASTAR-calls.sh
   ```

3. Run the test cases:

   ```bash
   ./ASTAR-calls.sh
   ```

4. Results will be saved in `ASTAR-tests/` in `.output` and `.stat` formats.

---


## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.
```
