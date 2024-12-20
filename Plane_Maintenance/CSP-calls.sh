#!/bin/bash

# Input directory
input_dir="CSP-tests"

# Create a list of tests sorted numerically
tests=($(ls "$input_dir"/*.txt | sort -V))

# Execute each test
for test_file in "${tests[@]}"; do
    echo "Running test: $test_file"
    python3 CSPMaintenance.py "$test_file"
    echo "Test completed: $test_file"
    echo "------------------------"
done

echo "All tests have been executed."
