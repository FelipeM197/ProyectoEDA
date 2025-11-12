
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

## 1. Implementación en Python (Multiprocesamiento): Preparación de Datos

A diferencia de la **implementación monolítica en Java**, la **Parte 2 en Python** se dividió en **dos scripts** para separar las responsabilidades, siguiendo un **enfoque más modular**:


### `procesar_datos.py` (Script de Preparación)

- **Propósito:** Su única tarea es leer el archivo `yelp_database.csv` original, limpiarlo usando **Pandas**, y exportar un archivo CSV intermedio y limpio.  
- **Salida:** `datos_procesados_py.csv`


### `analizar_ordenamiento.py` (Script de Análisis)

- **Propósito:** Lee el archivo `datos_procesados_py.csv` (ya limpio), aplica la **Fórmula de Confianza**, y ejecuta los **algoritmos de ordenamiento en paralelo** para medir el rendimiento.


### Enfoque de Implementación: Pandas para Procesamiento Vectorizado

El primer script (`procesar_datos.py`) se encarga de la limpieza.

---

### 2.1. Enfoque: Pandas y Carga Selectiva

En lugar del *streaming* utilizado en Java, se usa la biblioteca **Pandas**.  
Para optimizar el uso de **memoria RAM** (que es el principal problema de Pandas), no se carga el archivo CSV completo, sino únicamente las **tres columnas esenciales** para el análisis de los datos:

```python
# Carga solo las 3 columnas necesarias, ahorrando RAM
columnas_a_usar = ['Organization', 'Rating', 'NumberReview']
datos = pd.read_csv(archivo_original, usecols=columnas_a_usar)
```

### Manejo de Datos "Sucios" con Pandas

Los mismos **desafíos de datos corruptos** de la Parte 1 se resolvieron usando las **funciones vectorizadas de Pandas**, que son el equivalente al `try-catch` de Java:

---

**Problema (Java)**
Datos no numéricos o columnas desplazadas que requerían un manejo manual mediante `try-catch`.

**Solución (Python)**
Se utiliza `pd.to_numeric` con el argumento `errors='coerce'`.  
Esta función transforma cualquier dato que no pueda convertir (por ejemplo, `" and Catering"`) en `NaN` (*Not a Number*).


```python
datos['Rating'] = pd.to_numeric(datos['Rating'], errors='coerce')
datos['NumberReview'] = pd.to_numeric(datos['NumberReview'], errors='coerce')
```

**Filtrado**: Finalmente, se eliminan todas las filas corruptas (NaN) con una sola línea, garantizando un dataset limpio

```python
datos = datos.dropna(subset=['Rating', 'NumberReview'])
```

El script guarda el resultado (`datos_procesados_py.csv`), que sirve como punto de entrada estandarizado para la fase de análisis.

## Fase 2: Análisis y Ordenamiento Paralelo (Script 2)

El segundo script (`analizar_ordenamiento.py`) carga los datos limpios y realiza el trabajo pesado.

---

### 3.1. Carga y Aplicación de la Fórmula

- **Carga:** El script lee `datos_procesados_py.csv` en un **DataFrame de Pandas**.  
- **Cálculo de C:** El *Rating Promedio Global* (**C**) se calcula de forma optimizada utilizando **Pandas**.

```python 
C = datos['Rating'].mean()
```
**Conversión de Estructura**

Para usar **algoritmos de ordenamiento clásicos**, el **DataFrame** se convierte en una **lista de diccionarios de Python**, una estructura más nativa y adecuada para este tipo de algoritmos.

```python
lista_restaurantes = datos.to_dict('records')
```
**Cálculo de Fórmula**

El script **itera sobre la lista** y aplica la **Fórmula de Confianza** a cada restaurante,  
guardando el resultado en una nueva clave llamada **`puntuacion_total`**.

```python
# Bucle que aplica la fórmula a la lista de diccionarios
for r in lista_restaurantes:
    R = r.get('Rating', 0)
    v = r.get('NumberReview', 0)
    # ... (manejo de tipos) ...
    if (v + m) != 0:
        r['puntuacion_total'] = (v / (v + m)) * R + (m / (v + m)) * C
    else:
        r['puntuacion_total'] = 0.0
```

### Librerías y Funciones Clave

Para lograr el **paralelismo**, se utilizaron las siguientes **librerías** y **funciones auxiliares**:

---

- **`multiprocessing` (Librería):**  
  Es el núcleo del paralelismo en Python. Permite crear un *Pool* de procesos (trabajadores) que se ejecutan en diferentes núcleos de CPU.

- **`math` (Librería):**  
  Se usa `math.ceil` para calcular el tamaño de los *chunks* (trozos) de datos de manera uniforme.

- **`fusionar_dos_listas(listaA, listaB)` (Función Auxiliar):**  
  Función manual crucial que toma dos listas ya ordenadas y las fusiona en una sola lista ordenada (en orden descendente).

- **`fusionar_multiples_listas(listas_ordenadas)` (Función Auxiliar):**  
  Implementa el paso de **reducción**.  
  Toma la lista de *N chunks* ordenados (provenientes de los procesos paralelos) y los fusiona secuencialmente usando `fusionar_dos_listas`.

## Estrategia de Multiprocesamiento: "Divide, Mapea, Reduce"

El núcleo del proyecto es la **implementación de ordenamiento paralelo**.  
Las funciones `quick_sort_paralelo` y `heap_sort_paralelo` implementan esta estrategia de **tres pasos**:

---

### División (*Divide*)

La lista principal de aproximadamente **1 millón de restaurantes** se divide en **N "chunks" (trozos)**,  
donde **N** es el número de núcleos de CPU disponibles (`mult.cpu_count()`).

```python
num_nucleos = max(1, mult.cpu_count())
tamano_trozo = math.ceil(n / num_nucleos)
trozos = [lista[i:i+tamano_trozo] for i in range(0, n, tamano_trozo)]
```

### Mapeo (*Map - Paralelo*)

Este es el paso que se ejecuta **en paralelo**.  
Se crea un **Pool de procesos** y se utiliza `pool.map()`.  
Esta función envía un *chunk* a cada núcleo de CPU disponible.

Cada núcleo ejecuta de forma **independiente y simultánea** el algoritmo de ordenamiento secuencial  
(ya sea `heap_sort` o `quick_sort`) sobre su propio *chunk*.

```python
with mult.Pool(processes=num_nucleos) as pool:
    print("Enviando trozos a los núcleos para ordenar (pool.map)...")
    
    # Cada núcleo ejecuta 'heap_sort' en su 'trozo'
    trozos_ordenados = pool.map(heap_sort, trozos)
```
## Detalle de los Algoritmos de Ordenamiento Implementados

---

### Algoritmo 1: `heap_sort(lista)`

- **Descripción:**  
  Implementación clásica de **HeapSort** con complejidad **O(n log n)**.

- **Lógica:**  
  Primero construye un **Min-Heap** (el elemento más pequeño en la raíz)  
  y luego extrae los elementos uno por uno para construir la lista ordenada.

- **Uso:**  
  Se ejecuta en **paralelo**, donde cada núcleo aplica `heap_sort` a su propio *chunk*.

  ```python
  def heap_sort_paralelo(lista):
    """
    Orquesta el ordenamiento HeapSort O(n log n) en paralelo.
    """
    print("Iniciando HeapSort Paralelo...")
    
    num_nucleos = mult.cpu_count()
    print(f"Usando {num_nucleos} núcleos de CPU...")
    
    n = len(lista)
    tamano_trozo = math.ceil(n / num_nucleos)
    
    trozos = [lista[i : i + tamano_trozo] for i in range(0, n, tamano_trozo)]
    print(f"Lista dividida en {len(trozos)} trozos de ~{tamano_trozo} elementos.")

    with mult.Pool(processes=num_nucleos) as pool:
        print("Enviando trozos a los núcleos para ordenar (pool.map)...")
        
        # Llama a la función secuencial 'heap_sort' en cada núcleo
        trozos_ordenados = pool.map(heap_sort, trozos)
        
        print("Ordenamiento de trozos completado. Fusionando resultados...")

    # Llama a la fusión (Reduce)
    lista_final_ordenada = fusionar_multiples_listas(trozos_ordenados)
    
    return lista_final_ordenada
  ```

---

### Algoritmo 2: `quick_sort(lista)` (*MergeSort Iterativo*)

- **Descripción:**  
  Aunque la función se llama `quick_sort`, la implementación corresponde a un  
  **MergeSort Iterativo (no recursivo)**.  
  Esto resulta conceptualmente ideal, ya que la **estrategia de paralelismo** también sigue un enfoque de **MergeSort**.

- **Lógica:**  
  No utiliza recursividad; en su lugar, emplea un bucle `while` que duplica el tamaño (`width`)  
  de las sublistas a fusionar hasta que toda la lista queda ordenada.

- **Rendimiento:**  
  Complejidad **O(n log n)**.

- **Uso:**  
  Es la alternativa a `heap_sort` que cada núcleo puede ejecutar en el paso de **Mapeo**.

```python
  def quick_sort_paralelo(lista):
    if not lista:
        return lista
    
    print("Iniciando QuickSort Paralelo...")
    num_nucleos = max(1, mult.cpu_count())
    print(f"Usando {num_nucleos} núcleos de CPU...")
    
    n = len(lista)
    tamano_trozo = math.ceil(n / num_nucleos)
    trozos = [lista[i:i+tamano_trozo] for i in range(0, n, tamano_trozo)]
    print(f"Lista dividida en {len(trozos)} trozos de ~{tamano_trozo} elementos.")
    
    with mult.Pool(processes=num_nucleos) as pool:
        print("Enviando trozos a los núcleos para ordenar (pool.map)...")
        
        # Llama a la función secuencial 'quick_sort' en cada núcleo
        trozos_ordenados = pool.map(quick_sort, trozos)
        
        print("Ordenamiento de trozos completado. Fusionando resultados...")
        
    # Llama a la fusión (Reduce)
    lista_final_ordenada = fusionar_multiples_listas(trozos_ordenados)
    return lista_final_ordenada
  ```


### Medición de Rendimiento

Para **cuantificar el rendimiento**, se utiliza la biblioteca `time`.  
Se registra:

- El tiempo inicial (`time_inicio`) justo antes de llamar a la función de ordenamiento  
  (por ejemplo, `quick_sort`), y  
- El tiempo final (`time_fin`) inmediatamente después de completarla.

---

Esto permite **aislar y medir exclusivamente el tiempo de cómputo** (*CPU-Bound*)  
del algoritmo de ordenamiento, que es la **métrica clave** para el análisis de la **Parte 2 (Multiprocesamiento)**.

---

### Resultado Final

El archivo resultante `datos_ordenados_py.csv` incluye la **posición (ranking)** final de cada restaurante.




