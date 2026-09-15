# BiblioTech · Gestión de Biblioteca

Aplicación web para gestionar una biblioteca de libros construida para el **Examen práctico de Desarrollo de Aplicaciones Web** (Tecnológico Universitario Espíritu Santo).

Permite **listar, buscar, agregar, actualizar y eliminar** libros mediante una interfaz web amigable y una **API RESTful**.

## Tecnologías utilizadas

| Tecnología      | Uso                                       |
| --------------- | ----------------------------------------- |
| **Python 3**    | Lenguaje de programación                  |
| **Flask**       | Framework web                             |
| **Flask-RESTful** | Construcción de la API RESTful            |
| **SQLite**      | Base de datos (módulo `sqlite3` de Python) |
| **Jinja2**      | Motor de plantillas HTML (incluido con Flask) |
| **CSS**         | Diseño y usabilidad de la interfaz        |

## Funcionalidades

- **Listado de libros**: muestra todos los libros con título, autor, género y año de publicación.
- **Búsqueda**: por título, autor o género (una sola caja de búsqueda).
- **Agregar libros**: formulario con validación de todos los campos.
- **Actualizar libros**: edición completa de cualquier libro existente.
- **Eliminar libros**: con confirmación antes de eliminar.
- **API RESTful completa**: `GET`, `POST`, `PUT` y `DELETE`.

## Estructura del proyecto

```
biblioteca/
├── app.py              # Punto de entrada: crea la app, registra rutas y la API
├── models.py           # Modelo Libro y operaciones de la base de datos SQLite
├── routes.py           # Rutas web (listar, buscar, agregar, editar, eliminar)
├── api.py              # API RESTful con Flask-RESTful
├── seed.py             # (Opcional) Carga libros de ejemplo en la base de datos
├── requirements.txt    # Dependencias del proyecto
├── README.md
├── database.db         # Base de datos SQLite (se crea automáticamente)
├── static/
│   └── style.css       # Hoja de estilos de la aplicación
└── templates/
    ├── base.html       # Plantilla base (cabecera, navegación, mensajes)
    ├── index.html      # Listado de libros + búsqueda
    ├── add_book.html   # Formulario para agregar un libro
    └── edit_book.html  # Formulario para editar un libro
```

## Requisitos previos

- Python **3.8 o superior** instalado.
- **pip** disponible (en la mayoría de instalaciones de Python viene incluido).

## Cómo ejecutar la aplicación

### 1. Clonar o descargar el proyecto

```bash
git clone <URL_DEL_REPOSITORIO>
cd biblioteca
```

O simplemente ubicarse en la carpeta del proyecto desde la terminal.

### 2. Crear un entorno virtual

En **Linux / macOS**:

```bash
python3 -m venv .venv
```

En **Windows**:

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

Agrega 10 libros de ejemplo para que el catálogo no inicie vacío.

### 6. Ejecutar la aplicación

```bash
python app.py
```

La base de datos `database.db` se crea automáticamente la primera vez.

### 7. Abrir la aplicación

- Aplicación web: <http://127.0.0.1:5000>
- API: <http://127.0.0.1:5000/api/books>

Para detener el servidor, presiona `Ctrl + C` en la terminal.

## Rutas web (interfaz de usuario)

| Método | Ruta            | Descripción                                   |
| ------ | --------------- | --------------------------------------------- |
| GET    | `/`             | Lista todos los libros                        |
| GET    | `/?q=<texto>`   | Busca libros por título, autor o género       |
| GET    | `/nuevo`        | Muestra el formulario para agregar un libro   |
| POST   | `/nuevo`        | Guarda el libro nuevo                         |
| GET    | `/editar/<id>`  | Muestra el formulario de edición de un libro  |
| POST   | `/editar/<id>`  | Guarda los cambios del libro                  |
| POST   | `/eliminar/<id>`| Elimina el libro (con confirmación)           |

## API RESTful

Todas las rutas de la API usan el prefijo `/api`.

### Endpoints

| Método | Endpoint              | Descripción                                  | Código de respuesta |
| ------ | --------------------- | -------------------------------------------- | ------------------- |
| GET    | `/api/books`          | Lista todos los libros                       | 200                 |
| GET    | `/api/books/<id>`     | Obtiene un libro por su id                   | 200 / 404           |
| POST   | `/api/books`          | Crea un nuevo libro                          | 201 / 400           |
| PUT    | `/api/books/<id>`     | Actualiza un libro existente                 | 200 / 404 / 400     |
| DELETE | `/api/books/<id>`     | Elimina un libro por su id                   | 200 / 404           |

Formato de un libro en la API:

```json
{
  "id": 1,
  "titulo": "Cien años de soledad",
  "autor": "Gabriel García Márquez",
  "genero": "Novela",
  "anio_publicacion": 1967
}
```

> Nota: la columna `anio_publicacion` usa `anio` en lugar de `año` para evitar problemas con la letra "ñ" en la base de datos.

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
  -d '{"titulo":"Rayuela","autor":"Julio Cortázar","genero":"Novela","anio_publicacion":1963}'
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
    anio_publicacion INTEGER NOT NULL
);
```

Para inspeccionar la base de datos manualmente:

```bash
sqlite3 database.db "SELECT * FROM libros;"
```

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

---

**Tecnológico Universitario Espíritu Santo** · Desarrollo de Aplicaciones Web · Examen práctico