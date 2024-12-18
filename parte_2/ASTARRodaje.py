import heapq
import time
import sys
from itertools import product

def leer_mapa(archivo = sys.argv[1]):
    # Leer archivo mapa.csv y devolver mapa, posiciones iniciales y destinos
    with open (archivo, 'r') as file:
        lineas = file.readlines()

    n_aviones = int(lineas[0].strip())
    posiciones_iniciales = []
    posiciones_finales = []
    
    for i in range(1, n_aviones + 1):
        inicial, objetivo = lineas[i].strip().split()
        x_inicial, y_inicial = map(int, inicial.strip("()").split(","))
        x_objetivo, y_objetivo = map(int, objetivo.strip("()").split(","))
        posiciones_iniciales.append((x_inicial, y_inicial))
        posiciones_finales.append((x_objetivo, y_objetivo))
    
    mapa = []
    for linea in lineas[n_aviones + 1:]:
        fila = linea.strip().split(";")
        mapa.append(fila)
    
    return mapa, posiciones_iniciales, posiciones_finales
    

def generar_sucesores(estado, mapa):
    # Genera sucesores válidos desde un estado actual
    sucesores = []
    movimientos = [(-1,0), (1,0), (0,-1), (0,1), (0,0)]

    for acciones in product(movimientos, repeat=len(estado)):   # Generamos todas las combinaciones posibles gracias a product
        nuevo_estado = [(x +dx, y +dy) for (x,y), (dx,dy) in zip(estado, acciones)]     #Estamos creando el nuevo estado para cada avion
        if es_valido(nuevo_estado, estado, acciones, mapa):
            sucesores.append(tuple(nuevo_estado))
    
    return sucesores


def es_valido(nuevo_estado, estado_actual, acciones, mapa):
    # Verifica si un estado es válido: sin colisiones, sin cruces, movimientos dentro de límites.
    posiciones_ocupadas = set()

    for (nx, ny), (dx, dy) in zip(nuevo_estado, acciones):
        # Validar si la posición está dentro del mapa y no es gris
        if not (0 <= nx < len(mapa) and 0 <= ny < len(mapa[0])) or mapa[nx][ny] == 'G':
            return False  # Movimiento fuera de límites o celda bloqueada
        
        # No esperar en amarillo
        if mapa[nx][ny] == 'A' and (dx, dy) == (0, 0):
            return False  # Esperar en amarillo no permitido

        # Detectar colisiones (dos aviones en la misma celda)
        if (nx, ny) in posiciones_ocupadas:
            return False
        posiciones_ocupadas.add((nx, ny))

    # Verificar cruces simultáneos
    return not cruces_simultaneos(estado_actual, acciones)


def cruces_simultaneos(estado, acciones):
    # Verifica si hay cruces simultáneos entre celdas adyacentes.

    movimientos = {
        (x, y): (x + dx, y + dy)
        for (x, y), (dx, dy) in zip(estado, acciones)
    }

    for (origen1, destino1), (origen2, destino2) in product(movimientos.items(), repeat=2):
        if origen1 != origen2 and destino1 == origen2 and destino2 == origen1:
            return True  # Cruce simultáneo detectado
    return False


def heuristica_manhattan(estado, objetivos):
    # Calcula la distancia Manhattan desde el estado actual a los objetivos
    return sum(abs(x - gx) + abs(y - gy) for (x, y), (gx, gy) in zip(estado, objetivos))

def heuristica_2():
    pass

def a_estrella(estado_inicial, objetivos, mapa, metodo = int(sys.argv[2])):
    #Implementamos el algoritmo A* para encontrar el camino óptimo
    if metodo == 1:
        heuristica = heuristica_manhattan
    elif metodo == 2:
        heuristica = heuristica_2
    else:
        print("Error: numero de heuristica incorrecto: 1 o 2")
        sys.exit(1)

    abiertos = []  # Cola de prioridad para estados abiertos
    heapq.heappush(abiertos, (0, estado_inicial))  # Inicializamos con f=0
    g_cost = {estado_inicial: 0}  # Costo g(n) para cada estado
    padres = {estado_inicial: None}  # Guarda el camino (padres de cada estado)
    visitados = set()  # Estados ya visitados
    
    while abiertos:
        # Sacamos el nodo con el menor f(n)
        f_actual, estado_actual = heapq.heappop(abiertos)
        
        # Verificar si hemos alcanzado el estado objetivo
        if estado_actual == tuple(objetivos):
            print("todo correcto")
            return reconstruir_camino(padres, estado_actual), g_cost[estado_actual]
        
        if estado_actual in visitados:
            continue
        visitados.add(estado_actual)

        # Generar sucesores
        sucesores = generar_sucesores(estado_actual, mapa)
        for sucesor in sucesores:
            g_nuevo = g_cost[estado_actual] + 1  # Costo de moverse al sucesor (1 por movimiento)

            # Si el sucesor es nuevo o encontramos un mejor camino
            if sucesor not in g_cost or g_nuevo < g_cost[sucesor]:
                g_cost[sucesor] = g_nuevo
                f_nuevo = g_nuevo + heuristica(sucesor, objetivos)
                heapq.heappush(abiertos, (f_nuevo, sucesor))
                padres[sucesor] = estado_actual  # Guardar el padre del sucesor
    
    return None, None  # Si no se encuentra solución

def reconstruir_camino(padres, estado_final):
    # Reconstruir el camino desde el estado inicial al objetivo
    camino = []
    estado = estado_final
    while estado:
        camino.append(estado)
        estado = padres[estado]
    return camino[::-1]  # Devolvemos el camino en orden correcto


def guardar_solucion(solucion, nombre_archivo):
    # Guardar la solución en un archivo de salida
    pass

def guardar_estadisticas(tiempo, makespan, heuristica, nodos_expandidos, nombre_archivo):
    # Guardar estadísticas en un archivo .stat
    pass

mapa, inicio, fin = leer_mapa()
a_estrella(tuple(inicio), tuple(fin), mapa)
