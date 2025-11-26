import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.InputStream;
import java.util.Locale;

// Nombre de clase cambiado a Mayúscula (convención de Java)
public class limpiarDatos {

    public static void main(String[] args) throws IOException {
        // Establecemos las reglas de estados unidos por los decimales
        // Aqui se pone con coma en vez de punto, cosa que genera conflictos al leer y
        // escribir el csv
        Locale.setDefault(Locale.US);
        // Asegurar que los archivos se tomen desde la carpeta 'java' donde está este
        // archivo
        String nombreArchivoEntrada = "yelp_database.csv";
        String nombreArchivoSalida = "datos_procesados.csv";
        
        // Usar ClassLoader para cargar el archivo de forma portátil con InputStream (busca en los recursos del proyecto y no en los archivos del sistema)
        InputStream inputStream = limpiarDatos.class.getResourceAsStream("/" + nombreArchivoEntrada);

        // Verificación de existencia del archivo con if y mensaje de error claro
        if (inputStream == null) {
            System.err.println("ERROR FATAL: No se encuentra el recurso '" + nombreArchivoEntrada + "'.");
            System.err.println("Asegúrate de que el archivo esté en la carpeta 'java/' con los .java");
            System.err.println("Directorio actual: " + System.getProperty("user.dir"));
            return;
        }

        // Definimos la ruta de salida en el directorio actual
        String rutaCompletaSalida = nombreArchivoSalida;        
        
        System.out.println("Creando el archivo con 3 columnas: Organization,Rating,NumberReview");

        try (BufferedReader br = new BufferedReader(new InputStreamReader(inputStream));
                BufferedWriter bw = new BufferedWriter(new FileWriter(rutaCompletaSalida))) {
            String linea;

            linea = br.readLine(); // Saltamos la primera linea (cabecera)
            // Escribimos la nueva cabecera solo con los datos que nos interesan
            bw.write("Organization,Rating,NumberReview\n");

            while ((linea = br.readLine()) != null) {

                String[] partes = linea.split(",");
                // Aqui utilizamos un segundo try para asegurarnos de que los datos corruptos no
                // nos afecten
                try {
                    // el nombre esta en la posicion 3 del archivo
                    String nombre = partes[3];

                    // Se obtiene rating y numero de reseñas (sin hacer cálculos)
                    String ratingSucio = partes[5];
                    String numeroResenasSucio = partes[6];

                    // .trim regresa sin espacios blancos y replace quita las comillas
                    String ratingLimpio = ratingSucio.replace("\"", "").trim();
                    String numeroResenasLimpio = numeroResenasSucio.replace("\"", "").trim();

                    // Creamos el string que se escribira en el archivo con los datos limpios (solo
                    // 3 columnas)
                    String lineaLimpia = String.format("%s,%s,%s\n", nombre, ratingLimpio, numeroResenasLimpio);
                    bw.write(lineaLimpia);

                } catch (Exception e) {
                    // Se ha encontrado una linea corrupta o con menos columnas de las esperadas; la
                    // omitimos
                    System.err.println("Se ha encontrado una linea corrupta y se omitirá: " + e.getMessage());
                }
            }
        }
    }

}
