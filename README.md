# Libroteca · Gestión de Biblioteca

Aplicación web para gestionar una biblioteca de libros construida para el **Examen práctico de Desarrollo de Aplicaciones Web** (Tecnológico Universitario Espíritu Santo).

Permite **listar, buscar, agregar, actualizar y eliminar** libros mediante una interfaz web amigable y una **API RESTful**. Incluye además una **ficha de detalle por libro** (con portada e imagen), **portadas de los libros**, **descripciones**, búsqueda desde la barra de navegación y una página de **documentación del proceso** (`/proceso`).

## Tecnologías utilizadas

| Tecnología      | Uso                                       |
| --------------- | ----------------------------------------- |
| **Python 3**    | Lenguaje de programación                  |
| **Flask**       | Framework web                             |
| **Flask-RESTful** | Construcción de la API RESTful            |
| **SQLite**      | Base de datos (módulo `sqlite3` de Python) |
| **Jinja2**      | Motor de plantillas HTML (incluido con Flask) |
| **CSS3 / JavaScript** | Diseño, usabilidad e interactividad   |

## Funcionalidades

- **Listado de libros**: tarjetas con portada, título, autor, género, año y un extracto de la descripción.
- **Ficha de detalle**: al hacer clic en una tarjeta se abre la ficha del libro con la portada en grande y un texto explicativo.
- **Búsqueda**: por título, autor o género (y también por descripción), desde una caja fija en la barra de navegación.
- **Agregar libros**: formulario con título, autor, género, año, descripción y portada.
- **Portadas**: se puede subir una imagen desde la computadora (se guarda en `static/uploads/`) o pegar la URL de una imagen. Si no hay portada, se genera una automática con el título y las iniciales del autor.
- **Actualizar libros**: edición completa, conservando la portada si no se proporciona otra.
- **Eliminar libros**: con confirmación antes de eliminar (también borra la imagen subida).
- **API RESTful completa**: `GET`, `POST`, `PUT` y `DELETE`.
- **Página "Cómo se hizo"** en `/proceso`: documenta lo que pidió la universidad, los pasos seguidos, las decisiones agregadas, la estructura del código, el esquema de la base de datos, la API y cómo ejecutar el proyecto.

## Estructura del proyecto

```
biblioteca/
├── app.py              # Punto de entrada: crea la app, registra rutas y la API
├── models.py           # Modelo Libro y operaciones de la base de datos SQLite
├── routes.py           # Rutas web (catálogo, búsqueda, detalle, CRUD, proceso)
├── api.py              # API RESTful con Flask-RESTful
├── seed.py             # (Opcional) Carga libros de ejemplo con portada y descripción
├── requirements.txt    # Dependencias del proyecto
├── README.md
├── database.db         # Base de datos SQLite (se crea automáticamente)
├── static/
│   ├── style.css       # Hoja de estilos de la aplicación
│   └── uploads/        # Portadas subidas desde los formularios
└── templates/
    ├── base.html           # Plantilla base (nav con buscador, mensajes)
    ├── index.html          # Catálogo de libros (tarjetas)
    ├── book_detail.html    # Ficha del libro con portada y descripción
    ├── add_book.html       # Formulario para agregar un libro
    ├── edit_book.html      # Formulario para editar un libro
    └── proceso.html        # Documentación del proceso ("Cómo se hizo")
```

## Requisitos previos

- Python **3.8 o superior** instalado.
- **pip** disponible (incluido en la mayoría de instalaciones de Python).

## Cómo ejecutar la aplicación

### 1. Clonar o descargar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd biblioteca
```

O simplemente ubicarse en la carpeta del proyecto desde la terminal.

### 2. Crear un entorno virtual

**Linux / macOS:**

```bash
python3 -m venv .venv
```

**Windows:**

```bash
py -m venv .venv
```

### 3. Activar el entorno virtual

```bash
# Linux / macOS
source .venv/bin/activate

# Windows (Git Bash o PowerShell)
.venv\Scripts\activate
```

### 4. Instalar las dependencias

```bash
pip install -r requirements.txt
```

Esto instala **Flask** y **Flask-RESTful**. La base de datos SQLite no necesita instaladores adicionales: Python incluye el conector `sqlite3` de forma nativa.

### 5. (Opcional) Cargar libros de ejemplo

```bash
python seed.py
```

Agrega 10 libros de ejemplo con **portadas reales** (API abierta de Open Library) y **descripciones** para que el catálogo no inicie vacío. Si estás sin internet, las tarjetas muestran una portada automática.

### 6. Ejecutar la aplicación

```bash
python app.py
```

La base de datos `database.db` se crea automáticamente la primera vez.

### 7. Abrir la aplicación

- Aplicación web: <http://127.0.0.1:5000>
- Ficha de un libro: <http://127.0.0.1:5000/libro/1>
- Documentación del proceso: <http://127.0.0.1:5000/proceso>
- API: <http://127.0.0.1:5000/api/books>

Para detener el servidor, presiona `Ctrl + C` en la terminal.

## Rutas web (interfaz de usuario)

| Método | Ruta             | Descripción                                   |
| ------ | ---------------- | --------------------------------------------- |
| GET    | `/`              | Lista todos los libros                        |
| GET    | `/?q=<texto>`    | Busca por título, autor, género o descripción |
| GET    | `/libro/<id>`    | Ficha del libro (portada + descripción)       |
| GET    | `/nuevo`         | Formulario para agregar un libro              |
| POST   | `/nuevo`         | Guarda el libro nuevo                         |
| GET    | `/editar/<id>`   | Formulario de edición de un libro             |
| POST   | `/editar/<id>`   | Guarda los cambios del libro                  |
| POST   | `/eliminar/<id>` | Elimina el libro (con confirmación)           |
| GET    | `/proceso`       | Documentación del proceso de desarrollo       |

## API RESTful

Todas las rutas de la API usan el prefijo `/api`.

### Endpoints

| Método | Endpoint              | Descripción                             | Código de respuesta |
| ------ | --------------------- | --------------------------------------- | ------------------- |
| GET    | `/api/books`          | Lista todos los libros                  | 200                 |
| GET    | `/api/books?q=texto`  | Busca libros por título/autor/género    | 200                 |
| GET    | `/api/books/<id>`     | Obtiene un libro por su id              | 200 / 404           |
| POST   | `/api/books`          | Crea un nuevo libro                     | 201 / 400           |
| PUT    | `/api/books/<id>`     | Actualiza un libro existente            | 200 / 400 / 404     |
| DELETE | `/api/books/<id>`     | Elimina un libro por su id              | 200 / 404           |

Formato de un libro en la API:

```json
{
  "id": 1,
  "titulo": "Cien años de soledad",
  "autor": "Gabriel García Márquez",
  "genero": "Novela",
  "anio_publicacion": 1967,
  "descripcion": "La obra maestra del realismo mágico…",
  "imagen": "https://covers.openlibrary.org/b/isbn/9780307474728-L.jpg"
}
```

> Nota: la columna `anio_publicacion` usa `anio` en lugar de `año` para evitar problemas con la letra "ñ" en SQLite.

### Ejemplos con `curl`

Listar todos los libros:

```bash
curl http://127.0.0.1:5000/api/books
```

Buscar libros por título, autor o género:

```bash
curl "http://127.0.0.1:5000/api/books?q=novela"
```

Obtener un libro por id:

```bash
curl http://127.0.0.1:5000/api/books/1
```

Agregar un libro:

```bash
curl -X POST http://127.0.0.1:5000/api/books \
  -H "Content-Type: application/json" \
  -d '{"titulo":"Rayuela","autor":"Julio Cortázar","genero":"Novela","anio_publicacion":1963,"descripcion":"Una novela abierta que se lee de muchas formas.","imagen":"https://ejemplo.com/portada.jpg"}'
```

Actualizar un libro (se envían solo los campos que se quieren cambiar):

```bash
curl -X PUT http://127.0.0.1:5000/api/books/1 \
  -H "Content-Type: application/json" \
  -d '{"genero":"Clásico"}'
```

Eliminar un libro:

```bash
curl -X DELETE http://127.0.0.1:5000/api/books/1
```

## Base de datos

La tabla `libros` se crea así:

```sql
CREATE TABLE IF NOT EXISTS libros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    genero TEXT NOT NULL,
    anio_publicacion INTEGER NOT NULL,
    descripcion TEXT NOT NULL DEFAULT '',
    imagen TEXT NOT NULL DEFAULT ''
);
```

Para inspeccionar la base de datos manualmente:

```bash
sqlite3 database.db "SELECT * FROM libros;"
```

## Cómo se hizo

El desarrollo siguió estas etapas, tal y como se documenta en detalle en la página [`/proceso`](http://127.0.0.1:5000/proceso):

1. **Planteamiento y lectura del enunciado** → se identificó que el examen pedía una gestión de biblioteca con interfaz web + API RESTful y una página que explicara el proceso.
2. **Diseño de la base de datos** → tabla `libros` en SQLite con las columnas pedidas (título, autor, género, año) más `descripcion`, `imagen` y `favorito` para enriquecer la ficha.
3. **Stack y arranque del proyecto** → Flask + Flask-RESTful + Jinja2 sobre Python 3, sin frameworks de CSS para demostrar maquetación manual.
4. **Interfaz web** → catálogo con tarjetas y portadas, búsqueda desde la barra, formularios para agregar/editar con validaciones, ficha de detalle, confirmación al eliminar y feedback con mensajes flash.
5. **API RESTful** → `GET/POST/PUT/DELETE` sobre `/api/books` con Flask-RESTful, códigos de estado correctos y respuestas JSON.
6. **Datos de ejemplo y portadas** → script `seed.py` que carga libros reales con portadas locales (`static/portadas/`) para que la biblioteca no arranque vacía.
7. **Pruebas y pulido** → verificación de cada ruta con `curl`, revisión responsive en móvil (menú drawer + grillas adaptivas), naturalización de los textos y confirmación de los criterios del checklist de abajo.

Todas las decisiones de diseño están explicadas paso a paso en la página **Cómo se hizo** del sitio.

## Criterios de evaluación (checklist)

- [x] Listado de libros
- [x] Búsqueda por título, autor o género
- [x] Agregar libro
- [x] Actualizar libro
- [x] Eliminar libro
- [x] `GET /api/books`
- [x] `GET /api/books/<id>`
- [x] `POST /api/books`
- [x] `PUT /api/books/<id>`
- [x] `DELETE /api/books/<id>`
- [x] Base de datos SQLite funcional
- [x] README en GitHub
- [x] Repositorio subido

**Extras agregados (no pedidos, para mejorar el diseño y la usabilidad):** ficha de detalle con portada y descripción, búsqueda en la barra de navegación, subir imagen por archivo o URL, portadas automáticas, datos de ejemplo con portadas reales, validaciones de campos, confirmación al eliminar, responsive y página de documentación del proceso.

---

**Tecnológico Universitario Espíritu Santo** · Desarrollo de Aplicaciones Web · Examen práctico