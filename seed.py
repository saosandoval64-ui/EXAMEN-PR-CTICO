import models

SAMPLE_BOOKS = [
    ("Cien años de soledad", "Gabriel García Márquez", "Novela", 1967),
    ("1984", "George Orwell", "Distopía", 1949),
    ("La casa de los espíritus", "Isabel Allende", "Novela", 1982),
    ("El principito", "Antoine de Saint-Exupéry", "Infantil", 1943),
    ("Fundación", "Isaac Asimov", "Ciencia ficción", 1951),
    ("Crónica de una muerte anunciada", "Gabriel García Márquez", "Novela", 1981),
    ("Un mundo feliz", "Aldous Huxley", "Distopía", 1932),
    ("El amor en los tiempos del cólera", "Gabriel García Márquez", "Novela", 1985),
    ("Fahrenheit 451", "Ray Bradbury", "Ciencia ficción", 1953),
    ("Don Quijote de la Mancha", "Miguel de Cervantes", "Clásico", 1605),
]


def seed():
    models.init_db()
    for titulo, autor, genero, anio in SAMPLE_BOOKS:
        models.add_book(titulo, autor, genero, anio)
    print(f"Se agregaron {len(SAMPLE_BOOKS)} libros de ejemplo.")


if __name__ == "__main__":
    seed()