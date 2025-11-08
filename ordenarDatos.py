import pandas as pd
import locale
from copy import deepcopy
from Restaurante import Restaurante  # Importamos La clase Restaurante

# Configurar locale para punto decimal 
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

#  Ordenamos datos usando QuickSort y MergeSort basados en la puntuación total
# QuickSort
def quick_sort(lista, key=lambda x: x.rating):
    #Si la lista tiene 1 o menos elementos, ya está ordenada
    if len(lista) <= 1:
        return lista
    #Elegimos el pivote como el elemento medio
    pivote = lista[len(lista)//2]
    # Dividimos la lista en menores, iguales y mayores al pivote
    menores = [x for x in lista if key(x) < key(pivote)]
    iguales = [x for x in lista if key(x) == key(pivote)]
    mayores = [x for x in lista if key(x) > key(pivote)]
    # Ordenamos recursivamente y combinamos
    return quick_sort(menores, key) + iguales + quick_sort(mayores, key)

# MergeSort
def merge_sort(lista, key=lambda x: x.rating):
    # Si la lista tiene 1 o menos elementos, ya está ordenada
    if len(lista) <= 1:
        return lista
    # Dividimos la lista en dos mitades
    mitad = len(lista) // 2
    # Ordenamos recursivamente ambas mitades
    izquierda = merge_sort(lista[:mitad], key)
    derecha = merge_sort(lista[mitad:], key)
    # Combinamos las dos mitades ordenadas
    return merge(izquierda, derecha, key)
# Función para combinar dos listas ordenadas
def merge(izquierda, derecha, key):
    resultado = []
    i = j = 0
    # Recorremos ambas listas y añadimos el menor elemento a resultado
    while i < len(izquierda) and j < len(derecha):
        # Comparar usando la función key
        if key(izquierda[i]) <= key(derecha[j]):
            resultado.append(izquierda[i])
            i += 1
        else:
            resultado.append(derecha[j])
            j += 1
    # Añadir los elementos restantes
    resultado.extend(izquierda[i:])
    resultado.extend(derecha[j:])
    return resultado

# PROGRAMA
def main():
    archivo_entrada = "datos_limpios.csv"
    archivo_salida = "datos_ordenados.csv"

    print(f"Cargando datos desde: {archivo_entrada}")
    restaurantes = []

    # Leer archivo CSV
    datos = pd.read_csv(archivo_entrada)

    #Convertir en filas DataFrame a objetos Restaurante
    for _, fila in datos.iterrows():
        nombre = fila['Organization']
        rating = float(fila['Rating'])
        num_resenas = int(fila['NumberReview'])
        puntuacion_total = float(fila['PuntuacionConfianza'])
        restaurante = Restaurante(nombre, rating, num_resenas, puntuacion_total)
        restaurantes.append(restaurante)

    print(f"Se cargaron {len(restaurantes)} registros.\n")

    # Copias para comparar algoritmos
    lista_quick = deepcopy(restaurantes)
    lista_merge = deepcopy(restaurantes)

    print("Iniciando QuickSort...")
    lista_quick = quick_sort(lista_quick, key=lambda x: x.puntuacion_total)
    print("QuickSort completado.\n")

    print("Iniciando MergeSort...")

    lista_merge = merge_sort(lista_merge, key=lambda x: x.puntuacion_total)
    print("MergeSort completado.\n")

    # Guardar salida
    print(f"Escribiendo resultados en: {archivo_salida}")
    df_salida = pd.DataFrame([{
        'Organization': r.nombre,
        'Rating': r.rating,
        'NumberReview': r.num_resenas,
        'PuntuacionConfianza': r.puntuacion_total
    } for r in lista_quick])  # Usamos la lista ordenada por QuickSort

    print("Archivo creado")

if __name__ == "__main__":
    main()
