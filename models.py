import sqlite3

DATABASE = "database.db"


def connect():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    with conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS libros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                autor TEXT NOT NULL,
                genero TEXT NOT NULL,
                anio_publicacion INTEGER NOT NULL,
                descripcion TEXT NOT NULL DEFAULT '',
                imagen TEXT NOT NULL DEFAULT '',
                favorito INTEGER NOT NULL DEFAULT 0
            )
            """
        )
    conn.close()


def list_books(search=None):
    conn = connect()
    if search:
        like = f"%{search}%"
        rows = conn.execute(
            """
            SELECT * FROM libros
            WHERE titulo LIKE ? OR autor LIKE ? OR genero LIKE ? OR descripcion LIKE ?
            ORDER BY titulo COLLATE NOCASE
            """,
            (like, like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM libros ORDER BY titulo COLLATE NOCASE"
        ).fetchall()
    conn.close()
    return rows


def get_book(book_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM libros WHERE id = ?", (book_id,)
    ).fetchone()
    conn.close()
    return row


def add_book(titulo, autor, genero, anio, descripcion="", imagen=""):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO libros (titulo, autor, genero, anio_publicacion, descripcion, imagen)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (titulo, autor, genero, anio, descripcion, imagen),
        )
    conn.close()
    return cur.lastrowid


def update_book(book_id, titulo, autor, genero, anio, descripcion, imagen):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            UPDATE libros
            SET titulo = ?, autor = ?, genero = ?, anio_publicacion = ?,
                descripcion = ?, imagen = ?
            WHERE id = ?
            """,
            (titulo, autor, genero, anio, descripcion, imagen, book_id),
        )
    conn.close()
    return cur.rowcount


def delete_book(book_id):
    conn = connect()
    with conn:
        cur = conn.execute("DELETE FROM libros WHERE id = ?", (book_id,))
    conn.close()
    return cur.rowcount


def toggle_favorite(book_id):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE libros SET favorito = 1 - favorito WHERE id = ?", (book_id,)
        )
        value = conn.execute(
            "SELECT favorito FROM libros WHERE id = ?", (book_id,)
        ).fetchone()
    conn.close()
    return value[0] if value else None