"""Siembra extendida: libros nuevos, reseñas de ejemplo y lecturas acumuladas.

Es idempotente: no duplica libros ni reseñas si se vuelve a ejecutar.
Uso: python tools/seed_extra.py
"""

import os
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import models  # noqa: E402
from tools.build_sample_pdfs import BOOKS as NUEVOS  # noqa: E402

BASE = datetime(2026, 9, 1, 12, 0, tzinfo=timezone.utc)

# Fahrenheit 451 ya existe en el catálogo: se le asigna el PDF de muestra.
PDF_F451 = "pdf/fahrenheit-451.pdf"

NUEVOS_LIBROS = [
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "genero": "Distopía",
        "anio_publicacion": 1953,
        "descripcion": (
            "Un bombero empieza a esconder los libros que debería quemar y se pregunta si "
            "vale la pena vivir sin ideas. La novela fundacional sobre la censura."
        ),
        "imagen": "portadas/fahrenheit-451.jpg",
        "pdf": PDF_F451,
        "lecturas": 412,
    },
    {
        "titulo": "La metamorfosis",
        "autor": "Franz Kafka",
        "genero": "Narrativa",
        "anio_publicacion": 1915,
        "descripcion": (
            "Un empleado se despierta convertido en un insecto gigante y descubre que su "
            "familia, que lo mantenía, ahora lo teme."
        ),
        "imagen": "portadas/la-metamorfosis.jpg",
        "pdf": "pdf/la-metamorfosis.pdf",
        "lecturas": 288,
    },
    {
        "titulo": "Pedro Páramo",
        "autor": "Juan Rulfo",
        "genero": "Realismo mágico",
        "anio_publicacion": 1955,
        "descripcion": (
            "Juan Preciado viaja a Colotlán buscando a su padre Pedro Páramo y termina "
            "encontrando un pueblo habitado por los ecos de voces que nunca cesan."
        ),
        "imagen": "portadas/pedro-paramo.jpg",
        "pdf": "pdf/pedro-paramo.pdf",
        "lecturas": 197,
    },
    {
        "titulo": "El hobbit",
        "autor": "J. R. R. Tolkien",
        "genero": "Fantasía",
        "anio_publicacion": 1937,
        "descripcion": (
            "Bilbo Baggins, un hobbit tranquilo y sedentario, es arrastrado a una aventura "
            "para recuperar el tesoro de un dragón junto a trece enanos."
        ),
        "imagen": "portadas/el-hobbit.jpg",
        "pdf": "pdf/el-hobbit.pdf",
        "lecturas": 356,
    },
    {
        "titulo": "Harry Potter y la piedra filosofal",
        "autor": "J. K. Rowling",
        "genero": "Fantasía",
        "anio_publicacion": 1997,
        "descripcion": (
            "Harry descubre que es un mago a los once años y entra a Hogwarts, donde conoce "
            "a Ron y Hermione mientras se enfrenta a un secreto guardado en su escuela."
        ),
        "imagen": "portadas/harry-potter-piedra-filosofal.jpg",
        "pdf": "pdf/harry-potter-piedra-filosofal.pdf",
        "lecturas": 498,
    },
    {
        "titulo": "Orgullo y prejudice",
        "autor": "Jane Austen",
        "genero": "Clásico",
        "anio_publicacion": 1813,
        "descripcion": (
            "Elizabeth Bennet y el señor Darcy empiezan odiándose y terminan casándose, "
            "después de descubrir lo mal que se juzgaban."
        ),
        "imagen": "portadas/orgullo-y-prejuicio.jpg",
        "pdf": "pdf/orgullo-y-prejuicio.pdf",
        "lecturas": 174,
    },
    {
        "titulo": "Crimen y castigo",
        "autor": "Fiodor Dostoievski",
        "genero": "Clásico",
        "anio_publicacion": 1866,
        "descripcion": (
            "Un estudiante pobre comete un asesinato por una idea y pasa meses "
            "atormentado hasta que la justicia llega en forma de gracia."
        ),
        "imagen": "portadas/crimen-y-castigo.jpg",
        "pdf": "pdf/crimen-y-castigo.pdf",
        "lecturas": 233,
    },
    {
        "titulo": "El nombre de la rosa",
        "autor": "Umberto Eco",
        "genero": "Misterio",
        "anio_publicacion": 1980,
        "descripcion": (
            "Un monasterio medieval se ve perturbado por una serie de muertes y un "
            "investigador llega a acompañar a un bibliotecario ciego."
        ),
        "imagen": "portadas/el-nombre-de-la-rosa.jpg",
        "pdf": "pdf/el-nombre-de-la-rosa.pdf",
        "lecturas": 141,
    },
    {
        "titulo": "Rayuela",
        "autor": "Julio Cortázar",
        "genero": "Novela",
        "anio_publicacion": 1963,
        "descripcion": (
            "Un grupo de amigos en París atraviesa el juego, el azar y el amor en una "
            "búsqueda que rompe el orden del relato."
        ),
        "imagen": "portadas/rayuela.jpg",
        "pdf": "pdf/rayuela.pdf",
        "lecturas": 96,
    },
    {
        "titulo": "La sombra del viento",
        "autor": "Carlos Ruiz Zafón",
        "genero": "Misterio",
        "anio_publicacion": 2001,
        "descripcion": (
            "Un chico descubre el cementerio de los libros olvidados y ahí encuentra un "
            "manuscrito sin autor que cambia su vida para siempre."
        ),
        "imagen": "portadas/la-sombra-del-viento.jpg",
        "pdf": "pdf/la-sombra-del-viento.pdf",
        "lecturas": 118,
    },
]

# Lecturas iniciales de los libros que ya estaban en el catálogo.
LECTURAS_PREVIAS = {
    "Cien años de soledad": 264,
    "1984": 341,
    "La casa de los espíritus": 187,
    "El principito": 402,
    "Fundación": 156,
    "Crónica de una muerte anunciada": 132,
    "Un mundo feliz": 121,
    "El amor en los tiempos del cólera": 176,
    "Don Quijote de la Mancha": 229,
    "Frankenstein o el moderno Prometeo": 74,
}

from tools.resenas_datos import RESENAS  # noqa: E402


def seed_books():
    """Registra los libros nuevos y ajusta los que ya existían."""
    creados = 0
    existentes = {}

    for book in models.list_books():
        existentes[book["titulo"]] = dict(book)

    for nuevo in NUEVOS_LIBROS:
        actual = existentes.get(nuevo["titulo"])
        if not actual:
            book_id = models.add_book(
                nuevo["titulo"], nuevo["autor"], nuevo["genero"],
                nuevo["anio_publicacion"], nuevo["descripcion"],
                nuevo["imagen"], nuevo["pdf"],
            )
            with models.connect() as conn:
                conn.execute(
                    "UPDATE libros SET lecturas = ? WHERE id = ?",
                    (nuevo["lecturas"], book_id),
                )
            creados += 1
        else:
            with models.connect() as conn:
                conn.execute(
                    "UPDATE libros SET pdf = ?, imagen = ? WHERE id = ?",
                    (nuevo["pdf"], nuevo["imagen"], actual["id"]),
                )

    actualizados = 0
    for titulo, lecturas in LECTURAS_PREVIAS.items():
        actual = existentes.get(titulo)
        if actual:
            with models.connect() as conn:
                conn.execute(
                    "UPDATE libros SET lecturas = ? WHERE id = ?", (lecturas, actual["id"])
                )
            actualizados += 1

    return creados, actualizados


def seed_reviews():
    creada = 0
    for offset, (titulo, autor, calificacion, review_titulo, texto) in enumerate(RESENAS):
        book = None
        for row in models.list_books():
            if row["titulo"] == titulo:
                book = row
                break
        if not book:
            continue

        conn = models.connect()
        existe = conn.execute(
            "SELECT id FROM resenas WHERE libro_id = ? AND autor_nombre = ?",
            (book["id"], autor),
        ).fetchone()
        conn.close()
        if existe:
            continue

        creado_en = (BASE + timedelta(days=offset * 2, hours=offset)).isoformat()
        models.add_review(
            book_id=book["id"],
            autor_nombre=autor,
            calificacion=calificacion,
            titulo=review_titulo,
            texto=texto,
            usuario_id=None,
            creado_en=creado_en,
        )
        creada += 1
    return creada


if __name__ == "__main__":
    models.init_db()
    nuevos, actualizados = seed_books()
    reseñas = seed_reviews()
    print(f"Libros nuevos: {nuevos} | lecturas iniciales actualizadas: {actualizados}")
    print(f"Reseñas agregadas: {reseñas}")