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

    # Comprobar que no hay más tareas que franjas
    for avion in aviones:
        total_tareas = avion["t1"] + avion["t2"]
        if total_tareas > franjas:
            raise ValueError(f"El avión {avion['id']} tiene más tareas ({total_tareas}) que franjas disponibles ({franjas}).")

    # Crear variables para cada avión y cada franja horaria
    for avion in aviones:
        for franja in range(0, franjas):
            clave = f"{avion['id']}_f{franja}"
            problem.addVariable(clave, dominio)

    # Restricción: Máximo de aviones por taller
    def capacidad_taller(*asignaciones):
        ocupaciones = {}
        for avion, asignacion in zip(aviones, asignaciones):
            if asignacion not in ocupaciones:
                ocupaciones[asignacion] = {"JMB": 0, "STD": 0}
            if avion["tipo"] == "JMB":
                ocupaciones[asignacion]["JMB"] += 1
            else:
                ocupaciones[asignacion]["STD"] += 1

        for cuenta in ocupaciones.values():
            if cuenta["JMB"] > 1 or (cuenta["JMB"] == 1 and cuenta["STD"] > 0):
                return False
            if cuenta["STD"] > 2:
                return False
        return True


    for franja in range(franjas):
        variables_franja = [f"{avion['id']}_f{franja}" for avion in aviones]
        problem.addConstraint(capacidad_taller, variables_franja)

    # Restricción: Tareas especialistas en talleres especialistas
    def tareas_especialistas(*asignaciones):
        return all(asignacion in talleres_spc for asignacion in asignaciones)

    for avion in aviones:
        if avion["t2"] > 0:
            variables_t2 = [f"{avion['id']}_f{franja}" for franja in range(avion["t2"])]
            problem.addConstraint(tareas_especialistas, variables_t2)

    # Restricción: Orden de tareas especialistas antes de estándar
    def orden_tareas(*asignaciones):
        franjas_spc = [i for i, asignacion in enumerate(asignaciones) if asignacion in talleres_spc]
        franjas_std = [i for i, asignacion in enumerate(asignaciones) if asignacion in talleres_std]
        if franjas_spc and franjas_std:
            return max(franjas_spc) < min(franjas_std)
        return True

    for avion in aviones:
        if avion["t2"] > 0 and avion["t1"] > 0 and avion["restr"]:
            variables_avion = [f"{avion['id']}_f{franja}" for franja in range(franjas)]
            problem.addConstraint(orden_tareas, variables_avion)

    # Restricción: Maniobrabilidad de los aviones
    def maniobrabilidad(*asignaciones):
        ocupadas = set(asignaciones)
        for pos in ocupadas:
            adyacentes = {(pos[0] + dx, pos[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]}
            if all(adj in ocupadas for adj in adyacentes):
                return False
        return True


    for franja in range(franjas):
        variables_franja = [f"{avion['id']}_f{franja}" for avion in aviones]
        problem.addConstraint(maniobrabilidad, variables_franja)

    # Restricción: Separación de JUMBOS
    def separacion_jumbos(*asignaciones):
        jumbo_positions = [
            asignacion for avion, asignacion in zip(aviones, asignaciones) if avion["tipo"] == "JMB"
        ]
        jumbo_positions_set = set(jumbo_positions)
        for pos in jumbo_positions:
            adyacentes = [(pos[0] + dx, pos[1] + dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]]
            if any(adj in jumbo_positions_set for adj in adyacentes):
                return False
        return True

    # Seleccionar variables solo de aviones JUMBOS
    jumbo_variables = [
        f"{avion['id']}_f{franja}" for avion in aviones if avion["tipo"] == "JMB" for franja in range(franjas)
    ]
    problem.addConstraint(separacion_jumbos, jumbo_variables)


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
    
    # Ruta del directorio de soluciones
    solutions_dir = "solutions"
    if not os.path.exists(solutions_dir):
        os.makedirs(solutions_dir)  # Crear el directorio si no existe

    # Archivo de salida dentro del directorio solutions
    archivo_salida = os.path.join(solutions_dir, f"{base_name}.csv")

    try:
        # Leer datos y resolver el problema
        franjas, matriz_tamaño, talleres_std, talleres_spc, parkings, aviones = leer_datos(archivo_entrada)
        soluciones = resolver_problema(franjas, talleres_std, talleres_spc, parkings, aviones, None)
        guardar_resultados(archivo_salida, soluciones, aviones, talleres_std, talleres_spc, parkings)

        print(f"Resultados guardados en {archivo_salida}")
        
    # Gestión de errores
    except ValueError as e:
        print(e)
