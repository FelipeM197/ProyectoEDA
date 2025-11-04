public class Restaurante{
    String nombreREstaurante;
    double rating; 
    int numeroResenas;
    double puntuacionTotal;

    public Restaurante(String nombreREstaurante, double rating, int numeroResenas, double puntuacionTotal) {
        this.nombreREstaurante = nombreREstaurante;
        this.rating = rating;
        this.numeroResenas = numeroResenas;
        this.puntuacionTotal = puntuacionTotal;
    } 
    @Override
    public String toString() {
        return "Restaurante: " + nombreREstaurante + ", Rating: " + rating + ", Número de Reseñas: " + numeroResenas + ", Puntuación Total: " + puntuacionTotal;
    }

}