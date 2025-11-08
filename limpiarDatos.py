import pandas as pd
import locale
import os

# Se usa locale para usar el punto decimal como en EE.UU.
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')  # Fallback

# Constante m
m = 50

def main():
    # Archivos en una variable
    archivo_original = "yelp_database.csv"
    archivo_limpio = "datos_limpios.csv"


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

    # Calcular puntuaciones y limpiar datos
    # Quitamos comillas y espacios de todas las columnas de texto
    for col in datos.select_dtypes(include=['object']).columns:
        datos[col] = datos[col].astype(str).str.replace('"', '').str.strip()

    # Convertir rating y num_reviews (posiciones 5 y 6 en el archivo original) a numérico
    datos['rating'] = pd.to_numeric(datos['rating'], errors='coerce')
    datos['num_reviews'] = pd.to_numeric(datos['num_reviews'], errors='coerce')

    # Eliminamos las filas con valores nulos
    datos = datos.dropna(subset=['rating', 'num_reviews'])

    # Calcular la puntuación ajustada
    suma = (datos['Rating'] * datos['NumberReview']).sum()
    contador = datos['NumberReview'].sum()
    C = suma / contador if contador > 0 else 0.0

    print(f"Puntuación media global C: {C:.4f}")
    print("Generando el archivo limpio...")

    #Calcular la puntuacion de confianza para cada restaurante
    def calcular_puntuacion(row):
        R = row['rating']
        v = row['num_reviews']
        #Verificar que (v + m) no sea cero para evitar division por cero
        if (v + m) != 0:
            puntuacion = (v / (v + m)) * R + (m / (v + m)) * C
        else:
            puntuacion = 0    
        return round(puntuacion, 2)
    
    # Crear una nueva columna 'puntuacion' aplicando la función
    datos['puntuacion'] = datos.apply(calcular_puntuacion, axis=1)
    # Guardar el DataFrame limpio en un nuevo archivo CSV
    datos.to_csv(archivo_limpio, index=False)
    print(f"Archivo limpio generado: {archivo_limpio}")

if __name__ == "__main__":
    main()
