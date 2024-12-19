#!/bin/bash

# Directorio de entrada
input_dir="CSP-tests"

# Archivos de prueba
tests=(
    "01_2x2-2fr.txt"
    "02_3x3-3fr.txt"
    "03_4x4-2fr.txt"
    "04_3x3-4fr.txt"
    "05_5x5-4fr.txt"
    "06_1x3-2-2.txt"
    "07_1x5-3fr.txt"
    "08_all-JMB_1fr.txt"
    "09_all-JMB_3fr.txt"
    "10_only-STD.txt"
    "11_no-fr.txt"
    "12_t2>fr.txt"
)

# Ejecutar cada prueba
for test_file in "${tests[@]}"; do
    echo "Ejecutando prueba: $test_file"
    python3 CSPMaintenance.py "$input_dir/$test_file"
    echo "Prueba completada: $test_file"
    echo "------------------------"
done

echo "Todas las pruebas se han ejecutado."
