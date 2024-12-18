import sys
import os
import random
from constraint import Problem

def leer_datos(archivo):
    with open(archivo, 'r') as f:
        lineas = [linea.strip() for linea in f.readlines()]

    # Número de franjas horarias
    franjas = int(lineas[0].split(":")[1].strip())

    # Tamaño de la matriz
    matriz_tamaño = lineas[1]

    # Talleres y parkings
    talleres_std = [tuple(map(int, pos.strip("()").split(","))) for pos in lineas[2].split(":")[1].strip().split()]
    talleres_spc = [tuple(map(int, pos.strip("()").split(","))) for pos in lineas[3].split(":")[1].strip().split()]
    parkings = [tuple(map(int, pos.strip("()").split(","))) for pos in lineas[4].split(":")[1].strip().split()]

    # Aviones
    aviones = []
    for avion in lineas[5:]:
        id_, tipo, restr, t1, t2 = avion.split("-")
        aviones.append({
            "id": id_,
            "tipo": tipo,
            "restr": restr == "T",  # Convertir a booleano
            "t1": int(t1),
            "t2": int(t2),
        })

    return franjas, matriz_tamaño, talleres_std, talleres_spc, parkings, aviones


def resolver_problema(franjas, talleres_std, talleres_spc, parkings, aviones, limite_soluciones=None):
    
    problem = Problem()
    # Generar dominio
    dominio = talleres_std + talleres_spc + parkings

    # Crear variables para cada avión y cada franja horaria
    for avion in aviones:
        for franja in range(0, franjas):
            clave = f"{avion['id']}_f{franja}"
            problem.addVariable(clave, dominio)

    # Restricciones
    def capacidad_taller(*asignaciones):
        ocupaciones = {}
        for pos in asignaciones:
            if pos not in ocupaciones:
                ocupaciones[pos] = 0
            ocupaciones[pos] += 1
        return all(count <= 2 for count in ocupaciones.values())

    def maximo_un_jmb(*asignaciones):
        ocupaciones = {}
        for pos in asignaciones:
            if pos not in ocupaciones:
                ocupaciones[pos] = 0
            ocupaciones[pos] += 1
        return all(count <= 1 for count in ocupaciones.values())
    
    def compatibilidad_tareas(asignaciones, tareas_tipo2):
        talleres_visitados = set(asignaciones)
        if tareas_tipo2 > 0:
            return any(taller in talleres_spc for taller in talleres_visitados)
        return True

    def orden_tareas(t2, t1):
        return t2 in talleres_spc and t1 in (talleres_spc + list(talleres_std))
    
    def restriccion_parking(asignaciones, tareas, total_franjas):
        total_parkings = sum(1 for pos in asignaciones if pos in parkings)
        print("Total", total_parkings)
        max_parkings = total_franjas - tareas
        print("Max", max_parkings)
        if tareas == total_franjas:
            return total_parkings == 0
        return total_parkings <= max_parkings

    def maniobrabilidad(*asignaciones):
        ocupadas = set(asignaciones)
        for pos in ocupadas:
            x, y = pos
            adyacentes = {(x + dx, y + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]}
            if any(adj in ocupadas for adj in adyacentes):
                return False
        return True

    # Aplicar restricciones a cada franja horaria
    for franja in range(franjas):
        variables_franja = [f"{avion['id']}_f{franja}" for avion in aviones if f"{avion['id']}_f{franja}" in problem._variables]
        if variables_franja:
            problem.addConstraint(capacidad_taller, variables_franja)
            problem.addConstraint(maniobrabilidad, variables_franja)

        variables_jmb = [f"{avion['id']}_f{franja}" for avion in aviones if avion["tipo"] == "JMB" and f"{avion['id']}_f{franja}" in problem._variables]
        if variables_jmb:
            problem.addConstraint(maximo_un_jmb, variables_jmb)

    for avion in aviones:
        variables_avion = [f"{avion['id']}_f{franja}" for franja in range(avion["t1"], min(avion["t2"] + 1, franjas))]
        problem.addConstraint(
            lambda *asignaciones, t2=avion["t2"]: compatibilidad_tareas(asignaciones, t2),
            variables_avion
        )

        if avion["restr"]:
            for franja in range(avion["t1"], min(avion["t2"], franjas - 1)):
                t2_var = f"{avion['id']}_f{franja}"
                t1_var = f"{avion['id']}_f{franja + 1}"
                if t2_var in problem._variables and t1_var in problem._variables:
                    problem.addConstraint(orden_tareas, (t2_var, t1_var))


    # Límite de soluciones
    soluciones = []
    for solucion in problem.getSolutionIter():
        soluciones.append(solucion)
        if limite_soluciones and len(soluciones) >= limite_soluciones:
            break
    return soluciones

def guardar_resultados(archivo_salida, soluciones, aviones, talleres_std, talleres_spc, parkings):
    def formatear_posicion(pos):
        if pos in talleres_std:
            return f"STD{pos}"
        elif pos in talleres_spc:
            return f"SPC{pos}"
        elif pos in parkings:
            return f"PRK{pos}"
        else:
            raise ValueError(f"Posición no válida: {pos}")

    # Seleccionar un número aleatorio de soluciones a guardar (al menos 1)
    # num_soluciones = random.randint(1, len(soluciones))
    num_soluciones = len(soluciones)
    soluciones_a_guardar = random.sample(soluciones, num_soluciones)

    with open(archivo_salida, 'w') as f:
        # Escribir el número total de soluciones generadas
        f.write(f"N. Sol: {len(soluciones)}\n")
        
        for solucion in soluciones:
            index = soluciones.index(solucion)
            f.write(f"Solución {index+1}:\n")
            for avion in aviones:
                posiciones = []
                for franja in range(franjas):
                    clave = f"{avion['id']}_f{franja}"
                    if clave in solucion:
                        posiciones.append(formatear_posicion(solucion[clave]))
                f.write(f"{avion['id']}-{avion['tipo']}-{'T' if avion['restr'] else 'F'}-{avion['t1']}-{avion['t2']}: {', '.join(posiciones)}\n")

if __name__ == "__main__":
    archivo_entrada = sys.argv[1]

    # Crear el nombre del archivo de salida basado en el archivo de entrada
    base_name = os.path.splitext(os.path.basename(archivo_entrada))[0]
    archivo_salida = f"{base_name}.csv"

    # Leer datos y resolver el problema
    franjas, matriz_tamaño, talleres_std, talleres_spc, parkings, aviones = leer_datos(archivo_entrada)
    soluciones = resolver_problema(franjas, talleres_std, talleres_spc, parkings, aviones, 100)
    guardar_resultados(archivo_salida, soluciones, aviones, talleres_std, talleres_spc, parkings)

    print(f"Resultados guardados en {archivo_salida}")
