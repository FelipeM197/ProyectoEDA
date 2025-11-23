import pandas as pd                 #Libreria pandas para el manejo de datos 
import time                         #Libreria time para medir tiempos de ejecucion
import os                           #Libreria os para saber si existe en el sistema operativo un archivo
import sys                          #Libreria sys para aumentar el limite de recursión
import math                         #Libreria math para funciones matematicas
import multiprocessing as mult      #Libreria multiprocessing para paralelismo

# En python hay un seguro que impide que una funcion se llame asi misma infinitas veces y se bloquee el programa
# Aumentamos el límite de recursión para QuickSort con 1 millón de datos para evitar bloqueos

sys.setrecursionlimit(2000000)

# Configuración regional para el formato de números, ya que o si no los calculos ser harán con comas en vez de puntos

def quick_sort (lista, llave):
    """
    Se implementa el algoritmo de QuickSort de forma recursiva para ordenar una lista de diccionarios
    en función de una clave específica en orden descendente.
    """

    #Si la lista es de longitud 0 o 1, ya está ordenada
    #Retornamos la lista tal cual
    if len(lista) <= 1:
        return lista
    else:
        #Elegimos el pivote (elemento central)
        pivote = lista[len(lista) // 2] 

        #Dividimos la lista en tres sublistas
        #Nota: Para orden DESCENDENTE (Mayor a Menor):
        
        #Si el valor de la llave es mayor, va a la lista de la izquierda (primeros)
        menores = [x for x in lista if x[llave] > pivote[llave]]

        #Si el valor de la llave es igual, va a la lista de iguales
        iguales = [x for x in lista if x[llave] == pivote[llave]]

        #Si el valor de la llave es menor, va a la lista de la derecha (últimos)
        mayores = [x for x in lista if x[llave] < pivote[llave]]

        #Recursivamente ordenamos las sublistas y las concatenamos
        return quick_sort(menores, llave) + iguales + quick_sort(mayores, llave)
    
def heap(lista, n, i, llave):
    """
    Función auxiliar para el algoritmo HeapSort.
    """
    mayor = i               #Asumiendo que el nodo actual es el mayor
    izq = 2 * i + 1         #Índice del hijo izquierdo
    der = 2 * i + 2         #Índice del hijo derecho

    # Verificamos si los hijos son MENORES que el nodo actual (Min-Heap)
    # Esto es necesario para que, al intercambiar con el final, el orden sea DESCENDENTE.

    if izq < n and lista[izq][llave] < lista[mayor][llave]:
        mayor = izq

    if der < n and lista[der][llave] < lista[mayor][llave]:
        mayor = der

    # Si el mayor (que ahora apunta al menor) no es el nodo actual...
    if mayor != i:
        lista[i], lista[mayor] = lista[mayor], lista[i]
        heap(lista, n, mayor, llave)

def heap_sort(lista, llave):
    """
    Implementación del algoritmo HeapSort para ordenar una lista de diccionarios
    en función de una clave específica en orden descendente.
    """
    n = len(lista)

    # Construir el heap (reorganizar la lista)
    for i in range(n // 2 - 1, -1, -1):
        heap(lista, n, i, llave)

    # Extraer elementos del heap uno por uno
    for i in range(n - 1, 0, -1):
        lista[i], lista[0] = lista[0], lista[i]   # Intercambiar
        heap(lista, i, 0, llave)                  # Llamar a heapify en el heap reducido

    return lista

def fusionar_dos_listas(listaA, listaB, llave):
    """
    Implementación "simple" (manual) de la fusión de dos listas ordenadas.
    (Ordena DESCENDENTEMENTE)
    """
    lista_fusionada = []
    
    # Punteros (índices) para la Lista A y la Lista B
    i = 0 #puntero lista A
    j = 0 #puntero lista B
    
    # Recorremos ambas listas mientras haya elementos en las dos
    while i < len(listaA) and j < len(listaB):
        # (Orden DESCENDENTE)
        if listaA[i][llave] > listaB[j][llave]:
            lista_fusionada.append(listaA[i])
            i += 1 # Avanzamos el puntero A
        else:
            lista_fusionada.append(listaB[j])
            j += 1 # Avanzamos el puntero B

    #Si sobran elementos en la lista A, los añadimos al final
    lista_fusionada.extend(listaA[i:])
    lista_fusionada.extend(listaB[j:])

    return lista_fusionada

            
def fusionar_chucks(trozos, llave):

    """
    Función para fusionar múltiples listas ordenadas en una sola lista ordenada.
    """

    if not trozos:
        return []
    
    #Se comienza con el primer trozo
    resuldado = trozos[0]

    #Se va uniendo el resultado con cada uno de los trozos restantes
    for i in range(1, len(trozos)):
        resuldado = fusionar_dos_listas(resuldado, trozos[i], llave)
    
    return resuldado


def paralelismo_mulltiproceso(args):
    """
    Lo que se ejecuta en cada proceso hijo (nucleos).
    """
    algoritmo, lista, llave = args

    # Mostrar informacion de los nucleos
    # Usa la biblioteca multiprocessing para obtener el nombre y PID del proceso actual

    #current_process devuelve el proceso actual y .name y .pid dan el nombre y PID respectivamente
    proc_name = mult.current_process().name
    pid = mult.current_process().pid
    # imprimir nombre del núcleo y PID (información de los procesos workers)
    print(f"Núcleo: {proc_name}  PID: {pid}  - Ordenando {len(lista)} elementos usando {algoritmo.capitalize()}")

    if algoritmo == 'quicksort':
        return quick_sort(lista, llave)
    elif algoritmo == 'heapsort':
        return heap_sort(lista, llave)
    
    return lista

def ordenar_paralelo(lista, algoritmo, llave):
    """
    Orquesta el ordenamiento en paralelo usando múltiples procesos.
    """
    print(f"Iniciando {algoritmo.capitalize()} Paralelo por '{llave}'...")
    
    # Determina el número de núcleos disponibles
    num_nucleos = mult.cpu_count()
    print(f"Usando {num_nucleos} núcleos de CPU...")
    
    # Divide la lista en trozos aproximadamente iguales
    n = len(lista)
    tamano_trozo = math.ceil(n / num_nucleos)
    
    # Crear los trozos
    trozos = [lista[i : i + tamano_trozo] for i in range(0, n, tamano_trozo)]
    print(f"Lista dividida en {len(trozos)} trozos de ~{tamano_trozo} elementos.")

    # Crear un pool de procesos
    with mult.Pool(processes=num_nucleos) as pool:
        
        print("Enviando trozos a los núcleos para ordenar (pool.map)...")
        
        # Preparar los argumentos para cada proceso
        args = [(algoritmo, trozo, llave) for trozo in trozos]
        trozos_ordenados = pool.map(paralelismo_mulltiproceso, args)
        
        print("Ordenamiento de trozos completado. Fusionando resultados...")
    
    # Fusionar los trozos ordenados en una sola lista ordenada
    lista_final_ordenada = fusionar_chucks(trozos_ordenados, llave)
    
    return lista_final_ordenada


def main():
    """Función principal del programa"""
    # Definición de archivos de entrada y salida (ubicados en la misma carpeta del script)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    archivo_entrada = os.path.join(base_dir, "datos_procesados_py.csv")
    archivo_quick_sort = os.path.join(base_dir, "datos_ordenados_quick_sort.csv") # Archivo exclusivo de QuickSort
    archivo_heap_sort = os.path.join(base_dir, "datos_ordenados_heap_sort.csv")   # Archivo exclusivo de HeapSort
    
    m = 100  # Número mínimo de revisiones para considerar

    print(f"Cargando datos desde: {archivo_entrada}")

    if not os.path.exists(archivo_entrada):
        print(f"Error: El archivo {archivo_entrada} no existe.")
        return

    try:
        datos = pd.read_csv(archivo_entrada)
    except Exception as e:
        print(f"Error al leer el archivo {archivo_entrada}: {e}")
        return
    
    # Asegurar que las columnas necesarias existan y tengan el tipo correcto
    datos['Rating'] = pd.to_numeric(datos['Rating'], errors='coerce').fillna(0.0)
    datos['NumberReview'] = pd.to_numeric(datos['NumberReview'], errors='coerce').fillna(0).astype(int)
    
    lista_restaurantes = datos.to_dict('records')
    C = datos['Rating'].mean()

    print("\nMenu de opciones de ordenamiento:")
    print("1. QuickSort por numero de reseñas")
    print("2. HeapSort  por puntuacion total, desde el archivo de QuickSort")

    try:
        opcion = int(input("Seleccione una opción (1-2): "))
    except ValueError:
        print("Entrada inválida."); return
    
    print("Iniciando procesamiento...")
    tiempo_inicio = time.time()

    
    archivo_salida_actual = "" # Variable para saber qué archivo guardamos al final

    if opcion == 1:

        lista_restaurantes = ordenar_paralelo(lista_restaurantes, 'quicksort', 'NumberReview')
        
        # Configuración para reporte y guardado
        archivo_salida_actual = archivo_quick_sort
        llave_reporte = 'NumberReview'
        
        # Inicializamos puntuacion en 0 solo para el formato
        for r in lista_restaurantes:
            r['puntuacion_total'] = 0.0

    elif opcion == 2:
        
        # Verificar si el archivo de QuickSort existe, si no, generarlo
        if not os.path.exists(archivo_quick_sort):
            print(f"El archivo '{archivo_quick_sort}' no existe.")
            print("Ejecutando QuickSort automáticamente para generarlo primero...")
            
            lista_temp = ordenar_paralelo(lista_restaurantes, 'quicksort', 'NumberReview')
            df_temp = pd.DataFrame(lista_temp)
            # Inicializar puntuacion para que no falle al guardar
            df_temp['puntuacion_total'] = 0.0
            # Añadir posicion temporal
            df_temp.insert(0, 'Posicion', range(1, len(df_temp) + 1))
            
            columnas_temp = ['Posicion', 'Organization', 'Rating', 'NumberReview', 'puntuacion_total']
            # Asegurar que solo usamos columnas que existen
            cols_existentes = [col for col in columnas_temp if col in df_temp.columns]
            df_temp[cols_existentes].to_csv(archivo_quick_sort, index=False)
            print("Archivo intermedio generado y guardado.")
        
        # Leemos desde el nuevo archivo
        print(f"Leyendo datos ordenados desde disco: {archivo_quick_sort}...")
        try:
            datos_cargados = pd.read_csv(archivo_quick_sort)
            lista_restaurantes = datos_cargados.to_dict('records')
        except Exception as e:
            print(f"Error al leer archivo intermedio: {e}")
            return

        print("Calculando puntuaciones de confianza...")
        for r in lista_restaurantes:
            R = float(r.get('Rating', 0))
            v = int(r.get('NumberReview', 0))
            if (v + m) != 0:
                r['puntuacion_total'] = (v / (v + m)) * R + (m / (v + m)) * C
            else:
                r['puntuacion_total'] = 0.0

        print("Ordenando por 'puntuacion_total' con HeapSort...")
        lista_restaurantes = ordenar_paralelo(lista_restaurantes, 'heapsort', 'puntuacion_total')
        
        # Configuración para reporte y guardado
        archivo_salida_actual = archivo_heap_sort
        llave_reporte = 'puntuacion_total'

    else:
        print("Opción inválida.")
        return
    
    # Cálculo del tiempo de ejecución
    tiempo_fin = time.time()
    tiempo_total = (tiempo_fin - tiempo_inicio) * 1000.0

    print(f"Guardando datos ordenados en: {archivo_salida_actual}")

    datos_ordenados = pd.DataFrame(lista_restaurantes)

    # Recalcular o añadir columna de posición (si ya existe por la lectura, se sobrescribe para ser correcta)
    if 'Posicion' in datos_ordenados.columns:
        del datos_ordenados['Posicion']
    datos_ordenados.insert(0, 'Posicion', range(1, len(datos_ordenados) + 1))

    # Selección dinámica de columnas
    if opcion == 1:
        columnas_finales = ['Posicion', 'Organization', 'Rating', 'NumberReview']
    else:
        columnas_finales = ['Posicion', 'Organization', 'Rating', 'NumberReview', 'puntuacion_total']

    # Filtrar columnas válidas
    columnas_finales = [col for col in columnas_finales if col in datos_ordenados.columns]

    try:
        datos_ordenados[columnas_finales].to_csv(archivo_salida_actual, index=False)
        print(f"\nDatos ordenados guardados exitosamente en: {archivo_salida_actual}")
    except Exception as e:
        print(f"Error al guardar el archivo: {e}")
        return

    print(f"\nTiempo total de operación: {tiempo_total:.2f} ms")

    print(f"\nTop 20 restaurantes ÚNICOS ordenados por '{llave_reporte}':")
    
    nombres_vistos = set()
    contador = 0
    
    # Imprimir encabezado manual para que se vea ordenado
    # Ajustamos el espaciado (width) según las columnas
    if opcion == 1:
        print(f"{'Pos':<5} {'Organization':<40} {'Rating':<10} {'Reviews':<10}")
    else:
        print(f"{'Pos':<5} {'Organization':<40} {'Rating':<10} {'Reviews':<10} {'Score':<10}")

    for r in lista_restaurantes:
        nombre = r.get('Organization', 'Desconocido')
        
        # Si ya vimos este nombre, saltamos a la siguiente iteración
        if nombre in nombres_vistos:
            continue
            
        # Si es nuevo, lo añadimos al set y lo imprimimos
        nombres_vistos.add(nombre)
        contador += 1
        
        # Formatear la salida
        pos = contador
        rating = r.get('Rating', 0)
        reviews = r.get('NumberReview', 0)
        
        # Recortar nombre si es muy largo para que no rompa la tabla
        nombre_imp = (nombre[:37] + '..') if len(str(nombre)) > 37 else str(nombre)
        
        if opcion == 1:
            print(f"{pos:<5} {nombre_imp:<40} {rating:<10} {reviews:<10}")
        else:
            score = r.get('puntuacion_total', 0)
            print(f"{pos:<5} {nombre_imp:<40} {rating:<10} {reviews:<10} {score:.4f}")
        
        # Detenernos al llegar a 20 únicos
        if contador >= 20:
            break

    print("\nPrograma finalizado.")


if __name__ == "__main__":
    # freeze_support es necesario en Windows para evitar ejecuciones recursivas del main
    mult.freeze_support()
    main()