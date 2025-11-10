import java.io.BufferedReader;
import java.io.BufferedWriter; 
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Locale;

// Nombre de clase cambiado a Mayúscula (convención de Java)
public class limpiarDatos {

    public static void main(String[] args) throws IOException {
        // Establecemos las reglas de estados unidos por los decimales 
        // Aqui se pone con coma en vez de punto, cosa que genera conflictos al leer y escribir el csv
        Locale.setDefault(Locale.US);       
        String archivoOriginal = "yelp_database.csv"; 
        String archivoLimpio = "datos_procesados.csv";

        System.out.println("Creando el archivo con 3 columnas: Organization,Rating,NumberReview");

        try (BufferedReader br = new BufferedReader(new FileReader(archivoOriginal));
             BufferedWriter bw = new BufferedWriter(new FileWriter(archivoLimpio))) {
            
            String linea;
            
            linea = br.readLine(); // Saltamos la primera linea (cabecera)
            // Escribimos la nueva cabecera solo con los datos que nos interesan
            bw.write("Organization,Rating,NumberReview\n");

            while ((linea = br.readLine()) != null) {
                
                String[] partes = linea.split(",");
                // Aqui utilizamos un segundo try para asegurarnos de que los datos corruptos no nos afecten
                try {
                    // el nombre esta en la posicion 3 del archivo
                    String nombre = partes[3];

                    // Se obtiene rating y numero de reseñas (sin hacer cálculos)
                    String ratingSucio = partes[5];
                    String numeroResenasSucio = partes[6];

                    //.trim regresa sin espacios blancos y replace quita las comillas
                    String ratingLimpio = ratingSucio.replace("\"", "").trim();
                    String numeroResenasLimpio = numeroResenasSucio.replace("\"", "").trim();

                    // Creamos el string que se escribira en el archivo con los datos limpios (solo 3 columnas)
                    String lineaLimpia = String.format("%s,%s,%s\n", nombre, ratingLimpio, numeroResenasLimpio);
                    bw.write(lineaLimpia);

                } catch (Exception e) {
                    // Se ha encontrado una linea corrupta o con menos columnas de las esperadas; la omitimos
                    System.err.println("Se ha encontrado una linea corrupta y se omitirá: " + e.getMessage());
                }
            }
        }
    }    


}
