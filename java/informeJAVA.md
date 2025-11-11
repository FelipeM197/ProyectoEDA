
# Informe del Proyecto EDA: Procesamiento y Ordenamiento (Parte 1)

## 1\. Implementación Java (Single-Core): Preparación de Datos

El primer componente del proyecto consiste en procesar un dataset de gran tamaño (`yelp_database.csv`) utilizando Java en un solo núcleo. El objetivo no es solo leer los datos, sino también limpiarlos, transformarlos y prepararlos para la fase de análisis de algoritmos.

### Descripción de la Clase `Restaurante`

Para modelar los datos en el programa de análisis (`AnalisisOrdenamiento.java`), se definió una clase `Restaurante`. Esta clase actúa como un Objeto Simple de Java (POJO) o "molde" que encapsula los atributos de cada registro que nos interesa:

```java
public class Restaurante {
    String nombreREstaurante;
    double rating; 
    int numeroResenas;
    double puntuacionTotal; // Almacena el resultado de la fórmula

    // Constructor para inicializar el objeto
    public Restaurante(String nombre, double rating, int resenas, double puntuacion) {
        this.nombreREstaurante = nombre;
        this.rating = rating;
        this.numeroResenas = resenas;
        this.puntuacionTotal = puntuacion;
    }

    // Método de utilidad para depuración
    @Override
    public String toString() {
        return String.format("Restaurante[%s, Puntuacion: %.4f]", 
                             nombreREstaurante, puntuacionTotal);
    }
}
```

-----

## 2\. Desafíos de Implementación y Soluciones

Procesar un dataset "sucio" de 1 millón de filas presentó varios desafíos técnicos que requirieron soluciones específicas para garantizar la eficiencia y la integridad de los datos.

### Optimización de Memoria: Enfoque de Streaming (I/O)

Al procesar el archivo original "sucio" (`limpiarDatos.java`), se descartó el enfoque tradicional de leer todas las líneas en un `ArrayList`.

  * **Problema:** Cargar 1 millón de objetos Java en la memoria RAM (Heap) tiene un consumo muy alto. Cada objeto `String` y `Double`, sumado al *overhead* del propio objeto `Restaurante`, podría consumir varios gigabytes de RAM, llevando a un error `java.lang.OutOfMemoryError`.
  * **Solución (Enfoque Óptimo):** Se implementó un enfoque de "streaming" (flujo de datos). El programa utiliza un `BufferedReader` para leer una sola línea a la vez y un `BufferedWriter` para escribir la línea procesada de inmediato.
      * La memoria utilizada es mínima y constante, ya que solo existe una línea en la RAM en un momento dado.
      * Esto nos permite procesar archivos de tamaño virtualmente ilimitado (1 millón o 1 billón de filas) sin agotar los recursos del sistema.

### Manejo de Datos Corruptos: La Estrategia del Doble `try-catch`

El dataset original estaba "sucio" y el método `linea.split(",")` es muy frágil.

  * **Problema:** Se encontraron dos tipos de corrupción que lanzaban `NumberFormatException`:
    1.  **Datos No Numéricos:** Campos que debían ser números contenían texto (ej. `" and Catering""`).
    2.  **Desplazamiento de Columnas:** Comas (`.`) dentro del nombre de un restaurante (ej. `"Zaxby's, Chicken & Wings"`) engañaban al `split()`, provocando que el `Rating` (ej. `"3.5"`) se leyera en la columna de `NumberReview`, lo que causaba un error al intentar `Integer.parseInt("3.5")`.
  * **Solución:** Se implementó una estrategia de "doble `try-catch`" para hacer el programa robusto.
    1.  **`try-catch` en `calcularRatingPromedio`:** Permite que el cálculo del promedio `C` ignore las líneas corruptas sin detener el programa.
    2.  **`try-catch` en `main`:** Protege el bucle principal de escritura. Si una línea está desplazada o corrupta, se captura la excepción, se imprime un error en la consola y el programa continúa con la siguiente línea, asegurando que solo los datos válidos se escriban en el archivo limpio.

### Desafío de Configuración Regional (Locale) y `.trim()`

  * **Problema 1 (Locale):** El programa fallaba al leer números válidos como `"4.5"`. Esto se debía a un conflicto de Configuración Regional (Locale): el `.csv` usaba puntos (`.`) como separador decimal, pero el sistema operativo (y Java por defecto) esperaba comas (`,`). Irónicamente, al escribir los datos, `String.format()` generaba comas (ej. `"2,8290"`), corrompiendo el `.csv` de salida.

  * **Solución 1:** Se forzó a Java a usar el estándar de EE.UU. (que usa puntos) al inicio del `main`:

    ```java
    Locale.setDefault(Locale.US);
    ```

  * **Problema 2 (Datos "sucios"):** Incluso con el Locale corregido, el programa fallaba con entradas como `""4.5""` (con comillas) o `" 12 "` (con espacios).

  * **Solución 2:** Se "sanitizaron" (limpiaron) los strings antes de convertirlos, usando dos métodos encadenados:

    ```java
    // Ej: partes[5] es "\" 4.5 \""
    String ratingLimpio = partes[5].replace("\"", "").trim();
    // 1. .replace("\"", "") -> " 4.5 " (quita comillas)
    // 2. .trim()           -> "4.5" (quita espacios)
    double R = Double.parseDouble(ratingLimpio); // Funciona
    ```

-----

## 3\. Lógica del Proyecto: La Fórmula de Confianza

Para que la ordenación fuera significativa, no bastaba con usar el `Rating` simple. Un restaurante con 1 reseña de 5 estrellas no es "mejor" que uno con 1000 reseñas de 4.9 estrellas.

Se implementó una **fórmula de "Puntuación de Confianza"** (un promedio ponderado de estilo Bayesiano) para crear un ranking más justo.

**La Fórmula:**
$$Puntuación = \left( \frac{v}{v+m} \times R \right) + \left( \frac{m}{v+m} \times C \right)$$

**Descripción Detallada de los Componentes:**

  * **`R`** = `Rating`. Es la calificación individual del restaurante (ej. 4.9).
  * **`v`** = `NumberReview`. Es el número de reseñas (votos) de *ese* restaurante (ej. 1000).
  * **`C`** = Rating Promedio Global. Es la calificación promedio de *todo* el dataset (ej. `2.7821...`). Este valor lo calculamos en la "Pasada 1" de nuestro programa `limpiarDatos.java`.
  * **`m`** = Mínimo de Reseñas. Es una constante que nosotros definimos (ej. `100`). Actúa como una "perilla de confianza": es el número de reseñas que consideramos necesario para que un rating empiece a ser estadísticamente fiable.

**Cómo Funciona la Lógica:**

La fórmula es una "lucha de poder" entre el rating individual (`R`) y el promedio global (`C`). El número de reseñas (`v`) decide quién gana.

  * **Caso 1: Restaurante Popular (muchas reseñas, `v >> m`)**

      * `v = 1000`, `R = 4.9`.
      * La primera parte de la fórmula $\left( \frac{v}{v+m} \right)$ será $\left( \frac{1000}{1100} \right) \approx 0.91$ (91%).
      * La segunda parte $\left( \frac{m}{v+m} \right)$ será $\left( \frac{100}{1100} \right) \approx 0.09$ (9%).
      * `Puntuación = (0.91 * 4.9) + (0.09 * 2.78)`
      * **Resultado:** La puntuación final será muy cercana a su rating real de 4.9. **Lógica:** "Confiamos en este rating porque tiene muchas reseñas".

  * **Caso 2: Restaurante Nuevo (pocas reseñas, `v << m`)**

      * `v = 1`, `R = 5.0`.
      * La primera parte $\left( \frac{v}{v+m} \right)$ será $\left( \frac{1}{101} \right) \approx 0.01$ (1%).
      * La segunda parte $\left( \frac{m}{v+m} \right)$ será $\left( \frac{100}{101} \right) \approx 0.99$ (99%).
      * `Puntuación = (0.01 * 5.0) + (0.99 * 2.78)`
      * **Resultado:** La puntuación final será "arrastrada" fuertemente hacia el promedio `C` de 2.78. **Lógica:** "No confiamos en este 5.0; es estadísticamente irrelevante. Lo trataremos como si fuera 'promedio' hasta que tenga más reseñas".

Esta `PuntuacionConfianza` es la columna que usaremos para nuestro análisis de algoritmos de ordenamiento.

-----`
# Multiprocesamiento y Ordenamiento (Parte 2)

## 1. Implementación en Python (Single-Core): Preparación de Datos

La segunda parte del proyecto consiste en replicar la lógica de procesamiento de datos de Java a Python. El objetivo es crear una base de datos limpia idéntica que sirva como punto de entrada para el análisis de algoritmos de ordenamiento.

Para esta implementación, se optó por utilizar la biblioteca **Pandas**, un estándar de facto en el ecosistema de Python para la manipulación y análisis de datos.

---

### Enfoque de Implementación: Pandas para Procesamiento Vectorizado

A diferencia del enfoque de "streaming" (línea por línea) implementado en Java para optimizar el uso de memoria RAM, el enfoque de Python utiliza la biblioteca Pandas, que carga el dataset completo en memoria en una estructura de datos llamada `DataFrame`.

- **Diferencia Clave:** Mientras que la solución de Java (`BufferedReader`) se diseñó para un consumo de memoria mínimo y constante (evitando `OutOfMemoryError`), la solución de Python (`pd.read_csv`) carga todo el millón de filas en la RAM.  
- **Justificación:** Se asume un entorno con suficiente RAM. A cambio de un mayor consumo de memoria, Pandas ofrece una API de "procesamiento vectorizado" que simplifica enormemente las operaciones de limpieza y transformación de datos, permitiendo aplicar cambios a columnas enteras de una sola vez.


### Manejo de Datos "Sucios" con Pandas

Los mismos desafíos de datos corruptos encontrados en la Parte 1 fueron resueltos usando funciones optimizadas de Pandas, que reemplazan los bucles `try-catch` manuales de Java.

- **Problema (Java):** Datos con comillas (`""4.5""`) y espacios (`" 12 "`) que requerían `.replace("\"", "").trim()` por cada línea.

- **Solución (Python):** Se aplicó una "limpieza vectorizada" a todas las columnas de texto simultáneamente:

```python
# Limpia comillas y espacios en todas las columnas de texto
datos[col] = datos[col].astype(str).str.replace('"', '', regex=False).str.strip()
```

- **Problema (Java)**
Datos no numéricos (`" and Catering"`) y columnas desplazadas (`"3.5"` en la columna de tipo *Integer*) requerían un **doble `try-catch`** para evitar el `NumberFormatException`.

- **Solución (Python**)
**Pandas** maneja esto de forma más robusta.  
Se utiliza `pd.to_numeric` con el argumento `errors='coerce'`.  
Esta función intenta convertir la columna, y cualquier valor que falle (como `" and Catering"`) se transforma automáticamente en `NaN` (*Not a Number*).

```python
# Convierte a número, los errores se marcan como NaN
datos['rating'] = pd.to_numeric(datos['rating'], errors='coerce')
datos['num_reviews'] = pd.to_numeric(datos['num_reviews'], errors='coerce')

# Elimina todas las filas que fallaron la conversión
datos = datos.dropna(subset=['rating', 'num_reviews'])
```

Este enfoque elimina eficazmente todas las líneas corruptas o desplazadas sin necesidad de bloques `try-except` explícitos por cada fila.

### Lógica del Proyecto: Replicando la Fórmula en Pandas

La **fórmula de "Puntuación de Confianza"** sigue siendo el núcleo del proyecto.

### Fórmula 

\[
Puntuación = \left(\frac{v}{v+m} \times R\right) + \left(\frac{m}{v+m} \times C\right)
\]


### Cálculo de C (Promedio Global)

En lugar de una "Pasada 1" manual, **Pandas** calcula el promedio `C` de la columna `rating` (ya limpia) con un simple método:

```python
C = datos['rating'].mean()
```

### Aplicación de la Fórmula

La fórmula se aplica a cada fila del **DataFrame** usando el método `.apply(axis=1)`.  
Este método itera sobre cada fila (`row`) y ejecuta la función `calcular_puntuacion_row`,  
la cual contiene la **lógica bayesiana idéntica** a la versión implementada en **Java**.

```python
def calcular_puntuacion_row(row):
    R = row['rating']
    v = row['num_reviews']
    if (v + m) != 0:
        puntuacion = (v / (v + m)) * R + (m / (v + m)) * C
    else:
        puntuacion = 0
    return round(puntuacion, 2)

# Crea la nueva columna 'puntuacion' aplicando la función
datos['puntuacion'] = datos.apply(calcular_puntuacion_row, axis=1)
```
El **DataFrame resultante**, que contiene las columnas:

- `Organization`
- `Rating`
- `NumberReview`
- `PuntuacionConfianza`

se guarda en el archivo `datos_limpios.csv`.  
Este archivo sirve como **entrada estandarizada** para la fase de **análisis de algoritmos**.

---

## 2 Análisis de Algoritmos de Ordenamiento (Single-Core)

Esta fase del proyecto (correspondiente a **`AnalisisOrdenamiento.py`**) se centra en **cargar los datos limpios** y **medir el rendimiento** de diferentes algoritmos de ordenamiento.

---

### Carga de Datos y Estructura

El script `datos_limpios.csv` se carga nuevamente usando **Pandas**, pero para la fase de ordenamiento se transforma la estructura de datos.

- `datos.to_dict('records')`: El DataFrame de Pandas se convierte en una lista estándar de diccionarios de Python.

- **Motivo**: Los algoritmos de ordenamiento clásicos (como Bubble Sort y QuickSort) están diseñados para operar sobre listas en memoria, no sobre DataFrames.
Cada diccionario de la lista representa un restaurante, por ejemplo:
 ```python
 {'Organization': 'Taco Bell', 'Rating': 3.5, 'NumReviews': 120, 'Puntuacion': 4.2}
```
### Implementación y Comparativa de Algoritmos

El script está diseñado para **comparar el rendimiento** de diferentes algoritmos al ordenar la lista de diccionarios por la variable `puntuacion_total` (calculada en el script).

---

### 🔹 Bubble Sort (`buble_sort`)

Se implementa este **algoritmo clásico**.  
Aunque es conocido por su ineficiencia en *datasets* grandes (complejidad \( O(n^2) \)),  
sirve como una **línea base fundamental** para la comparación.

---

### 🔹 QuickSort (`platzhalter`)

El menú incluye una opción para **QuickSort**, un algoritmo mucho más eficiente del tipo **"Divide y Vencerás"**,  
con una **complejidad promedio** de \( O(n \log n) \).  
Sirve como una **comparativa de rendimiento más realista** frente a Bubble Sort.

---

### Medición de Rendimiento

Para **cuantificar el rendimiento**, se utiliza la biblioteca `time`.  
Se registra:

- El tiempo inicial (`time_inicio`) justo antes de llamar a la función de ordenamiento  
  (por ejemplo, `buble_sort`), y  
- El tiempo final (`time_fin`) inmediatamente después de completarla.

---

Esto permite **aislar y medir exclusivamente el tiempo de cómputo** (*CPU-Bound*)  
del algoritmo de ordenamiento, que es la **métrica clave** para el análisis de la **Parte 2**.

---

### Resultado Final

El archivo resultante `datos_ordenados.csv` incluye la **posición (ranking)** final de cada restaurante.




