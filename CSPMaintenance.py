import sys
from constraint import Problem

def leer_datos(archivo):
    with open(archivo, 'r') as f:
        lineas = [linea.strip() for linea in f.readlines()]

    # Número de franjas horarias
    franjas = int(lineas[0])

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
        for franja in range(franjas):
            problem.addVariable(f"{avion['id']}_f{franja}", dominio)

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
        variables_franja = [f"{avion['id']}_f{franja}" for avion in aviones]
        problem.addConstraint(capacidad_taller, variables_franja)
        problem.addConstraint(maniobrabilidad, variables_franja)

        variables_jmb = [f"{avion['id']}_f{franja}" for avion in aviones if avion["tipo"] == "JMB"]
        if variables_jmb:
            problem.addConstraint(maximo_un_jmb, variables_jmb)

    for avion in aviones:
        problem.addConstraint(
            lambda *asignaciones, t2=avion["t2"]: compatibilidad_tareas(asignaciones, t2),
            [f"{avion['id']}_f{franja}" for franja in range(franjas)]
        )
        if avion["restr"]:
            for franja in range(franjas - 1):
                t2_var = f"{avion['id']}_f{franja}"
                t1_var = f"{avion['id']}_f{franja + 1}"
                problem.addConstraint(orden_tareas, (t2_var, t1_var))

    # Límite de soluciones
    soluciones = []
    for solucion in problem.getSolutionIter():
        soluciones.append(solucion)
        if limite_soluciones and len(soluciones) >= limite_soluciones:
            break

    return soluciones


def guardar_resultados(archivo_salida, soluciones):
    with open(archivo_salida, 'w') as f:
        f.write(f"N. Sol: {len(soluciones)}\n")
        for i, solucion in enumerate(soluciones):
            f.write(f"Solución {i + 1}:\n")
            for avion, asignaciones in solucion.items():
                f.write(f"{avion}: {asignaciones}\n")

if __name__ == "__main__":
    archivo_entrada = sys.argv[1]
    archivo_salida = "solution.csv"

    # Leer datos y resolver el problema
    franjas, matriz_tamaño, talleres_std, talleres_spc, parkings, aviones = leer_datos(archivo_entrada)
    soluciones = resolver_problema(franjas, talleres_std, talleres_spc, parkings, aviones, 200)
    guardar_resultados(archivo_salida, soluciones)

    print(f"Resultados guardados en {archivo_salida}")
