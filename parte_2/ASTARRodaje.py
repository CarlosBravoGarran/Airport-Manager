import heapq
import sys
import os
import time
from itertools import product

# Leer el archivo de entrada
def leer_mapa(archivo):
    with open(archivo, 'r') as f:
        lineas = f.readlines()

    num_aviones = int(lineas[0].strip())
    posiciones_iniciales = []
    posiciones_objetivo = []

    for i in range(1, num_aviones + 1):
        inicio, objetivo = lineas[i].strip().split()
        posiciones_iniciales.append(tuple(map(int, inicio.strip('()').split(','))))
        posiciones_objetivo.append(tuple(map(int, objetivo.strip('()').split(','))))

    mapa = [linea.strip().split(';') for linea in lineas[num_aviones + 1:]]
    return num_aviones, posiciones_iniciales, posiciones_objetivo, mapa

# Verificar si una celda es transitable
def celda_transitable(mapa, x, y):
    filas, columnas = len(mapa), len(mapa[0])
    return 0 <= x < filas and 0 <= y < columnas and mapa[x][y] != 'G'

# Generar los sucesores de un estado
def generar_sucesores(mapa, posiciones):
    direcciones = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1), 'W': (0, 0)}
    sucesores_por_avion = []

    for posicion in posiciones: # Generar sucesores por avión
        x, y = posicion
        sucesores = []
        for mov, (dx, dy) in direcciones.items():
            nx, ny = x + dx, y + dy 
            if mov == 'W' and mapa[x][y] == 'A': 
                continue
            if celda_transitable(mapa, nx, ny):
                sucesores.append(((nx, ny), mov))
        sucesores_por_avion.append(sucesores)

    # Generar todas las combinaciones de sucesores
    combinaciones = list(product(*sucesores_por_avion))
    sucesores_validos = [
        comb for comb in combinaciones if movimientos_validos(comb, posiciones)
    ]
    return sucesores_validos

# Verificar si los movimientos son válidos
def movimientos_validos(movimientos, posiciones_iniciales):
    posiciones_finales = [mov[0] for mov in movimientos]
    if len(posiciones_finales) != len(set(posiciones_finales)):
        return False
    # Verificar si hay colisiones
    for i, pos_final in enumerate(posiciones_finales):
        for j, pos_inicial in enumerate(posiciones_iniciales):
            if i != j and pos_final == posiciones_iniciales[j] and posiciones_finales[j] == posiciones_iniciales[i]:
                return False
    return True

# Heurística de Manhattan
def heuristica_manhattan(posiciones, objetivos):
    return sum(
        abs(pos[0] - obj[0]) + abs(pos[1] - obj[1]) for pos, obj in zip(posiciones, objetivos)
    )

# Heurística distancia Euclidea
def heuristica_euclidea(posiciones, objetivos):
    return sum(
        ((pos[0] - obj[0])**2 + (pos[1] - obj[1])**2)**0.5 for pos, obj in zip(posiciones, objetivos)
    )

# Algoritmo A*
def a_star(mapa, posiciones_iniciales, posiciones_objetivo, heuristica):
    lista_abierta = []
    heapq.heappush(lista_abierta, (0 + heuristica(posiciones_iniciales, posiciones_objetivo), 0, posiciones_iniciales, []))
    conjunto_cerrado = set()
    nodos_expandidos = 0

    while lista_abierta:
        _, g, posiciones, movimientos = heapq.heappop(lista_abierta)
        if posiciones == posiciones_objetivo: # Solución encontrada
            return movimientos, nodos_expandidos

        # Verificar si el estado ya ha sido expandido
        if tuple(posiciones) in conjunto_cerrado:
            continue
        conjunto_cerrado.add(tuple(posiciones))
        nodos_expandidos += 1

        # Generar sucesores y agregarlos a la lista abierta
        sucesores = generar_sucesores(mapa, posiciones)
        for sucesor in sucesores:
            nuevas_posiciones = [s[0] for s in sucesor]
            accion = [s[1] for s in sucesor]
            nuevo_g = g + 1
            h = heuristica(nuevas_posiciones, posiciones_objetivo)
            heapq.heappush(lista_abierta, (nuevo_g + h, nuevo_g, nuevas_posiciones, movimientos + [accion]))

    return None, nodos_expandidos

# Guardar el output
def guardar_output(nombre_mapa, movimientos, posiciones_iniciales, directorio_salida, h_num):
    direcciones = {'↑': (-1, 0), '↓': (1, 0), '←': (0, -1), '→': (0, 1), 'W': (0, 0)}
    salida = ""

    for avion in range(len(posiciones_iniciales)):
        x, y = posiciones_iniciales[avion]
        linea = f"{posiciones_iniciales[avion]}"
        for mov in movimientos:
            operando = direcciones[mov[avion]]
            x += operando[0]
            y += operando[1]
            linea += f" {mov[avion]} {(x, y)}"
        salida += f"{linea}\n"

    output_file = f"{directorio_salida}/{nombre_mapa}-{h_num}.output"
    with open(output_file, "w") as f:
        f.write(salida)

# Guardar las estadísticas
def guardar_estadisticas(nombre_mapa, tiempo_total, movimientos, heuristica_inicial, nodos_expandidos, directorio_salida, h_num):
    stat_file = f"{directorio_salida}/{nombre_mapa}-{h_num}.stat"
    with open(stat_file, "w") as f:
        f.write(f"Tiempo total: {tiempo_total:.6f}s\n")
        f.write(f"Makespan: {len(movimientos)}\n")
        f.write(f"h inicial: {heuristica_inicial}\n")
        f.write(f"Nodos expandidos: {nodos_expandidos}\n")

# Función principal
def main():
    if len(sys.argv) != 3:
        print("Uso: python ASTARRodaje.py <path mapa.csv> <h_num>")
        sys.exit(1)

    ruta_mapa = sys.argv[1]
    h_num = int(sys.argv[2])

    nombre_mapa = os.path.basename(ruta_mapa).split('.')[0]
    directorio_salida = os.path.dirname(ruta_mapa)

    num_aviones, posiciones_iniciales, posiciones_objetivo, mapa = leer_mapa(ruta_mapa)

    # Seleccionar heurística
    if h_num == 1:
        heuristica = heuristica_manhattan
    elif h_num == 2:
        heuristica = heuristica_euclidea
    else:
        print("Error: h_num debe ser 1 (Manhattan) o 2 (Euclidea).")
        sys.exit(1)

    inicio = time.time()
    movimientos, nodos_expandidos = a_star(mapa, posiciones_iniciales, posiciones_objetivo, heuristica)
    tiempo_total = time.time() - inicio

    if movimientos is not None:
        guardar_output(nombre_mapa, movimientos, posiciones_iniciales, directorio_salida, h_num)
        guardar_estadisticas(nombre_mapa, tiempo_total, movimientos, heuristica(posiciones_iniciales, posiciones_objetivo), nodos_expandidos, directorio_salida, h_num)
    else:
        print("No se encontró solución.")

if __name__ == "__main__":
    main()
