# Informe proyecto Final EDA I

Integrantes: Aidan Carrasco, Deysi Guachamín, Felipe Merino

## 1. Introducción

**Objetivo del Proyecto:**

- Aprender a manejar datos masivos
- Profundizar en la lógica de algoritmos
- Realizar un estudio sobre la base de datos elegida
- Descubrir cuáles son los restaurantes mejor ranqueados

**Caso de Estudio:** Se ha elegido un dataset obtenido del sitio "Yelp", una plataforma digital masiva, principalmente utilizada en países anglosajones (Estados Unidos, Canadá, etc.). Se basa en el "crowdsourcing" (colaboración abierta), es decir, es un gran directorio de negocios locales, principalmente restaurantes, donde los usuarios pueden dejar reseñas sobre las experiencias vividas en dichos establecimientos.

El objetivo dentro de nuestro caso será conocer cuáles son los restaurantes más populares dentro de la plataforma. Para ello, primero se analizó el dataset y se filtró solo las columnas necesarias para el estudio.

- Antes: ID, Time_GMT, Phone, Organization, OLF, Rating, NumberReview, Category, Country, CountryCode, State, City, Street, Building

- Después: Organization, Rating, NumberReview

Con los datos listos se diseñó una fórmula con el objetivo de conseguir rankings más "fiables". Esto se debe a que dentro del dataset existen muchos restaurantes con 5 estrellas pero solo 1 o 2 reseñas, por lo que no podríamos darles un puesto alto en nuestro ranking.

## La Fórmula de Confianza

$$Puntuación = \left( \frac{v}{v+m} \times R \right) + \left( \frac{m}{v+m} \times C \right)$$

**Donde:**

- **R:** Rating individual
- **v:** Número de reseñas (votos)
- **C:** El rating promedio de todo el dataset
- **m:** El "umbral de confianza"

El valor de $m$ lo marcamos como 100, lo que quiere decir que el restaurante necesita al menos 100 reseñas para que su rating real $R$ y el promedio $C$ tengan el mismo peso

Lo que quiere decir que si tiene menos de 100 reseñas, su puntuación apuntará a su promedio $C$, mientras que si tiene más de 100, su puntuación apuntará a su rating real $R$

La fórmula utiliza dos fracciones que actúan como "pesos" en un promedio ponderado, donde los pesos suman siempre 1:
$$\frac{v}{v+m} + \frac{m}{v+m} = 1$$

-------------------------------------

El **Primer Peso:** $\frac{v}{v+m}$ determina qué porcentaje del total de votos (reales + virtuales) proviene de reseñas reales

Cuando $v$ es pequeño (ej: $v = 1$): $\frac{1}{101} \approx 0.01$ → el rating real $R$ tiene poco peso

Cuando $v$ es grande (ej: $v = 1000$): $\frac{1000}{1100} \approx 0.91$ → el rating real $R$ domina

Por lo tanto, representa el "grado de confianza" en el rating real del restaurante

--------------------------

El **Segundo Peso:** $\frac{m}{v+m}$ representa cuánto arrastramos la puntuación hacia el promedio global cuando hay pocas reseñas

Cuando $v$ es pequeño (ej: $v = 1$): $\frac{100}{101} \approx 0.99$ → el promedio global $C$ domina

Cuando $v$ es grande (ej: $v = 1000$): $\frac{100}{1100} \approx 0.09$ → el promedio global $C$ tiene poco peso

## 3. Metodología y Entorno de Pruebas

**Preparación de Datos:** Describir el proceso de limpieza (Java limpiarDatos.java y Python limpiar_datos.py). Mencionar la limpieza de comillas (.trim().replace()) y la corrección del locale (punto vs coma)

**Entorno de Hardware:**

- Computadora 1 (Felipe): especificaciones (CPU, núcleos, RAM)
- Computadora 2 (Aidan): especificaciones (CPU, núcleos, RAM)
- Computadora 3 (Deysi): especificaciones (CPU, núcleos, RAM)

**Entorno de Software:**

- Java: versión del JDK
- Python: versión de Python, Pandas, multiprocessing

### Algoritmos implementados

**QuickSort ($O(n \log n)$):**

- **Lógica (Java):** Explicar la implementación de tu compañera (partición de Hoare, pivote aleatorio)
- **Lógica (Python):** Explicar la implementación (partición de Lomuto, pivote aleatorio)

**HeapSort ($O(n \log n)$):**

- **Lógica (Java y Python):** Explicar el proceso en dos fases, primero construir el montículo (heapify) y luego extraer la raíz y re-balancear

## 5. Implementación de Multiprocesamiento (Python)

**Estrategia:** "Divide y vencerás" en paralelo. Explicar por qué no se puede paralelizar un algoritmo $O(n^2)$ como BubbleSort, pero sí un $O(n \log n)$

**Componentes Clave:**

- **mult.Pool():** Explicar que esto crea los "trabajadores" (uno por núcleo)
- **pool.map():** Explicar que este es el comando que asigna un trozo de datos a cada trabajador y los ejecuta en paralelo
- **Funciones "Silenciosas":** Explicar por qué fue necesario crear _quick_sort_silencioso y_heap_sort_silencioso (para evitar el "deadlock" de la consola)
- **Fusión Manual:** Explicar que la función fusionar_dos_listas fue necesaria para ensamblar los trozos ordenados al final

## 6. Resultados y Tablas Comparativas

**Tabla 1: Java (un solo núcleo) - Tiempo en milisegundos**

| Computadora | CPU (núcleos) | QuickSort (ms) | HeapSort (ms) |
| :--- | :--- | :--- | :--- |
| PC 1 (Felipe) | (ej. i7, 4 núcleos) | Tiempo | Tiempo |
| PC 2 (Aidan) | (ej. Ryzen 5, 6 núcleos) | Tiempo | Tiempo |
| PC 3 (Deysi) | (ej. M1, 8 núcleos) | Tiempo | Tiempo |

**Tabla 2: Python (paralelo) - Tiempo en milisegundos**

| Computadora | CPU (núcleos) | QuickSort Paralelo (ms) | HeapSort Paralelo (ms) |
| :--- | :--- | :--- | :--- |
| PC 1 (Felipe) | (ej. i7, 4 núcleos) | Tiempo | Tiempo |
| PC 2 (Aidan) | (ej. Ryzen 5, 6 núcleos) | Tiempo | Tiempo |
| PC 3 (Deysi) | (ej. M1, 8 núcleos) | Tiempo | Tiempo |

**Análisis de Resultados:**

- Comparar QuickSort vs HeapSort (¿cuál fue más rápido en Java y por qué?)
- Comparar Java (un núcleo) vs Python (paralelo)
- Analizar el "speedup" (aceleración): ¿El PC de 8 núcleos fue el doble de rápido que el de 4 núcleos? ¿Por qué sí o por qué no? Mencionar el costo de la fusión y el pool.map

## 7. Conclusión

Responder a la pregunta principal del proyecto: "¿Cuál es el mejor ordenamiento?"

Resumir el hallazgo, por ejemplo "El algoritmo QuickSort ejecutado en paralelo en Python fue la solución más rápida" si ese fue el resultado

Mencionar la importancia de elegir algoritmos compatibles con la paralelización, $O(n \log n)$ frente a $O(n^2)$

-------------------------------------
