"""PDF de muestra para los libros sin texto completo en el repositorio.

Genera un PDF con la portada, la ficha del libro y una sinopsis de la obra.
Uso: python tools/build_sample_pdfs.py
"""

import os

from PIL import Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A5
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORTADAS_DIR = os.path.join(BASE_DIR, "static", "portadas")
PDF_DIR = os.path.join(BASE_DIR, "static", "pdf")

ACCENT = colors.HexColor("#b4572b")
BRAND = colors.HexColor("#24384c")
INK = colors.HexColor("#221d16")
INK_SOFT = colors.HexColor("#7a7166")
LINE = colors.HexColor("#e7e2d8")

# titulo, autor, genero, anio, portada, pdf, descripcion corta, sinopsis larga
BOOKS = [
    {
        'titulo': "Fahrenheit 451",
        'autor': "Ray Bradbury",
        'genero': "Distopía",
        'portada': "fahrenheit-451.jpg",
        'pdf': "fahrenheit-451.pdf",
        'descripcion': "Un bombero empieza a esconder los libros que debería quemar y se pregunta si vale la pena vivir sin ideas.",
        'anio': 1953,
        'sinopsis': [
            "En un futuro donde los bomberos queman libros en lugar de apagar incendios, Montag cumple su trabajo con eficacia y sin preguntas. El título alude a la temperatura a la que el papel empieza a arder.",
            "Un vecino con el que cruza palabras en el metro le deja pensando, y Montag empieza a robar volumenes para leerlos de madrugada. Lo que sigue no es solo una censura estatal: Bradbury describe tambien la presion social, la television y el entretenimiento masivo que hacen que nadie quiera pensar.",
            "Huye de la ciudad junto a un grupo de personas que ha memorizado lo que ama, porque un libro que nadie recuerda es un libro que no existe.",
        ],
    },
    {
        'titulo': "La metamorfosis",
        'autor': "Franz Kafka",
        'genero': "Narrativa",
        'portada': "la-metamorfosis.jpg",
        'pdf': "la-metamorfosis.pdf",
        'descripcion': "Un empleado se despierta convertido en un insecto y descubre que su familia, que lo mantenia, ahora lo teme.",
        'anio': 1915,
        'sinopsis': [
            "Gregor Samsa sostiene a su familia con el sueldo de agente comercial. La novela abre con una de las lineas mas conocidas de la literatura: al despertar, Gregor se encuentra convertido en un monstruoso insecto.",
            "Lo que sigue es una historia sobre el valor de las personas. Su padre lo empuja de vuelta a su habitación, su madre llora y su hermana empieza a ocuparse de el a la fuerza. La rutina domestica se reorganiza entera: el aceite llega por la puerta y nadie entra a su cuarto.",
            "Kafka construye con humor negro un relato sobre lo poco que se ama sin condiciones. La criatura nunca habla y, aun asi, termina siendo expulsada.",
        ],
    },
    {
        'titulo': "Pedro Paramo",
        'autor': "Juan Rulfo",
        'genero': "Realismo magico",
        'portada': "pedro-paramo.jpg",
        'pdf': "pedro-paramo.pdf",
        'descripcion': "Juan Preciado busca a su padre Pedro Paramo y encuentra un pueblo habitado por los ecos de voces que nunca cesan.",
        'anio': 1955,
        'sinopsis': [
            "Juan Preciado llega al pueblo de Colotlan, en Jalisco, siguiendo la carta de su padre, Pedro Paramo, que lo abandono cuando era nino.",
            "Lo encuentra muerto y convertido en un ruido al que la gente del lugar ya esta acostumbrada. El pueblo esta casi vacio: quedan mujeres que repiten frases para siempre y un olor a cajete.",
            "Rulfo escribe en frases cortas y va urdiendo voces que vienen del pasado y del presente, como si el tiempo en Comala no tuviera un solo sentido. La novela es un retrato de un Mexico rural en descomposicion.",
        ],
    },
    {
        'titulo': "El hobbit",
        'autor': "J. R. R. Tolkien",
        'genero': "Fantasia",
        'portada': "el-hobbit.jpg",
        'pdf': "el-hobbit.pdf",
        'descripcion': "Bilbo Baggins, un hobbit tranquilo y sedentario, acaba en una aventura para recuperar el tesoro de un dragon.",
        'anio': 1937,
        'sinopsis': [
            "El hobbit es la puerta de entrada a la Tierra Media. Bilbo Baggins vive en el Shire, un territorio prospero y pacifico, y no desea ninguna aventura. Gandalf, un mago, lo arrastra junto a trece enanos que quieren recuperar el reino de Erebor del dragon Smaug.",
            "Durante el viaje Bilbo se apodera un anillo que vuelve invisible a quien lo usa, y desde ese momento su vida cambia. Lo que empieza como una excursion termina en una batalla en el interior de una montana.",
            "Tolkien construyo un mundo con mapas, idiomas y canciones. La novela es, ante todo, el retrato de alguien que parte cobarde y vuelve valiente.",
        ],
    },
    {
        'titulo': "Harry Potter y la piedra filosofal",
        'autor': "J. K. Rowling",
        'genero': "Fantasia",
        'portada': "harry-potter-piedra-filosofal.jpg",
        'pdf': "harry-potter-piedra-filosofal.pdf",
        'descripcion': "Harry descubre que es un mago a los once anos y entra a Hogwarts, donde conoce a Ron y Hermione.",
        'anio': 1997,
        'sinopsis': [
            "Harry Potter crece en la casa de sus tios sin saber por que sus padres desaparecieron cuando era bebe. En su undecimo cumpleanos recibe una carta que lo invita al colegio de magia Hogwarts.",
            "Alli conoce a Ron Weasley y a Hermione Granger y suelta su primer hechizo sin querer. El problema central es un tesoro escondido bajo tres capas de proteccion dentro del colegio: la piedra filosofal.",
            "Es el primer tomo de una saga de siete libros. Lo que empieza como una aventura escolar se convierte con los anos en un duelo contra Lord Voldemort.",
        ],
    },
    {
        'titulo': "Orgullo y prejuicio",
        'autor': "Jane Austen",
        'genero': "Clasico",
        'portada': "orgullo-y-prejuicio.jpg",
        'pdf': "orgullo-y-prejuicio.pdf",
        'descripcion': "Elizabeth Bennet y el senor Darcy empiezan odiandose y terminan casandose, tras descubrir lo mal que se juzgaban.",
        'anio': 1813,
        'sinopsis': [
            "Elizabeth Bennet es la segunda de cinco hermanas en una familia que no heredo dinero. Austen la describe como inteligente, divertida y con una opinion firme sobre casi todo, empezando por el matrimonio.",
            "En un baile conoce a Fitzwilliam Darcy, un terrateniente rico, orgulloso y frio. Darcy la desprecia en publico y ella se ofende. A partir de ahi comienza una relacion de malentendidos y orgullo mutuo.",
            "La novela explora como juzgamos a los demas a partir de apariencias. Despues de conocer en segunda persona la historia de Darcy, Elizabeth entiende que sus juicios iniciales fueron tan injustos como los de el.",
        ],
    },
    {
        'titulo': "Crimen y castigo",
        'autor': "Fiodor Dostoievski",
        'genero': "Clasico",
        'portada': "crimen-y-castigo.jpg",
        'pdf': "crimen-y-castigo.pdf",
        'descripcion': "Un estudiante pobre comete un asesinato por una idea y pasa meses atormentado hasta que la justicia llega en forma de gracia.",
        'anio': 1866,
        'sinopsis': [
            "Raskolnikov, un estudiante que vive en una barana de San Petersburgo, empuja a una vieja usurera por las escaleras y la roba. Lo hace porque se le ha ocurrido una teoria: que un hombre extraordinario tiene derecho a saltarse las leyes.",
            "El crimen no le da la libertad que buscaba. Le da fiebre, insomnio y la certeza de que no es mas que un vulgar asesino. Se debate entre confesar o seguir mintiendo, y en ese tugur aparece Sonia, una mujer pobre que vive al borde y que le ofrece consuelo.",
            "Dostoievski convierte una novela policial en un examen sobre la conciencia, la culpa y el valor de la redencion.",
        ],
    },
    {
        'titulo': "El nombre de la rosa",
        'autor': "Umberto Eco",
        'genero': "Misterio",
        'portada': "el-nombre-de-la-rosa.jpg",
        'pdf': "el-nombre-de-la-rosa.pdf",
        'descripcion': "Un monasterio medieval se ve perturbado por una serie de muertes y un investigador llega a acompanar a un bibliotecario ciego.",
        'anio': 1980,
        'sinopsis': [
            "Adso de Melk, un joven monje, acompana a su abad William de Baskerville en la biblioteca de una abadia del norte de Italia. Una muerte misteriosa ocurre en el monasterio y William empieza a investigar.",
            "Cada muerte apunta a uno de los libros prohibidos de la biblioteca y deja tras de si un rompecabezas de estilo distinto. El monasterio se convierte en un laberinto: siete pisos, bibliotecas, y un manuscrito que se pierde.",
            "Eco mezcla novela policial, novela medieval y semiologia para preguntarse hasta donde puede llegar el conocimiento antes de convertirse en violencia.",
        ],
    },
    {
        'titulo': "Rayuela",
        'autor': "Julio Cortazar",
        'genero': "Novela",
        'portada': "rayuela.jpg",
        'pdf': "rayuela.pdf",
        'descripcion': "Un grupo de amigos en Paris atraviesa el juego, el azar y el amor en una busqueda que rompe el orden del relato.",
        'anio': 1963,
        'sinopsis': [
            "La novela empieza en Paris con un grupo de amigos. Entre ellos estan Morel, un trumpetista que busca un club, y la mediadora Corte, que propone un juego que rompe las reglas.",
            "El libro esta armado con secciones numeradas y una hojilla pegada: se puede leer de corrido, saltando paginas, siguiendo las flechas y las rayas, o usando el indice como recorrido alternativo.",
            "En medio, un personaje busca un objeto prohibido en un lugar imposible, mientras el viaje atraviesa toda la historia. Es una novela donde la forma es el argumento.",
        ],
    },
    {
        'titulo': "La sombra del viento",
        'autor': "Carlos Ruiz Zafon",
        'genero': "Misterio",
        'portada': "la-sombra-del-viento.jpg",
        'pdf': "la-sombra-del-viento.pdf",
        'descripcion': "Un chico descubre el cementerio de los libros olvidados y ahi encuentra un manuscrito que cambia su vida.",
        'anio': 2001,
        'sinopsis': [
            "Daniel Sempere tiene trece anos y vive en el Barcelona de la posguerra. Su padre es bibliotecario y le lleva de vez en cuando al Cementerio de los Libros Olvidados, un lugar donde los libros que nadie quiere guardan la eternidad.",
            "Entre miles de libros, Daniel encuentra El viento de la sombra, un libro sin autor y de argumento desconocido que alguien ha protegido en secreto. Lo esconde y empieza a ser perseguido por quienes lo buscan.",
            "La novela mezcla fantasia, misterio y aventura. Es el primer volumen de la Trilogia de la Sombra del Viento.",
        ],
    },
]


def build(book):
    titulo = book["titulo"]
    autor = book["autor"]
    genero = book["genero"]
    anio = book["anio"]
    portada = book["portada"]
    pdf_name = book["pdf"]
    sinopsis = "<br/><br/>".join(book["sinopsis"])
    cover_path = os.path.join(PORTADAS_DIR, portada)
    out_path = os.path.join(PDF_DIR, pdf_name)
    os.makedirs(PDF_DIR, exist_ok=True)

    base = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=base["Title"], fontSize=20, leading=25,
                        textColor=INK, spaceAfter=4)
    autor_st = ParagraphStyle("autor", parent=base["Normal"], fontSize=10.5,
                              alignment=TA_CENTER, textColor=INK_SOFT, spaceAfter=2)
    meta_st = ParagraphStyle("meta", parent=base["Normal"], fontSize=8.6,
                             alignment=TA_CENTER, textColor=INK_SOFT)
    seccion = ParagraphStyle("seccion", parent=base["Heading2"], fontSize=12.5,
                             textColor=BRAND, spaceBefore=10, spaceAfter=7)
    cuerpo = ParagraphStyle("cuerpo", parent=base["BodyText"], fontSize=10.3,
                            leading=16.2, textColor=INK, spaceAfter=9,
                            alignment=4)
    pie = ParagraphStyle("pie", parent=base["Normal"], fontSize=8.2,
                         textColor=INK_SOFT, alignment=TA_CENTER)

    doc = SimpleDocTemplate(
        out_path, pagesize=A5,
        leftMargin=18 * 2.83, rightMargin=18 * 2.83,
        topMargin=16 * 2.83, bottomMargin=16 * 2.83,
        title=titulo, author=autor,
    )

    historia = [
        Paragraph(titulo, h1),
        Paragraph(f"por {autor}", autor_st),
        Paragraph(f"{genero} · {anio}", meta_st),
        Spacer(1, 14),
    ]

    if os.path.exists(cover_path):
        with Image.open(cover_path) as img:
            ancho, alto = img.size
        objetivo = 250
        escala = min(objetivo / ancho, 420 / alto)
        historia.append(RLImage(cover_path, width=ancho * escala, height=alto * escala))
        historia.append(Spacer(1, 12))

    historia += [
        Paragraph("De qué trata", seccion),
        Paragraph(sinopsis, cuerpo),
        Paragraph(
            "Esta edición muestra la portada y una sinopsis de la obra como muestra "
            "de lectura. El texto completo no se distribuye en este repositorio.",
            pie,
        ),
    ]

    historia.append(PageBreak())
    historia.append(Paragraph("Cómo leer este libro", seccion))
    historia.append(Paragraph(
        "<b>Paso 1.</b> Entra a la ficha del libro desde el catálogo y pulsa el botón "
        "<i>Leer libro</i>. El visor integrado abre este PDF en el navegador con la "
        "barra de herramientas nativa para pasar de página, hacer zoom o imprimir."
        "<br/><br/>"
        "<b>Paso 2.</b> Si el visor no carga, usa el enlace de la parte inferior para "
        "abrir el archivo en una pestaña nueva."
        "<br/><br/>"
        "<b>Paso 3.</b> Al terminar, vuelve a la ficha y deja una reseña contando qué "
        "te pareció: eso ayuda a otras personas a decidir si lo leen.",
        cuerpo,
    ))
    historia.append(Spacer(1, 10))
    historia.append(Paragraph(
        "Libroteca · Tu biblioteca, organizada", pie
    ))

    doc.build(historia)
    return out_path


if __name__ == "__main__":
    for book in BOOKS:
        path = build(book)
        print(f"OK  {os.path.relpath(path, BASE_DIR)} ({os.path.getsize(path)//1024} KB)")