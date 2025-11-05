import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Locale;

public class Ordenar {

    public static void main(String[] args) {
        // Establecemos las reglas de estados unidos por los decimales
        Locale.setDefault(Locale.US); 
        
        String archivoLimpio = "datos_procesados.csv";

        System.out.println("Cargando datos a memoria desde: " + archivoLimpio);

        // Creamos el ArrayList donde se guardará todo
        // (Le damos un tamaño inicial para que sea más eficiente)
        ArrayList<Restaurante> listaRestaurantes = new ArrayList<>(1_000_000); 

        // usamos el mismo letodo que en limpiar datos
        try (BufferedReader br = new BufferedReader(new FileReader(archivoLimpio))) {
            String linea;
            
            br.readLine(); 

            while ((linea = br.readLine()) != null) {
                String[] partes = linea.split(",");
                
                // se pone un try por si alguna linea del archivo limpio esta corrupta
                try{
                    // Leemos las 4 columnas de nuestro archivo limpio
                    String nombreREstaurante = partes[0];
                    double rating = Double.parseDouble(partes[1]);   
                    int numeroResenas = Integer.parseInt(partes[2]);
                    double puntuacionTotal = Double.parseDouble(partes[3]);
                    
                    // Creamos el objeto Restaurante
                    Restaurante restaurante = new Restaurante(nombreREstaurante, rating, numeroResenas, puntuacionTotal);
                    
                    // En lugar de escribir (bw.write), guardamos en la lista
                    listaRestaurantes.add(restaurante);

                }catch (NumberFormatException e){
                    System.err.println("Saltando línea mal formada: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            // Capturamos un error si, por ejemplo, el archivo no existe.
            e.printStackTrace();
        }
        
        System.out.println("Carga completa. Se leyeron " + listaRestaurantes.size() + " registros.");

        // --- 2. PREPARAR LISTAS PARA ORDENAR ---
        ArrayList<Restaurante> listaParaAlgoritmoA = new ArrayList<>(listaRestaurantes);
        ArrayList<Restaurante> listaParaAlgoritmoB = new ArrayList<>(listaRestaurantes);
        ArrayList<Restaurante> listaParaAlgoritmoC = new ArrayList<>(listaRestaurantes);

        
        
        // TODO: Implementar QuickSort
        System.out.println("Iniciando QuickSort...");


        // TODO: Implementar MergeSort
        System.out.println("Iniciando MergeSort...");

        
        String nombreSalida = "Salida_Ordenada.csv";
        System.out.println("Escribiendo archivo ordenado en: " + nombreSalida);

        try (BufferedWriter bw = new BufferedWriter(new FileWriter(nombreSalida))) {
            
            // Escribimos la cabecera primero
            bw.write("Organization,Rating,NumberReview,PuntuacionConfianza\n");
            
            for (Restaurante r : listaParaAlgoritmoA) { 
                
                // Convertimos el objeto 'Restaurante' de nuevo a un string CSV
                String lineaLimpia = String.format("%s,%.2f,%d,%.4f",
                        r.nombreREstaurante, r.rating, r.numeroResenas, r.puntuacionTotal);
                
                bw.write(lineaLimpia);
                bw.newLine(); // Añadimos un salto de línea
            }
            System.out.println("Archivo '" + nombreSalida + "' creado exitosamente!");
            
        } catch (IOException e) {
            // Capturamos un error si no podemos escribir el archivo
            e.printStackTrace();
        }
        
        System.out.println("Análisis completado.");
    }
    
    // Aquí abajo añadiremos los métodos 'quickSort', 'partition', 'mergeSort' y 'merge'
}