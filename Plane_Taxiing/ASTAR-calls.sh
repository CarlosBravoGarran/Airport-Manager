#!/bin/bash

# Directory of test cases
input_dir="ASTAR-tests"

# List of tests sorted numerically
tests=($(ls $input_dir/*.csv | sort -V))

# Execute each test
for test_file in "${tests[@]}"; do
    base_name=$(basename "$test_file" .csv)
    echo "Running test with Manhattan heuristic (h_num = 1): $base_name"
    python3 ASTARRodaje.py "$test_file" 1
    echo "Test completed with Manhattan heuristic: $base_name"
    echo "------------------------"
    
    echo "Running test with Euclidean heuristic (h_num = 2): $base_name"
    python3 ASTARRodaje.py "$test_file" 2
    echo "Test completed with Euclidean heuristic: $base_name"
    echo "------------------------"
done

echo "All tests have been executed."
