import models

PORTADAS_DIR = "portadas"

SAMPLE_BOOKS = [
    {
        "titulo": "Cien años de soledad",
        "autor": "Gabriel García Márquez",
        "genero": "Novela",
        "anio_publicacion": 1967,
        "descripcion": (
            "La obra maestra del realismo mágico. Siete generaciones de la familia "
            "Buendía viven en el mítico pueblo de Macondo, entre guerras, leyendas, "
            "amores imposibles y destinos marcados por el mismo nombre. Un clásico "
            "universal de la literatura latinoamericana."
        ),
        "portada": "portadas/cien-anos-de-soledad.jpg",
        "pdf": "pdf/cien-anos-de-soledad.pdf",
    },
    {
        "titulo": "1984",
        "autor": "George Orwell",
        "genero": "Distopía",
        "anio_publicacion": 1949,
        "descripcion": (
            "Winston Smith trabaja en el Ministerio de la Verdad y empieza a "
            "cuestionar el régimen totalitario que lo vigila todo a través del "
            "Gran Hermano. Una de las distopías más influyentes del siglo XX."
        ),
        "portada": "portadas/1984.jpg",
        "pdf": "pdf/1984.pdf",
    },
    {
        "titulo": "La casa de los espíritus",
        "autor": "Isabel Allende",
        "genero": "Novela",
        "anio_publicacion": 1982,
        "descripcion": (
            "La saga familiar de la familia Trueba se entrelaza con la historia de "
            "Chile a lo largo del siglo XX, mezclando lo cotidiano con lo "
            "sobrenatural."
        ),
        "portada": "portadas/la-casa-de-los-espiritus.jpg",
        "pdf": "pdf/la-casa-de-los-espiritus.pdf",
    },
    {
        "titulo": "El principito",
        "autor": "Antoine de Saint-Exupéry",
        "genero": "Infantil",
        "anio_publicacion": 1943,
        "descripcion": (
            "Un piloto varado en el desierto conoce a un pequeño príncipe que llegó "
            "de otro planeta. Ciencia y corazón en una fábula que se lee a los "
            "ocho años y se relee a los ochenta."
        ),
        "portada": "portadas/el-principito.jpg",
        "pdf": "pdf/el-principito.pdf",
    },
    {
        "titulo": "Fundación",
        "autor": "Isaac Asimov",
        "genero": "Ciencia ficción",
        "anio_publicacion": 1951,
        "descripcion": (
            "Hari Seldon, creador de la psicohistoria, predice el colapso del vasto "
            "Imperio Galáctico y funda la Fundación para abreviar una era de "
            "oscuridad."
        ),
        "portada": "portadas/fundacion.jpg",
        "pdf": "pdf/fundacion.pdf",
    },
    {
        "titulo": "Crónica de una muerte anunciada",
        "autor": "Gabriel García Márquez",
        "genero": "Novela",
        "anio_publicacion": 1981,
        "descripcion": (
            "El pueblo entero sabe que van a matar a Santiago Nasar y nadie lo "
            "evita. Una investigación que reconstruye las horas previas al crimen "
            "con la precisión de quien ya conoce el final."
        ),
        "portada": "portadas/cronica-de-una-muerte-anunciada.jpg",
        "pdf": "pdf/cronica-de-una-muerte-anunciada.pdf",
    },
    {
        "titulo": "Un mundo feliz",
        "autor": "Aldous Huxley",
        "genero": "Distopía",
        "anio_publicacion": 1932,
        "descripcion": (
            "En una sociedad futura se fabrican seres humanos por lotes, se elimina "
            "el sufrimiento y se condiciona a todos para amar su papel. Un clásico "
            "de la distopía sobre la felicidad obligatoria."
        ),
        "portada": "portadas/un-mundo-feliz.jpg",
        "pdf": "pdf/un-mundo-feliz.pdf",
    },
    {
        "titulo": "El amor en los tiempos del cólera",
        "autor": "Gabriel García Márquez",
        "genero": "Novela",
        "anio_publicacion": 1985,
        "descripcion": (
            "Florentino Ariza espera más de cincuenta años para poder declarar su "
            "amor a Fermina Daza, fiel a la promesa de un amor que sobrevive a la "
            "espera, la distancia y el paso del tiempo."
        ),
        "portada": "portadas/el-amor-en-los-tiempos-del-colera.jpg",
        "pdf": "pdf/el-amor-en-los-tiempos-del-colera.pdf",
    },
    {
        "titulo": "Fahrenheit 451",
        "autor": "Ray Bradbury",
        "genero": "Ciencia ficción",
        "anio_publicacion": 1953,
        "descripcion": (
            "En un futuro donde los bomberos queman libros en lugar de apagar "
            "incendios, el bombero Montag empieza a esconder volúmenes prohibidos "
            "y a preguntarse si vale la pena vivir sin ideas."
        ),
        "portada": "portadas/fahrenheit-451.jpg",
        "pdf": "",
    },
    {
        "titulo": "Don Quijote de la Mancha",
        "autor": "Miguel de Cervantes",
        "genero": "Clásico",
        "anio_publicacion": 1605,
        "descripcion": (
            "Un hidalgo enloquecido por los libros de caballerías sale por los "
            "caminos de La Mancha a deshacer entuertos. La novela fundacional de "
            "la literatura moderna."
        ),
        "portada": "portadas/don-quijote-de-la-mancha.jpg",
        "pdf": "pdf/don-quijote-de-la-mancha.pdf",
    },
    {
        "titulo": "Frankenstein o el moderno Prometeo",
        "autor": "Mary Shelley",
        "genero": "Clásico",
        "anio_publicacion": 1818,
        "descripcion": (
            "Victor Frankenstein da vida a una criatura que el mismo rechaza. Huida, "
            "la criatura le exige que le fabrique una compañía, y ese rechazo desata "
            "una de las venganzas más oscuras del siglo XIX."
        ),
        "portada": "",
        "pdf": "pdf/frankenstein.pdf",
    },
]


def seed():
    models.init_db()
    for book in SAMPLE_BOOKS:
        models.add_book(
            book["titulo"],
            book["autor"],
            book["genero"],
            book["anio_publicacion"],
            book["descripcion"],
            book["portada"],
            book.get("pdf", ""),
        )
    print(f"Se agregaron {len(SAMPLE_BOOKS)} libros de ejemplo con portada y PDF local.")


if __name__ == "__main__":
    seed()
