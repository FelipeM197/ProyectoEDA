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
        System.out.println("1. Ordenar con BubbleSort");
        System.out.println("2. Ordenar con QuickSort (próximamente)");
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
                System.out.println("Ejecutando BubbleSort...");
                bubbleSort(listaRestaurantes);
                break;
            case 2:
                System.out.println("QuickSort aún no implementado.");
                return;
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
    

    /**
     * Este algoritmo es O(n^2), por lo que deberia tardarse algunos minutos
     */
    public static void bubbleSort(ArrayList<Restaurante> lista) {
        int n = lista.size();
        int iteracion = 0;
        
        for (int i = 0; i < n - 1; i++) {
            boolean intercambiado = false;
            iteracion++;
            System.out.printf("Iteración %d de %d...\n", iteracion, n-1);
            
            for (int j = 0; j < n - i - 1; j++) {
                if (lista.get(j).puntuacionTotal < lista.get(j + 1).puntuacionTotal) {
                    Restaurante temp = lista.get(j);
                    lista.set(j, lista.get(j + 1));
                    lista.set(j + 1, temp);
                    intercambiado = true;
                }
            }
            
            if (!intercambiado) {
                System.out.println("Ordenamiento completado en " + iteracion + " iteraciones.");
                break;
            }
        }
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