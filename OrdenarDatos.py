import pandas as pd
import locale
import time
import os
import sys
import random
import math
import multiprocessing as mult

m = 100.0  # Factor de normalización

# Aumentamos el límite de recursión para QuickSort con 1 millón de datos
sys.setrecursionlimit(2000000)

# Configuración regional para el formato de números, ya que o si no los calculos ser harán con comas en vez de puntos
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

# Ordenamos de forma descendente por rating usando QuickSort
def quick_sort(lista):
    n = len(lista)
    if n <= 1:
        return lista

    def merge(left, right):
        i = 0
        j = 0
        merged = []
        while i < len(left) and j < len(right):
            if left[i].get('Rating', 0) > right[j].get('Rating', 0):
                merged.append(left[i]); i += 1
            else:
                merged.append(right[j]); j += 1
        # anexar restos
        while i < len(left):
            merged.append(left[i]); i += 1
        while j < len(right):
            merged.append(right[j]); j += 1
        return merged

    width = 1
    # Usamos una lista temporal para construir las fusiones en cada paso
    result = lista[:]  # copia superficial de referencias a diccionarios
    while width < n:
        for i in range(0, n, 2 * width):
            left = result[i: i + width]
            right = result[i + width: i + 2 * width]
            merged = merge(left, right)
            # escribir vuelta en result
            result[i: i + len(merged)] = merged
        width *= 2

    return result

def quick_sort_paralelo(lista):
    if not lista:
        return lista
    
    # Imprimimos en el proceso 'main' (seguro)
    print("Iniciando QuickSort Paralelo...")
    num_nucleos = max(1, mult.cpu_count())
    print(f"Usando {num_nucleos} núcleos de CPU...")
    
    n = len(lista)
    tamano_trozo = math.ceil(n / num_nucleos)
    trozos = [lista[i:i+tamano_trozo] for i in range(0, n, tamano_trozo)]
    print(f"Lista dividida en {len(trozos)} trozos de ~{tamano_trozo} elementos.")
    
    with mult.Pool(processes=num_nucleos) as pool:
        print("Enviando trozos a los núcleos para ordenar (pool.map)...")
        
        # Ahora llamamos a _quick_sort (nombre original sin 'silencioso')
        trozos_ordenados = pool.map(quick_sort, trozos)
        
        print("Ordenamiento de trozos completado. Fusionando resultados...")
        
    lista_final_ordenada = fusionar_multiples_listas(trozos_ordenados)
    return lista_final_ordenada

# Agregar de nuevo las funciones de fusión que faltaban
def fusionar_multiples_listas(listas_ordenadas):
    if not listas_ordenadas:
        return []

    # Empezamos con la primera lista ordenada
    lista_fusionada = listas_ordenadas[0]
    
    # Iteramos sobre el RESTO de las listas (del 1 en adelante)
    for i in range(1, len(listas_ordenadas)):
        print(f"Fusionando trozo {i+1} de {len(listas_ordenadas)}...")
        # Fusionamos el resultado acumulado con el siguiente trozo
        lista_fusionada = fusionar_dos_listas(lista_fusionada, listas_ordenadas[i])
        
    return lista_fusionada

def fusionar_dos_listas(listaA, listaB):
    """
    Implementación "simple" (manual) de la fusión de dos listas ordenadas.
    (Ordena DESCENDENTEMENTE)
    """
    lista_fusionada = []
    
    # Punteros (índices) para la Lista A y la Lista B
    i = 0
    j = 0
    
    # Recorremos ambas listas mientras haya elementos en las dos
    while i < len(listaA) and j < len(listaB):
        # (Orden DESCENDENTE)
        if listaA[i]['Rating'] > listaB[j]['Rating']:
            lista_fusionada.append(listaA[i])
            i += 1 # Avanzamos el puntero A
        else:
            lista_fusionada.append(listaB[j])
            j += 1 # Avanzamos el puntero B
            
    # Cuando una lista se acaba, añadimos lo que queda de la otra
    while i < len(listaA):
        lista_fusionada.append(listaA[i])
        i += 1
    while j < len(listaB):
        lista_fusionada.append(listaB[j])
        j += 1
        
    return lista_fusionada


def heap_sort(lista):
    n = len(lista)
    # Construir min-heap
    for i in range(n // 2 - 1, -1, -1):
        _heapify_worker(lista, n, i)
    # Extraer elementos
    for i in range(n - 1, 0, -1):
        lista[0], lista[i] = lista[i], lista[0]
        _heapify_worker(lista, i, 0)
    return lista

def _heapify_worker(lista, n, i):
    menor = i
    izq = 2 * i + 1
    der = 2 * i + 2

    if izq < n and lista[izq]['Rating'] < lista[menor]['Rating']:
        menor = izq
    if der < n and lista[der]['Rating'] < lista[menor]['Rating']:
        menor = der

    if menor != i:
        lista[i], lista[menor] = lista[menor], lista[i]
        _heapify_worker(lista, n, menor)

def heap_sort_paralelo(lista):
    """
    Orquesta el ordenamiento HeapSort O(n log n) en paralelo.
    """
    print("Iniciando HeapSort Paralelo...")
    
    # Determina el número de núcleos a usar
    num_nucleos = mult.cpu_count()
    print(f"Usando {num_nucleos} núcleos de CPU...")
    
    # Divide la lista en 'N' trozos (chunks)
    n = len(lista)
    tamano_trozo = math.ceil(n / num_nucleos)
    
    trozos = [lista[i : i + tamano_trozo] for i in range(0, n, tamano_trozo)]
    print(f"Lista dividida en {len(trozos)} trozos de ~{tamano_trozo} elementos.")

    # Crea el Pool de Trabajadores
    with mult.Pool(processes=num_nucleos) as pool:
        
        print("Enviando trozos a los núcleos para ordenar (pool.map)...")
        
        # Usamos la función _heap_sort (sin 'silencioso')
        trozos_ordenados = pool.map(heap_sort, trozos)
        
        print("Ordenamiento de trozos completado. Fusionando resultados...")

    # Fusiona los trozos ordenados
    lista_final_ordenada = fusionar_multiples_listas(trozos_ordenados)
    
    return lista_final_ordenada

def imprimir_lista(lista, n=20):
    """Función para imprimir los primeros 'n' elementos mostrando solo nombre y rating"""
    print(f"Mostrando los primeros {n} elementos de la lista:")
    for i, item in enumerate(lista[:n]):
        nombre = item.get('Organization') or item.get('Name') or 'N/A'
        rating = item.get('Rating', 'N/A')
        try:
            rating_val = float(rating)
            rating_str = f"{rating_val:.2f}"
        except Exception:
            rating_str = str(rating)
        print(f"{i + 1}. {nombre} — Rating: {rating_str}")
        

def main():
    """Función principal del programa"""
    # Definición de archivos de entrada y salida
    archivo_entrada = "datos_procesados_py.csv"
    archivo_salida = "datos_ordenados_py.csv"

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
    print("Calculando C (Promedio Global) desde los datos...")
    C = datos['Rating'].mean()
    print(f"C (Promedio Global) calculado: {C:.4f}")

    # Conversión de DataFrame a lista de diccionarios
    lista_restaurantes = datos.to_dict('records')
    print(f"Carga completada. Procesando {len(lista_restaurantes)} registros...")

    print("\nMenu de opciones de ordenamiento (Paralelo):")
    print("1. QuickSort (Paralelo - Múltiples Núcleos)")
    print("2. HeapSort (Paralelo - Múltiples Núcleos)")

    try:
        opcion = int(input("Seleccione una opción (1-2): "))
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
        return

    ### El tiempo total incluye el cálculo de la fórmula + el ordenamiento
    print("Iniciando procesamiento y ordenamiento...")
    tiempo_inicio = time.time()

    # Cálculo de puntuación de confianza para cada restaurante
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

    # --- SELECCIÓN ACTUALIZADA ---
    if opcion == 1:
        print("Ordenando con QuickSort (Paralelo)...")
        lista_restaurantes = quick_sort_paralelo(lista_restaurantes)
    elif opcion == 2:
        print("Ordenando con HeapSort (Paralelo)...")
        lista_restaurantes = heap_sort_paralelo(lista_restaurantes)
    else:
        print("Opción inválida. Saliendo del programa.")
        return

    # Cálculo del tiempo de ejecución
    tiempo_fin = time.time()
    tiempo_total = (tiempo_fin - tiempo_inicio) * 1000.0

    # Preparación de datos para exportación
    datos_ordenados = pd.DataFrame(lista_restaurantes)
    datos_ordenados.insert(0, 'Posicion', range(1, len(datos_ordenados) + 1))

    # Selección y renombre de columnas
    columnas_finales = ['Posicion', 'Organization', 'Rating', 'NumberReview', 'puntuacion_total']
    datos_ordenados = datos_ordenados[columnas_finales]
    # Guardado de resultados
    try:
        datos_ordenados.to_csv(archivo_salida, index=False)
        print(f"\nDatos ordenados guardados en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo {archivo_salida}: {e}")
        return

    print(f"\nTiempo total (Procesamiento + Ordenamiento): {tiempo_total:.2f} ms")

    #Imprimir los primeros 20 elementos
    imprimir_lista(lista_restaurantes, n=20)
    print("Programa finalizado.")


if __name__ == "__main__":
    mult.freeze_support()
    main()