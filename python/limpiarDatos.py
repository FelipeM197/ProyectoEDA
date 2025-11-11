import pandas as pd
import locale
import os

# Se usa locale para usar el punto decimal como en EE.UU.
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Fallback

def main():
    # Archivos en una variable
    archivo_original = "yelp_database.csv"
    archivo_limpio = "datos_procesados_py.csv" 

    # Validacion de entrada del archivo
    if not os.path.exists(archivo_original):
        print(f"El archivo {archivo_original} no existe.")
        return
    
    # (Usamos los nombres correctos del CSV original)
    columnas_a_usar = ['Organization', 'Rating', 'NumberReview']
    
    print(f"Leyendo {archivo_original} (solo 3 columnas)...")
    # Leer el archivo CSV original con pandas, usando solo las columnas necesarias
    try:
        datos = pd.read_csv(archivo_original, usecols=columnas_a_usar)
    except ValueError as e:
        print(f"Error: No se encontraron las columnas requeridas. Revisa los nombres.")
        print(f"Detalle: {e}")
        return

    if datos.empty:
        print("El archivo de datos está vacío o no se pudo leer.")
        return
    
    print("Limpiando datos...")
    
    # (Llamamos a una función que SÓLO limpia)
    datos_limpios = limpiar_columnas(datos)

    # Guardar los datos limpios en un nuevo archivo CSV
    datos_limpios.to_csv(archivo_limpio, index=False)
    print(f"Datos limpios (3 columnas) guardados en {archivo_limpio}")


def limpiar_columnas(datos):
    """
    Toma un DataFrame de pandas y limpia las columnas
    'Organization', 'Rating', y 'NumberReview'.
    """
    
    # Limpiar columna 'Organization' (tipo objeto/string)
    # Evitar advertencias de pandas sobre regex en replace
    try:
        datos['Organization'] = datos['Organization'].astype(str).str.replace('"', '', regex=False).str.strip()
    except TypeError:
        # Compatibilidad con versiones antiguas de pandas que no soportan regex kwarg
        datos['Organization'] = datos['Organization'].astype(str).str.replace('"', '').str.strip()

    # Convertir rating y num_reviews a numérico
    # (Usamos los nombres correctos con Mayúscula)
    datos['Rating'] = pd.to_numeric(datos['Rating'], errors='coerce')
    datos['NumberReview'] = pd.to_numeric(datos['NumberReview'], errors='coerce')

    # Eliminamos las filas con valores nulos (donde 'coerce' falló)
    datos = datos.dropna(subset=['Rating', 'NumberReview'])

    # CORRECCIÓN: Convertimos 'NumberReview' a entero (opcional, pero limpio)
    datos['NumberReview'] = datos['NumberReview'].astype(int)

    return datos

# (La usaremos en el próximo script de análisis)


# Ejecutar el programa
if __name__ == "__main__":
    main()