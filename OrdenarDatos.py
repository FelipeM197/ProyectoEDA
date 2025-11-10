import pandas as pd
import locale
import time
import os
from Restaurante import Restaurante

# Constantes para el cálculo de puntuación de confianza
m = 100.0  # Factor de normalización
C = 3.0    # Puntuación media de referencia

# Configuración regional para el formato de números
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

def buble_sort(lista):
    """
    Implementa el algoritmo Bubble Sort para ordenar restaurantes por puntuación
    Args:
        lista: Lista de diccionarios con información de restaurantes
    Returns:
        Lista ordenada de restaurantes
    """
    n = len(lista)
    for i in range(n):
        intercambio = False
        for j in range(0, n-i-1):
            if lista[j]['puntuacion_total'] > lista[j+1]['puntuacion_total']:
                lista[j], lista[j+1] = lista[j+1], lista[j]
                intercambio = True
        
        if not intercambio:
            print(f"Burble Sort: {i+1} iteraciones")
            break
    return lista

def main():
    """Función principal del programa"""
    # Definición de archivos de entrada y salida
    archivo_entrada = "datos_limpios.csv"
    archivo_salida = "datos_ordenados.csv"

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

    # Conversión de DataFrame a lista de diccionarios
    lista_restaurantes = datos.to_dict('records')
    print(f"Carga completada. Procesando {len(lista_restaurantes)} registros...")

    # Menú de selección de algoritmo
    print("\nMenu de opciones de ordenamiento:")
    print("1. QuickSort por Puntuacion de Confianza")
    print("2. BubbleSort por Puntuacion de Confianza")

    try:
        opcion = int(input("Seleccione una opción (1-2): "))
    except ValueError:
        print("Entrada inválida. Por favor, ingrese un número.")
        return
    
    tiempo_inicio = time.time()

    # Cálculo de puntuación de confianza para cada restaurante
    for r in lista_restaurantes:
        R = r['Rating']
        v = r['NumberReview']
        r['puntuacion_total'] = (v / (v + m)) * R + (m / (v + m)) * C

    # Selección y ejecución del algoritmo de ordenamiento
    if opcion == 1:
        print("Ordenando con QuickSort por Puntuacion de Confianza...")
        # Aquí iría la implementación de QuickSort
        print("QuickSort no implementado aún")
        return
    elif opcion == 2:
        print("Ordenando con BubbleSort por Puntuacion de Confianza...")
        lista_restaurantes = buble_sort(lista_restaurantes)
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

    datos_ordenados.rename(columns={
        'Organization': 'Restaurant', 
        'NumberReview': 'Number of Reviews'
    }, inplace=True)

    # Guardado de resultados
    try:
        datos_ordenados.to_csv(archivo_salida, index=False)
        print(f"Datos ordenados guardados en: {archivo_salida}")
    except Exception as e:
        print(f"Error al guardar el archivo {archivo_salida}: {e}")
        return

    print(f"Tiempo total de ordenamiento: {tiempo_total:.2f} ms")
    print("Programa finalizado.")

if __name__ == "__main__":
    main()
