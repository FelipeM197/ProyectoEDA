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
        String archivoLimpio = "datos_procesados.csv";
        String archivoSalida = "restaurantes_ordenados.csv";

        // Lectura de los datos
        System.out.println("Cargando datos a memoria desde: " + archivoLimpio);
        ArrayList<Restaurante> listaRestaurantes = new ArrayList<>(1_000_000);

        try (BufferedReader br = new BufferedReader(new FileReader(archivoLimpio))) {
            String linea;
            br.readLine(); // Saltamos la cabecera 

            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(",");
                try{
                    String nombreREstaurante = partes[0];
                    double rating = Double.parseDouble(partes[1]);   
                    int numeroResenas = Integer.parseInt(partes[2]);
                    Restaurante restaurante = new Restaurante(nombreREstaurante, rating, numeroResenas);
                    listaRestaurantes.add(restaurante);

                }catch (NumberFormatException e){
                    System.err.println("Saltando línea mal formada: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        
        System.out.println("Carga completa. Se leyeron " + listaRestaurantes.size() + " registros.");

        System.out.println("\n=== MENÚ DE ORDENAMIENTO ===");
        System.out.println("1. Ordenar con HeapSort");
        System.out.println("2. Ordenar con QuickSort");
        System.out.print("Seleccione el algoritmo (1-2): ");
        
        int opcion = scanner.nextInt();
        
        // Iniciamos el cronómetro después de la selección
        long tiempoInicio = System.nanoTime();
        
        // Calculamos C (promedio global) para la fórmula bayesiana
        double sumaTotalRatings = 0.0;
        for (Restaurante r : listaRestaurantes) {
            sumaTotalRatings += r.rating;
        }
        double C = sumaTotalRatings / listaRestaurantes.size();
        System.out.println("C calculado: " + C);
        
        // Aplicamos la fórmula bayesiana a cada restaurante:
        // Score = (v/(v+m) * R) + (m/(v+m) * C)
        // Donde: v = número de reviews, R = rating individual, C = promedio global
        for (Restaurante r : listaRestaurantes) {
            double R = r.rating;
            int v = r.numeroResenas;
            r.puntuacionTotal = (v / (v + m)) * R + (m / (v + m)) * C;
        }
        

        
        long tiempoFin = System.nanoTime();
        double tiempoTotalMS = (tiempoFin - tiempoInicio) / 1_000_000.0;
        
        // Menu principal
        System.out.println("\nIniciando ordenamiento...");
        switch(opcion) {
            case 1:
                System.out.println("Ejecutando HeapSort ");
                heapSort(listaRestaurantes);
                break;
            case 2:
                System.out.println("Ejecutando QuickSort");
                quickSort(listaRestaurantes);
                break;
            default:
                System.out.println("Opción no válida.");
                return;
        }

        // Generar archivo solo si se realizó el ordenamiento
        try (BufferedWriter writer = new BufferedWriter(new FileWriter(archivoSalida))) {
            writer.write("Posición,Nombre,Rating,NumeroReseñas,PuntuaciónTotal\n");
            for (int i = 0; i < listaRestaurantes.size(); i++) {
                Restaurante r = listaRestaurantes.get(i);
                writer.write(String.format("%d,%s,%.2f,%d,%.4f\n", 
                    i+1, r.nombre, r.rating, r.numeroResenas, r.puntuacionTotal));
            }
            System.out.println("\nResultados guardados en: " + archivoSalida);
        } catch (IOException e) {
            System.err.println("Error al escribir resultados: " + e.getMessage());
        }

        // Resultados finales
        System.out.printf("\nTiempo total: %.2f segundos\n", tiempoTotalMS/1000.0);
        System.out.println("\n=== TOP 10 RESTAURANTES ===");
        for (int i = 0; i < 10 && i < listaRestaurantes.size(); i++) {
            System.out.println((i+1) + ". " + listaRestaurantes.get(i));
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
}