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
        #menores, iguales y mayores que el pivote

        #Si el valor de la llave es mayor, va a la lista de menores
        menores = [x for x in lista if x[llave] > pivote[llave]]

        #Si el valor de la llave es igual, va a la lista de iguales
        iguales = [x for x in lista if x[llave] == pivote[llave]]

        #Si el valor de la llave es menor, va a la lista de mayores
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

    # Verificamos si los hijos son mayores que el nodo actual

    #si el valor de la llave es mayor, actualizamos el mayor
    if izq < n and lista[izq][llave] > lista[mayor][llave]:
        mayor = izq

    #si el valor de la llave es mayor, actualizamos el mayor
    if der < n and lista[der][llave] > lista[mayor][llave]:
        mayor = der

    # Si el mayor no es el nodo actual, intercambiamos y seguimos heapificando
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
    1. Recibe los argumentos necesarios.
    2. Llama al algoritmo de ordenamiento correspondiente.
    3. Retorna la lista ordenada.
    4. El proceso padre se encarga de fusionar los resultados.
    5. Retorna la lista ordenada final.
    6. Usa QuickSort o HeapSort según se indique.
    7. args: tupla (función, lista, llave)
    8. Retorna la lista ordenada.
    9. Algoritmo: 'quicksort' o 'heapsort'
    10. Usa la función adecuada según el algoritmo.
    11. Retorna la lista ordenada.
    12. Si el algoritmo no es reconocido, retorna la lista sin ordenar.
    """
    algoritmo, lista, llave = args

    # Mostrar informacion de los nucleos
    # Usa la biblioteca multiprocessing para obtener el nombre y PID del proceso actual

    #current_process devuelve el proceso actual y .name y .pid dan el nombre y PID respectivamente
    proc_name = mult.current_process().name
    pid = mult.current_process().pid
    print ( "Nucleo:", proc_name, " PID:", pid, " - Ordenando", len(lista), "elementos usando", algoritmo.capitalize())
    
    if algoritmo == 'quicksort':
        return quick_sort(lista, llave)
    elif algoritmo == 'heapsort':
        return heap_sort(lista, llave)
    
    return lista

def ordenar_paralelo(lista, algoritmo, llave):
    """
    Orquesta el ordenamiento en paralelo usando múltiples procesos.
    1. Divide la lista en trozos.
    2. Crea un pool de procesos.
    3. Envía los trozos a los procesos para ordenar.
    4. Fusiona los resultados ordenados.
    5. Retorna la lista ordenada final.
    """
    print(f"Iniciando {algoritmo.capitalize()} Paralelo...")
    
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


#Oe pelada te falta refactorizar el main ojo

def main():
    """Función principal del programa"""
    # Definición de archivos de entrada y salida
    archivo_entrada = "datos_procesados_py.csv"
    archivo_salida = "datos_ordenados_py.csv"
    m = 100  # Número mínimo de revisiones para considerar

    print(f"Cargando datos desde: {archivo_entrada}")

    # Verificación de existencia del archivo
    if not os.path.exists(archivo_entrada):
        print(f"Error: El archivo {archivo_entrada} no existe.")
        return

    # Lectura del archivo CSV
    try:
        datos = pd.read_csv(archivo_entrada)
    except Exception as e:
        print(f"Error al leer el archivo {archivo_entrada}: {e}")
        return
    
    # Asegurar que las columnas necesarias existan
    #Fillna lo que hace es rellenar los valores nulos con un valor por defecto 0
    datos['Rating'] = pd.to_numeric(datos['Rating'], errors='coerce').fillna(0.0)
    datos['NumberReview'] = pd.to_numeric(datos['NumberReview'], errors='coerce').fillna(0).astype(int)
    
    # Se convierte la lista en diccionarios para facilitar el manejo

    lista_restaurantes = datos.to_dict('records')

    # Cálculo de la puntuación global C (promedio de todos los ratings)
    # mean calcula el promedio de una columna en pandas
    C = datos['Rating'].mean()

    #Menu de opciones de ordenamiento

    print("\nMenu de opciones de ordenamiento (Paralelo):")
    print("1. QuickSort (Paralelo - Múltiples Núcleos)")
    print("2. HeapSort (Paralelo - Múltiples Núcleos)")

    # Seleccion del algoritmo de ordenamiento
    # Manejo de errores para entradas inválidas

    try:
        opcion = int(input("Seleccione una opción (1-2): "))
        if opcion == 1:
            algoritmo_elegido = 'quicksort'
        elif opcion == 2:
            algoritmo_elegido = 'heapsort'
        else:
            print("Opción inválida. Saliendo."); return
    except ValueError:
        print("Entrada inválida."); return
    
    ### El tiempo total incluye el cálculo de la fórmula + el ordenamiento
    print("Iniciando procesamiento y ordenamiento...")
    tiempo_inicio = time.time()

    # Iniciamos el ordenamiento paralelo infdicando que la llave es 'Rating'
    lista_restaurantes = ordenar_paralelo(lista_restaurantes, algoritmo_elegido, 'Rating')

    # CALCULAR LA PUNTUACIÓN TOTAL PARA CADA RESTAURANTE
    # Aplicamos luego del primer ordenamiento para tener los datos limpios
    for r in lista_restaurantes:
        R = r.get('Rating', 0)
        v = r.get('NumberReview', 0)
        try:
            # asegurar tipos numéricos
            R = float(R)
            v = int(v)
        except Exception:
            R = 0.0
            v = 0
        if (v + m) != 0:
            r['puntuacion_total'] = (v / (v + m)) * R + (m / (v + m)) * C
        else:
            r['puntuacion_total'] = 0.0

   
    # Calculamos segun la formula de puntuacion total
    lista_restaurantes = ordenar_paralelo(lista_restaurantes, algoritmo_elegido, 'puntuacion_total')
    
    # Cálculo del tiempo de ejecución
    tiempo_fin = time.time()
    tiempo_total = (tiempo_fin - tiempo_inicio) * 1000.0

    # GUARDAR LOS RESULTADOS EN UN NUEVO ARCHIVO CSV
    print(f"Guardando datos ordenados en: {archivo_salida}")

    datos_ordenados = pd.DataFrame(lista_restaurantes)

    # Añadir columna de posición
    datos_ordenados.insert(0, 'Posicion', range(1, len(datos_ordenados) + 1))

    # Selección y renombre de columnas (SOLO LAS NECESARIAS para que no consuma mucho ram pandas)
    columnas_finales = ['Posicion', 'Organization', 'Rating', 'NumberReview', 'puntuacion_total']
    # Filtrar solo las columnas necesarias
    columnas_finales = [col for col in columnas_finales if col in datos_ordenados.columns]

    # Guardado de resultados
    try:
        datos_ordenados[columnas_finales].to_csv(archivo_salida, index=False)
        print(f"\nDatos ordenados guardados en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo {archivo_salida}: {e}")
        return

    print(f"\nTiempo total (Procesamiento + Ordenamiento): {tiempo_total:.2f} ms")

    #Imprimir los primeros 20 elementos
    print("\nTop 20 restaurantes ordenados por puntuación total:")
    print(datos_ordenados[columnas_finales].head(20).to_string(index=False))

    print("Programa finalizado.")


if __name__ == "__main__":
    mult.freeze_support()
    main()