
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

-----


