#!/bin/bash

# Directorio de entrada
input_dir="CSP-tests"

# Crear lista de pruebas ordenadas numéricamente
tests=($(ls "$input_dir"/*.txt | sort -V))

# Ejecutar cada prueba
for test_file in "${tests[@]}"; do
    echo "Ejecutando prueba: $test_file"
    python3 CSPMaintenance.py "$test_file"
    echo "Prueba completada: $test_file"
    echo "------------------------"
done

echo "Todas las pruebas se han ejecutado."
