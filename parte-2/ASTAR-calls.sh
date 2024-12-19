#!/bin/bash

# Directorio de los casos de prueba
input_dir="ASTAR-tests"

# Lista de pruebas ordenadas numéricamente
tests=($(ls $input_dir/*.csv | sort -V))

# Ejecutar cada prueba
for test_file in "${tests[@]}"; do
    base_name=$(basename "$test_file" .csv)
    echo "Ejecutando prueba con heurística Manhattan (h_num = 1): $base_name"
    python3 ASTARRodaje.py "$test_file" 1
    echo "Prueba completada con heurística Manhattan: $base_name"
    echo "------------------------"
    
    echo "Ejecutando prueba con heurística Euclidiana (h_num = 2): $base_name"
    python3 ASTARRodaje.py "$test_file" 2
    echo "Prueba completada con heurística Euclidiana: $base_name"
    echo "------------------------"
done

echo "Todas las pruebas se han ejecutado."
