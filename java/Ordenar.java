import java.io.*;
import java.util.ArrayList;
import java.util.Locale;
import java.util.Scanner;

public class Ordenar {
    // m = 100 es un valor de equilibrio para la fórmula bayesiana
    // Este número actúa como "número de ratings" virtual para equilibrar entre
    // el rating individual del restaurante y el promedio global
    private static final double m = 100.0;

    public static void main(String[] args) {
       Locale.setDefault(Locale.US);
        Scanner scanner = new Scanner(System.in);
        String nombreArchivoEntrada = "datos_procesados.csv";
        // Usar el directorio actual sin subcarpeta 'java'
        File archivoEntrada = encontrarArchivo(nombreArchivoEntrada);

        if (archivoEntrada == null) {
            System.err.println("ERROR FATAL: No se encuentra el archivo '" + nombreArchivoEntrada + "'.");
            System.err.println("Asegúrate de estar ejecutando el programa desde la carpeta 'proyectoEda' o 'proyectoEda/java'.");
            System.err.println("Ruta de búsqueda actual: " + System.getProperty("user.dir"));
            return;
        }

        // Definimos las rutas completas basadas en donde encontramos el archivo de entrada
        // Esto asegura que los archivos de salida se guarden en la misma carpeta que el de entrada
        String carpetaBase = archivoEntrada.getParent();
        if (carpetaBase == null) carpetaBase = "."; // Por si está en la raíz actual

        String archivoLimpio = archivoEntrada.getPath(); // Ruta completa detectada
        
        // Los de salida los guardamos en la misma carpeta donde encontramos el de entrada
        String archivoQuickSort = carpetaBase + File.separator + "datos_ordenados_quick_sort.csv";
        String archivoSalida = carpetaBase + File.separator + "restaurantes_ordenados.csv";
        
        System.out.println("Archivo encontrado en: " + archivoLimpio);


        // Lectura previa de datos (solo usada por opción 1)
        System.out.println("=== MENÚ DE ORDENAMIENTO ===");
        System.out.println("1. Generar archivo QuickSort por numero de reseñas");
        System.out.println("2. Ejecutar HeapSort por puntuacion total (desde archivo QuickSort)");
        System.out.print("Seleccione el algoritmo (1-2): ");
        int opcion = scanner.nextInt();

        if (opcion == 1) {
            System.out.println("Cargando datos a memoria desde: " + archivoLimpio);
            ArrayList<Restaurante> listaRestaurantes = new ArrayList<>(1_000_000);
            try (BufferedReader br = new BufferedReader(new FileReader(archivoLimpio))) {
                String linea;
                br.readLine(); // Saltamos la cabecera 
                while ((linea = br.readLine()) != null) {
                    String[] partes = linea.split(",");
                    try{
                        String nombre = partes[0];
                        double rating = Double.parseDouble(partes[1]);   
                        int numeroResenas = Integer.parseInt(partes[2]);
                        Restaurante restaurante = new Restaurante(nombre, rating, numeroResenas);
                        listaRestaurantes.add(restaurante);
                    } catch (Exception e){
                        // Ignorar líneas mal formadas
                    }
                }
            } catch (IOException e) {
                System.err.println("Error leyendo " + archivoLimpio + ": " + e.getMessage());
                return;
            }

            if (listaRestaurantes.isEmpty()) {
                System.out.println("No se cargaron registros. Abortando.");
                return;
            }

            System.out.println("Carga completa. Se leyeron " + listaRestaurantes.size() + " registros.");
            System.out.println("Iniciando QuickSort por NumberReview (genera archivo intermedio)...");
            long t0 = System.nanoTime();

            // QuickSort por número de reseñas (no calcula fórmula)
            recursividadReviews(listaRestaurantes, 0, listaRestaurantes.size() - 1);

            long t1 = System.nanoTime();
            double tiempoSeg = (t1 - t0) / 1_000_000_000.0;
            System.out.printf("QuickSort (por reseñas) completado en %.4f segundos\n", tiempoSeg);

            // Escribir archivo intermedio con la estructura esperada
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(archivoQuickSort))) {
                // El archivo intermedio NO incluye la columna PuntuaciónTotal
                writer.write("Posición,Nombre,Rating,NumeroReseñas\n");
                for (int i = 0; i < listaRestaurantes.size(); i++) {
                    Restaurante r = listaRestaurantes.get(i);
                    writer.write(String.format("%d,%s,%.2f,%d\n",
                        i+1, r.nombre, r.rating, r.numeroResenas));
                }
                System.out.println("Archivo QuickSort generado: " + archivoQuickSort);
            } catch (IOException e) {
                System.err.println("Error al escribir " + archivoQuickSort + ": " + e.getMessage());
            }
            // Imprimir Top 20 únicos
            System.out.println("\n=== TOP 20 RESTAURANTES (por NumberReview) ===");
            imprimirTop20Unicos(listaRestaurantes, false);

        } else if (opcion == 2) {
            // Verificamos que exista el archivo generado por QuickSort
            File f = new File(archivoQuickSort);
            if (!f.exists()) {
                System.out.println("El archivo " + archivoQuickSort + " no existe.");
                System.out.println("Genere primero el archivo QuickSort (opción 1).");
                return;
            }

            // Cargar lista desde archivoQuickSort
            ArrayList<Restaurante> listaRestaurantes = new ArrayList<>(1_000_000);
            try (BufferedReader br = new BufferedReader(new FileReader(archivoQuickSort))) {
                String linea;
                br.readLine(); // cabecera
                while ((linea = br.readLine()) != null) {
                    String[] partes = linea.split(",");
                    try{
                        // Formato esperado: Posición,Nombre,Rating,NumeroReseñas,PuntuaciónTotal
                        String nombre = partes[1];
                        double rating = Double.parseDouble(partes[2]);
                        int numeroResenas = Integer.parseInt(partes[3]);
                        Restaurante restaurante = new Restaurante(nombre, rating, numeroResenas);
                        listaRestaurantes.add(restaurante);
                    } catch (Exception e) {
                        // ignorar línea mal formada
                    }
                }
            } catch (IOException e) {
                System.err.println("Error leyendo " + archivoQuickSort + ": " + e.getMessage());
                return;
            }

            if (listaRestaurantes.isEmpty()) {
                System.out.println("No se cargaron registros desde " + archivoQuickSort);
                return;
            }

            System.out.println("Cálculo de C (promedio global) y aplicación de la fórmula...");
            long t0 = System.nanoTime();

            double sumaTotalRatings = 0.0;
            for (Restaurante r : listaRestaurantes) sumaTotalRatings += r.rating;
            double C = sumaTotalRatings / listaRestaurantes.size();
            System.out.println("C calculado: " + C);

            for (Restaurante r : listaRestaurantes) {
                double R = r.rating;
                int v = r.numeroResenas;
                r.puntuacionTotal = (v / (v + m)) * R + (m / (v + m)) * C;
            }

            // Ordenar por puntuacionTotal con HeapSort
            System.out.println("Ejecutando HeapSort por puntuación total...");
            heapSort(listaRestaurantes);

            long t1 = System.nanoTime();
            double tiempoSeg = (t1 - t0) / 1_000_000_000.0;
            System.out.printf("HeapSort completado en %.4f segundos\n", tiempoSeg);

            // Escribir archivo final (conserva duplicados en el archivo)
            try (BufferedWriter writer = new BufferedWriter(new FileWriter(archivoSalida))) {
                writer.write("Posición,Nombre,Rating,NumeroReseñas,PuntuaciónTotal\n");
                for (int i = 0; i < listaRestaurantes.size(); i++) {
                    Restaurante r = listaRestaurantes.get(i);
                    writer.write(String.format("%d,%s,%.2f,%d,%.4f\n",
                        i+1, r.nombre, r.rating, r.numeroResenas, r.puntuacionTotal));
                }
                System.out.println("Archivo final generado: " + archivoSalida);
            } catch (IOException e) {
                System.err.println("Error al escribir " + archivoSalida + ": " + e.getMessage());
            }
            // Imprimir Top 20 únicos con puntuación
            System.out.println("\n=== TOP 20 RESTAURANTES (por PuntuaciónTotal) ===");
            imprimirTop20Unicos(listaRestaurantes, true);

        } else {
            System.out.println("Opción no válida.");
        }

        scanner.close();
    }
    

    public static void heapSort(ArrayList<Restaurante> lista) {
        int n = lista.size();

        // Construir un Min-Heap (el elemento más pequeño en la raíz)
        // Empezamos desde el último nodo no-hoja (n/2 - 1)
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(lista, n, i);
        }

        // Extraer elementos (el más pequeño) uno por uno
        for (int i = n - 1; i > 0; i--) {
            // Mover la raíz actual (el más pequeño) al final de la sección
            // (que es 'i')
            Restaurante temp = lista.get(0);
            lista.set(0, lista.get(i));
            lista.set(i, temp);
            
            // (Imprimimos el progreso, similar a Python)
            if (i % 1000 == 0) {
                 System.out.printf("HeapSort: Re-balanceando heap... %d/%d\r", (n-i), n);
            }

            // Llamar a heapify en el heap reducido (tamaño 'i')
            heapify(lista, i, 0);
        }
        System.out.println("\nHeapSort completado.");
    }

    /**
     * Función auxiliar 'heapify' (o 'hundir').
     * Asegura que el sub-árbol con raíz en 'i' cumpla la propiedad de Min-Heap.
     * 'n' es el tamaño del heap.
     */
    public static void heapify(ArrayList<Restaurante> lista, int n, int i) {
        int menor = i;      // Inicializamos 'menor' como la raíz
        int izq = 2 * i + 1;  // índice del hijo izquierdo
        int der = 2 * i + 2;  // índice del hijo derecho

        // Si el hijo izquierdo es MENOR que la raíz
        if (izq < n && lista.get(izq).puntuacionTotal < lista.get(menor).puntuacionTotal) {
            menor = izq;
        }

        // Si el hijo derecho es MENOR que el 'menor' actual
        if (der < n && lista.get(der).puntuacionTotal < lista.get(menor).puntuacionTotal) {
            menor = der;
        }

        // Si 'menor' no es la raíz (o sea, si un hijo era más pequeño)
        if (menor != i) {
            // Intercambiamos la raíz con el 'menor'
            Restaurante swap = lista.get(i);
            lista.set(i, lista.get(menor));
            lista.set(menor, swap);

            // Recursivamente llamamos a 'heapify' en el sub-árbol afectado
            heapify(lista, n, menor);
        }
    }



    public static void quickSort(ArrayList<Restaurante> lista) {
        System.out.println("\nIniciando QuickSort...");
        // Llama al método recursivo principal
        recursividad(lista, 0, lista.size() - 1);
        System.out.println("\nQuickSort completado.");
    }

    /**
      Método de partición (esquema Hoare) del código de tu compañera.
      Hecho 'static' y modificado para usar acceso directo a '.puntuacionTotal'.
     */
    public static int compara(ArrayList<Restaurante> arreglo, int inicio, int fin) {
        // Para hacer el codigo mas dinamico, eligimos un pivote aleatorio
        int pivote = pivoteAleatorio(arreglo, inicio, fin);
        // CORRECCIÓN: Se cambió getPuntuacionTotal() por .puntuacionTotal
        double pivoteValor = arreglo.get(pivote).puntuacionTotal;

        // Variables para los índices que recorrerán el arreglo
        int i = inicio;
        int j = fin;

        // Mientras no se crucen los índices
        while (i <= j) {
            // CORRECCIÓN: Se cambió getPuntuacionTotal() por .puntuacionTotal
            while (i <= fin && arreglo.get(i).puntuacionTotal > pivoteValor) {
                i++;
            }
            // CORRECCIÓN: Se cambió getPuntuacionTotal() por .puntuacionTotal
            while (j >= inicio && arreglo.get(j).puntuacionTotal < pivoteValor) {
                j--;
            }
            // Si no se han cruzado los índices, se realiza el intercambio
            if (i <= j) {
                cambio(arreglo, i, j);
                i++;
                j--;
            }
        }
        return i;
    }

    /**
      Método para intercambiar dos elementos en el arreglo.
      Hecho 'static'.
     */
    public static void cambio(ArrayList<Restaurante> arreglo, int i, int j) {
        Restaurante temp = arreglo.get(i);
        arreglo.set(i, arreglo.get(j));
        arreglo.set(j, temp);
    }

    /**
      Método recursivo principal para aplicar el Quicksort.
      Hecho 'static'.
     */
    public static void recursividad(ArrayList<Restaurante> arreglo, int inicio, int fin) {
        if (inicio < fin) {
            int i = compara(arreglo, inicio, fin);

            // Las llamadas recursivas ahora son estáticas
            if (inicio < i - 1) recursividad(arreglo, inicio, i - 1);
            if (i < fin) recursividad(arreglo, i, fin);
        }
    }

    /**
      Método para obtener un pivote aleatorio.
      Hecho 'static'.
     */
    public static int pivoteAleatorio(ArrayList<Restaurante> arreglo, int inicio, int fin) {
        int indiceAleatorio = inicio + (int) (Math.random() * (fin - inicio + 1));
        return indiceAleatorio;
    }

    //Clase para obtener el promedio de los ratings y asi obtener una C (Parte de la formula) con la que trabajar
    public static double calcularRatingPromedio(String archivoOriginal) {
        
        double sumaTotalRatings = 0.0;
        int conteoTotalLineas = 0;
        
        try (BufferedReader br = new BufferedReader(new FileReader(archivoOriginal))) {
            
            String linea;
            
            // Leemos y con eso saltamos la cabecera
            br.readLine(); 

            // bucle que leera el resto del archivo
            while ((linea = br.readLine()) != null) {
                
                String[] partes = linea.split(",");
                // se pone un try para que en caso de que los datos no coincidan, ej: sea 
                //un string en vez de un numero, no se rompa el programa
                try{
                    String stringRatingSucio = partes[5];

                    // Limpiamos el string de posibles comillas u otros caracteres no numericos
                    // Esto se hace porque se noto que al limpiar hay varios archivos decimales pasados por string
                    String stringRatingLimpio = stringRatingSucio.replace("\"", "").trim();

                    double rating = stringRatingLimpio.isEmpty() ? 0.0 : Double.parseDouble(stringRatingLimpio);

                    sumaTotalRatings += rating;
                    conteoTotalLineas++;
                }catch (NumberFormatException e){
                    System.err.println("Dato corrupto en el calculo de C: " + e.getMessage());
                }
 
            }
            
        } catch (IOException e) {
            System.err.println("Error: " + e.getMessage());
        }
        
        if (conteoTotalLineas > 0) {
            return sumaTotalRatings / conteoTotalLineas;
        } else {
            return 0.0; // En caso de que no haya lineas 
        }
    }

    // Nuevo: comparador/recursividad quicksort por NumberReview (no tocar comentarios existentes)
    public static int comparaReviews(ArrayList<Restaurante> arreglo, int inicio, int fin) {
        int pivote = pivoteAleatorio(arreglo, inicio, fin);
        int pivoteValor = arreglo.get(pivote).numeroResenas;
        int i = inicio;
        int j = fin;
        while (i <= j) {
            while (i <= fin && arreglo.get(i).numeroResenas > pivoteValor) i++;
            while (j >= inicio && arreglo.get(j).numeroResenas < pivoteValor) j--;
            if (i <= j) {
                cambio(arreglo, i, j);
                i++; j--;
            }
        }
        return i;
    }

    public static void recursividadReviews(ArrayList<Restaurante> arreglo, int inicio, int fin) {
        if (inicio < fin) {
            int i = comparaReviews(arreglo, inicio, fin);
            if (inicio < i - 1) recursividadReviews(arreglo, inicio, i - 1);
            if (i < fin) recursividadReviews(arreglo, i, fin);
        }
    }

    // Imprime en consola el Top 20 de restaurantes sin nombres repetidos.
    // Si porPuntuacion == true muestra Score, Reviews y Rating; si es false muestra Reviews y Rating.
    public static void imprimirTop20Unicos(ArrayList<Restaurante> lista, boolean porPuntuacion) {
        ArrayList<String> nombresVistosLocal = new ArrayList<>(20); // como mucho guardaremos 20 nombres
        int mostrados = 0;
        for (Restaurante restauranteActual : lista) {
            String nombreNormalizadoLocal = (restauranteActual.nombre == null) ? "" : restauranteActual.nombre.trim().toLowerCase();
            boolean yaVisto = false;
            // búsqueda lineal en la lista pequeña nombresVistosLocal (máx 20 elementos)
            for (String n : nombresVistosLocal) {
                if (n.equals(nombreNormalizadoLocal)) {
                    yaVisto = true;
                    break;
                }
            }
            if (yaVisto) continue;

            nombresVistosLocal.add(nombreNormalizadoLocal);
            mostrados++;
            if (porPuntuacion) {
                System.out.printf("%2d. %-35s Score: %.4f  Reviews: %d  Rating: %.2f\n", mostrados,
                    (restauranteActual.nombre.length() > 32 ? restauranteActual.nombre.substring(0, 32) + ".." : restauranteActual.nombre),
                    restauranteActual.puntuacionTotal, restauranteActual.numeroResenas, restauranteActual.rating);
            } else {
                System.out.printf("%2d. %-40s Reviews: %d  Rating: %.2f\n", mostrados,
                    (restauranteActual.nombre.length() > 37 ? restauranteActual.nombre.substring(0, 37) + ".." : restauranteActual.nombre),
                    restauranteActual.numeroResenas, restauranteActual.rating);
            }

            if (mostrados >= 20) break;
        }
    }
    public static File encontrarArchivo(String nombreArchivo) {
        // 1. Intento directo (si ejecutamos desde la carpeta 'java')
        File f = new File(nombreArchivo);
        if (f.exists()) return f;

        // 2. Intento relativo a carpeta 'java' (si ejecutamos desde 'proyectoEda')
        // File.separator se adapta automáticamente a Windows (\) o Linux (/)
        f = new File("java" + File.separator + nombreArchivo);
        if (f.exists()) return f;
        
        // 3. Intento en carpeta 'src' (común en IDEs como VS Code o IntelliJ)
        f = new File("src" + File.separator + nombreArchivo);
        if (f.exists()) return f;

        // Si no se encuentra en ninguno
        return null;
    }
}