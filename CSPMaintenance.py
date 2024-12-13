from constraint import Problem

def leer_datos_archivo(ruta_archivo):
    """Lee los datos del archivo de entrada y los estructura."""
    with open(ruta_archivo, 'r') as archivo:
        lineas = archivo.readlines()

    franjas_horarias = int(lineas[0].strip())
    tamanio_matriz = tuple(map(int, lineas[1].strip().split('x')))
    talleres_std = [tuple(map(int, coord[1:-1].split(','))) for coord in lineas[2].strip().replace('STD:', '').split()]
    talleres_spc = [tuple(map(int, coord[1:-1].split(','))) for coord in lineas[3].strip().replace('SPC:', '').split()]
    parkings = [tuple(map(int, coord[1:-1].split(','))) for coord in lineas[4].strip().replace('PRK:', '').split()]
    aviones = [linea.strip() for linea in lineas[5:]]

    return franjas_horarias, tamanio_matriz, talleres_std, talleres_spc, parkings, aviones

def crear_modelo(franjas_horarias, talleres_std, talleres_spc, parkings, aviones, debug=False):
    """Crea el modelo del problema usando python-constraint."""
    problem = Problem()

    # Crear variables para cada avión en cada franja horaria con dominios ajustados
    for avion in aviones:
        id_avion = avion.split('-')[0]
        tipo_tarea = avion.split('-')[2]  # Extraer si requiere tareas tipo 2 (T o F)
        if tipo_tarea == "T":
            dominios = talleres_spc  # Solo talleres especialistas para tareas tipo 2
        else:
            dominios = talleres_std + talleres_spc + parkings

        for franja in range(franjas_horarias):
            problem.addVariable(f"{id_avion}_franja_{franja}", dominios)

    if debug:
        print("Variables creadas con dominios ajustados.")

    # Restricción 1: Cada posición puede tener un único avión por franja horaria
    for franja in range(franjas_horarias):
        variables_franja = [f"{avion.split('-')[0]}_franja_{franja}" for avion in aviones]

        def no_repetidos(*asignaciones):
            return len(set(asignaciones)) == len(asignaciones)

        problem.addConstraint(no_repetidos, variables_franja)

    if debug:
        print("Restricción 1 aplicada.")

    # Restricción 2: Capacidad máxima de los talleres
    talleres = talleres_std + talleres_spc
    for franja in range(franjas_horarias):
        for taller in talleres:
            def capacidad_taller(*asignaciones):
                asignados = [a for a in asignaciones if a == taller]
                jumbos = sum(1 for a in asignados if a in talleres_spc)
                return len(asignados) <= 2 and jumbos <= 1

            variables_taller = [f"{avion.split('-')[0]}_franja_{franja}" for avion in aviones]
            problem.addConstraint(capacidad_taller, variables_taller)

    if debug:
        print("Restricción 2 aplicada.")

    # Restricción 3: Compatibilidad de talleres y tareas
    for avion in aviones:
        id_avion = avion.split('-')[0]
        tipo_tarea = avion.split('-')[2]  # Extraer si requiere tareas tipo 2 (T o F)
        if tipo_tarea == "T":
            for franja in range(franjas_horarias):
                def solo_talleres_especialistas(asignacion, talleres_spc=talleres_spc):
                    return asignacion in talleres_spc

                problem.addConstraint(
                    solo_talleres_especialistas,
                    [f"{id_avion}_franja_{franja}"]
                )

    if debug:
        print("Restricción 3 aplicada.")

    # Restricción 4: Orden de las tareas
    for avion in aviones:
        id_avion = avion.split('-')[0]
        tipo_tarea = avion.split('-')[2]  # Extraer si requiere tareas tipo 2 (T o F)
        t2 = int(avion.split('-')[3])  # Número de tareas tipo 2
        t1 = int(avion.split('-')[4])  # Número de tareas tipo 1

        # Franjas para tareas tipo 2
        for franja in range(t2):
            def tareas_tipo2(asignacion, talleres_spc=talleres_spc):
                return asignacion in talleres_spc

            problem.addConstraint(
                tareas_tipo2,
                [f"{id_avion}_franja_{franja}"]
            )

        # Franjas para tareas tipo 1
        for franja in range(t2, t2 + t1):
            def tareas_tipo1(asignacion, talleres=talleres_std + talleres_spc):
                return asignacion in talleres

            problem.addConstraint(
                tareas_tipo1,
                [f"{id_avion}_franja_{franja}"]
            )

    if debug:
        print("Restricción 4 aplicada.")

    # Restricción 5: Restricciones de maniobrabilidad
    movimientos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    for franja in range(franjas_horarias):
        variables_franja = [f"{avion.split('-')[0]}_franja_{franja}" for avion in aviones]

        def maniobrabilidad(*asignaciones):
            ocupadas = set(asignaciones)
            for asignacion in asignaciones:
                if asignacion is None:
                    continue
                x, y = asignacion
                adyacentes_libres = any((x + dx, y + dy) not in ocupadas for dx, dy in movimientos)
                if not adyacentes_libres:
                    return False
            return True

        problem.addConstraint(maniobrabilidad, variables_franja)

    if debug:
        print("Restricción 5 aplicada.")

    # Restricción 6: Separación entre JUMBOS
    movimientos = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    aviones_jumbo = [avion for avion in aviones if avion.split('-')[1] == "JMB"]
    for franja in range(franjas_horarias):
        variables_franja = [f"{avion.split('-')[0]}_franja_{franja}" for avion in aviones_jumbo]

        def separacion_jumbos(*asignaciones):
            ocupadas = set(asignaciones)
            for asignacion in asignaciones:
                if asignacion is None:
                    continue
                x, y = asignacion
                adyacentes_ocupadas = sum(1 for dx, dy in movimientos if (x + dx, y + dy) in ocupadas)
                if adyacentes_ocupadas > 0:
                    return False
            return True

        problem.addConstraint(separacion_jumbos, variables_franja)

    if debug:
        print("Restricción 6 aplicada.")

    return problem

def guardar_resultados(ruta_salida, soluciones):
    """Guarda las soluciones encontradas en un archivo CSV."""
    with open(ruta_salida, 'w') as archivo:
        archivo.write(f"N. Sol: {len(soluciones)}\n")
        for i, solucion in enumerate(soluciones, start=1):
            archivo.write(f"Solución {i}:\n")
            for clave, valor in solucion.items():
                archivo.write(f"{clave}: {valor}\n")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Uso: python CSPMaintenance.py <path maintenance>")
        sys.exit(1)

    ruta_entrada = sys.argv[1]
    ruta_salida = ruta_entrada.replace('.txt', '.csv')

    # Leer datos del archivo
    franjas_horarias, tamanio_matriz, talleres_std, talleres_spc, parkings, aviones = leer_datos_archivo(ruta_entrada)

    # Crear modelo y resolver
    problema = crear_modelo(franjas_horarias, talleres_std, talleres_spc, parkings, aviones, debug=True)

    # Reducir el número de soluciones computadas para evitar tiempos largos
    soluciones = problema.getSolutions()[:10]

    # Guardar resultados
    guardar_resultados(ruta_salida, soluciones)

    print(f"Resultados guardados en {ruta_salida}")
