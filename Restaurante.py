class Restaurante:
        
        def _init__(self, nombreREstaurante, rating, numeroResenas, puntuacionTotal):
            self.nombreREstaurante = nombreREstaurante
            self.rating = rating
            self.numeroResenas = numeroResenas
            self.puntuacionTotal = puntuacionTotal 

        def __repr__(self):
            return f"Restaurante(nombreREstaurante={self.nombreREstaurante}, rating={self.rating}, numeroResenas={self.numeroResenas}, puntuacionTotal={self.puntuacionTotal})"
        