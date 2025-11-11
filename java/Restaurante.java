public class Restaurante {
    public String nombre;
    public double rating;
    public int numeroResenas;
    public double puntuacionTotal;

    // Constructor con los campos básicos
    public Restaurante(String nombre, double rating, int numeroResenas) {
        this.nombre = nombre;
        this.rating = rating;
        this.numeroResenas = numeroResenas;
        this.puntuacionTotal = 0.0; // Se calculará después
    }

    @Override
    public String toString() {
        return String.format("%s (Rating: %.2f, Reseñas: %d, Score: %.4f)", 
            nombre, rating, numeroResenas, puntuacionTotal);
    }
}