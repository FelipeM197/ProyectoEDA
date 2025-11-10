import pandas as pd
import locale
import os

# Se usa locale para usar el punto decimal como en EE.UU.
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Fallback

# Constante m
m = 100.0

def main():
    # Archivos en una variable
    archivo_original = "yelp_database.csv"

    # Validacion de entrada del archivo
    if not os.path.exists(archivo_original):
        print(f"El archivo {archivo_original} no existe.")
        return
    
    # Leer el archivo CSV original con pandas
    datos = pd.read_csv(archivo_original)

    if datos.empty:
        print("El archivo de datos está vacío o no se pudo leer.")
        return
    
    print("Calculando puntuaciones y limpiando datos...")
    calcular_puntuacion(datos)

def calcular_puntuacion(datos):
    archivo_limpio = "datos_limpios.csv"
    
    # Calcular puntuaciones y limpiar datos
    for col in datos.select_dtypes(include=['object']).columns:
        # Evitar advertencias de pandas sobre regex en replace
        try:
            datos[col] = datos[col].astype(str).str.replace('"', '', regex=False).str.strip()
        except TypeError:
            # Compatibilidad con versiones antiguas de pandas que no soportan regex kwarg
            datos[col] = datos[col].astype(str).str.replace('"', '').str.strip()

    # Convertir rating y num_reviews (posiciones 5 y 6 en el archivo original) a numérico
    datos['rating'] = pd.to_numeric(datos['rating'], errors='coerce')
    datos['num_reviews'] = pd.to_numeric(datos['num_reviews'], errors='coerce')

    # Eliminamos las filas con valores nulos
    datos = datos.dropna(subset=['rating', 'num_reviews'])

    # Calcular la puntuación ajustada promedio simple
    C = datos['rating'].mean() if not datos['rating'].empty else 0

    #Imprimir el valor de C para verificación
    print(f"Puntuación media global C: {C:.4f}")

    #Calcular la puntuacion de confianza para cada restaurante
    #C = Suma de Raing / Total de filas
    def calcular_puntuacion_row(row):
        R = row['rating']
        v = row['num_reviews']
        #Verificar que (v + m) no sea cero para evitar division por cero
        if (v + m) != 0:
            puntuacion = (v / (v + m)) * R + (m / (v + m)) * C
        else:
            puntuacion = 0    
        return round(puntuacion, 2)
    
    # Crear una nueva columna 'puntuacion' aplicando la función (sin argumentos inválidos)
    datos['puntuacion'] = datos.apply(calcular_puntuacion_row, axis=1)
    
    #Renombrar las columnas al formato solicitado
    datos.rename(columns={
        'organization': 'Organization', 
        'rating': 'Rating', 
        'num_reviews': 'NumberReview',
        'puntuacion': 'PuntuacionConfianza'
    }, inplace=True, errors='ignore')

    # Seleccionar solo las columnas necesarias para el archivo limpio, pero solo las que existan
    columnas_a_guardar = ['Organization', 'Rating', 'NumberReview', 'PuntuacionConfianza']
    columnas_existentes = [c for c in columnas_a_guardar if c in datos.columns]
    if not columnas_existentes:
        print("No se encontraron columnas válidas para guardar. Revisar nombres de columnas en el CSV de entrada.")
        return
    datos_finales = datos[columnas_existentes]

    # Guardar los datos limpios en un nuevo archivo CSV
    datos_finales.to_csv(archivo_limpio, index=False)
    print(f"Datos limpios guardados en {archivo_limpio}")

# Ejecutar el programa
if __name__ == "__main__":
    main()
