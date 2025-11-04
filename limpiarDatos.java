import java.io.BufferedReader;
import java.io.BufferedWriter; 
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

// Nombre de clase cambiado a Mayúscula (convención de Java)
public class limpiarDatos {

    // m es una constante, la definimos aquí
    private static final double m = 100.0;

    public static void main(String[] args) throws IOException {
        // Establecemos las reglas de estados unidos por los decimales 
        // Aqui se pone con coma en vez de punto, cosa que genera conflictos al leer y escribir el csv
        Locale.setDefault(Locale.US);       
        String archivoOriginal = "yelp_database.csv"; 
        String archivoLimpio = "datos_procesados.csv";
        System.out.println("Calculando C (Rating Promedio)...");
        
        // Calculamos C 
        double C = calcularRatingPromedio(archivoOriginal); 
        
        System.out.println("Resultado C = " + C); // Imprimimos el C calculado
        System.out.println("Creando el archivo");

        try (BufferedReader br = new BufferedReader(new FileReader(archivoOriginal));
             BufferedWriter bw = new BufferedWriter(new FileWriter(archivoLimpio))) {
            
            String linea;
            
            linea = br.readLine(); // Saltamos la primera linea (cabecera)
            // Escribimos la nueva cabecera solo con los datos que nos interesan
            bw.write("Organization,Rating,NumberReview,PuntuacionConfianza\n");

            while ((linea = br.readLine()) != null) {
                
                String[] partes = linea.split(",");
                // Aqui utilizamos un segundo try para asegurarnos de que los datos corruptos no nos afecten
                try {
                    // el nombre esta en la posicion 3 del archivo
                    String nombre = partes[3];

                    // Se realiza el mismo proceso que en el promedio
                    String ratingSucio = partes[5];
                    String numeroResenasSucio = partes[6];

                    //.trim regresa sin espacios blancos y replace quita las comillas
                    String ratingLimpio = ratingSucio.replace("\"", "").trim();
                    String numeroResenasLimpio = numeroResenasSucio.replace("\"", "").trim();
                    // Leemos los datos, siempre asegurandonos de que no sea nulo
                    double R = ratingLimpio.isEmpty() ? 0.0 : Double.parseDouble(ratingLimpio);
                    int v = numeroResenasLimpio.isEmpty() ? 0 : Integer.parseInt(numeroResenasLimpio);
                    
                    //prueba de que habia un problema con las posiciones de los datos
                    //int v = (int) numeroResenasDecimal;
                    // Formula: Puntuación = (v/(v+m) * R) + (m/(v+m) * C)
                    double parte1 = (v / (v + m)) * R;
                    double parte2 = (m / (v + m)) * C;
                    double puntuacionConfianza = parte1 + parte2;
                    // Creamos el string que se escribira en el archivo con los datos limpios
                    // String.format ayuda a resumir el metodo tradicional, le decimos que tipo de datos esperar y se los pasamos en el segundo parametro
                    String lineaLimpia = String.format("%s,%.2f,%d,%.4f\n", nombre, R, v, puntuacionConfianza);
                    bw.write(lineaLimpia);

                } catch (NumberFormatException e) {
                    System.err.println("Se ha encontrado un dato corrupto" + e.getMessage());
                }
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
