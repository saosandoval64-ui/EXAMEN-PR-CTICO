import sqlite3

DATABASE = "database.db"


def connect():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def _columns(conn, table):
    return {row["name"] for row in conn.execute(f"PRAGMA table_info({table})")}


def _add_missing_columns(conn):
    changes = {
        "libros": {
            "lecturas": "INTEGER NOT NULL DEFAULT 0",
            "usuario_id": "INTEGER",
        },
        "usuarios": {
            "google_id": "TEXT",
            "avatar_url": "TEXT NOT NULL DEFAULT ''",
            "verificado": "INTEGER NOT NULL DEFAULT 0",
            "es_admin": "INTEGER NOT NULL DEFAULT 0",
            "bloqueado": "INTEGER NOT NULL DEFAULT 0",
            "codigo_verificacion": "TEXT NOT NULL DEFAULT ''",
            "creado_en": "TEXT NOT NULL DEFAULT ''",
        },
        "resenas": {
            "respuesta_a": "INTEGER",
        },
    }
    for table, columns in changes.items():
        existing = _columns(conn, table)
        if not existing:
            continue
        for column, ddl in columns.items():
            if column not in existing:
                conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}")
    conn.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS idx_usuarios_google ON usuarios (google_id)"
    )


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
                pdf TEXT NOT NULL DEFAULT '',
                favorito INTEGER NOT NULL DEFAULT 0,
                lecturas INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                clave_hash TEXT NOT NULL DEFAULT '',
                google_id TEXT UNIQUE,
                avatar_url TEXT NOT NULL DEFAULT '',
                verificado INTEGER NOT NULL DEFAULT 0,
                es_admin INTEGER NOT NULL DEFAULT 0,
                codigo_verificacion TEXT NOT NULL DEFAULT '',
                creado_en TEXT NOT NULL DEFAULT ''
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS resenas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                libro_id INTEGER NOT NULL,
                usuario_id INTEGER,
                autor_nombre TEXT NOT NULL,
                calificacion INTEGER NOT NULL,
                titulo TEXT NOT NULL DEFAULT '',
                texto TEXT NOT NULL,
                creado_en TEXT NOT NULL DEFAULT '',
                respuesta_a INTEGER,
                FOREIGN KEY (libro_id) REFERENCES libros (id) ON DELETE CASCADE,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE SET NULL,
                FOREIGN KEY (respuesta_a) REFERENCES resenas (id) ON DELETE CASCADE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS favoritos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                libro_id INTEGER NOT NULL,
                creado_en TEXT NOT NULL DEFAULT '',
                UNIQUE (usuario_id, libro_id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE,
                FOREIGN KEY (libro_id) REFERENCES libros (id) ON DELETE CASCADE
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_resenas_libro ON resenas (libro_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_resenas_padre ON resenas (respuesta_a)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_libros_usuario ON libros (usuario_id)")
        _add_missing_columns(conn)
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


def top_read_books(limit=5):
    conn = connect()
    rows = conn.execute(
        """
        SELECT * FROM libros
        ORDER BY lecturas DESC, titulo COLLATE NOCASE
        LIMIT ?
        """,
        (limit,),
    ).fetchall()
    conn.close()
    return rows


def register_read(book_id):
    conn = connect()
    with conn:
        conn.execute("UPDATE libros SET lecturas = lecturas + 1 WHERE id = ?", (book_id,))
    conn.close()


def get_book(book_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM libros WHERE id = ?", (book_id,)
    ).fetchone()
    conn.close()
    return row


def add_book(titulo, autor, genero, anio, descripcion="", imagen="", pdf="",
             usuario_id=None):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO libros
                (titulo, autor, genero, anio_publicacion, descripcion, imagen, pdf, usuario_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (titulo, autor, genero, anio, descripcion, imagen, pdf, usuario_id),
        )
    conn.close()
    return cur.lastrowid


def update_book(book_id, titulo, autor, genero, anio, descripcion, imagen, pdf=""):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            UPDATE libros
            SET titulo = ?, autor = ?, genero = ?, anio_publicacion = ?,
                descripcion = ?, imagen = ?, pdf = ?
            WHERE id = ?
            """,
            (titulo, autor, genero, anio, descripcion, imagen, pdf, book_id),
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


# --- Usuarios ---------------------------------------------------------------


def get_user_by_correo(correo):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE correo = ? COLLATE NOCASE", (correo,)
    ).fetchone()
    conn.close()
    return row


def get_user_by_google_id(google_id):
    conn = connect()
    row = conn.execute(
        "SELECT * FROM usuarios WHERE google_id = ?", (google_id,)
    ).fetchone()
    conn.close()
    return row


def get_user(user_id):
    conn = connect()
    row = conn.execute("SELECT * FROM usuarios WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return row


def create_user(nombre, correo, clave_hash="", google_id=None, avatar_url="",
                verificado=0, es_admin=0, codigo_verificacion="", creado_en=""):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO usuarios
                (nombre, correo, clave_hash, google_id, avatar_url, verificado,
                 es_admin, codigo_verificacion, creado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (nombre, correo, clave_hash, google_id, avatar_url, verificado,
             es_admin, codigo_verificacion, creado_en),
        )
    conn.close()
    return cur.lastrowid


def set_verification_code(user_id, codigo):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE usuarios SET codigo_verificacion = ? WHERE id = ?", (codigo, user_id)
        )
    conn.close()


def mark_user_verified(user_id):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE usuarios SET verificado = 1, codigo_verificacion = '' WHERE id = ?",
            (user_id,),
        )
    conn.close()


def link_google_account(user_id, google_id, avatar_url=""):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE usuarios SET google_id = ?, avatar_url = ?, verificado = 1 WHERE id = ?",
            (google_id, avatar_url, user_id),
        )
    conn.close()


def set_user_password(user_id, clave_hash):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE usuarios SET clave_hash = ?, verificado = 1 WHERE id = ?",
            (clave_hash, user_id),
        )
    conn.close()


# --- Reseñas ----------------------------------------------------------------


def add_review(book_id, autor_nombre, calificacion, titulo, texto, usuario_id=None,
               creado_en=""):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO resenas
                (libro_id, usuario_id, autor_nombre, calificacion, titulo, texto, creado_en)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (book_id, usuario_id, autor_nombre, calificacion, titulo, texto, creado_en),
        )
    conn.close()
    return cur.lastrowid


def list_reviews(book_id=None):
    conn = connect()
    if book_id is None:
        rows = conn.execute(
            """
            SELECT r.*, l.titulo AS libro_titulo, l.autor AS libro_autor, l.imagen AS libro_imagen
            FROM resenas r
            JOIN libros l ON l.id = r.libro_id
            ORDER BY r.creado_en DESC, r.id DESC
            """
        ).fetchall()
    else:
        rows = conn.execute(
            """
            SELECT r.*, l.titulo AS libro_titulo, l.autor AS libro_autor, l.imagen AS libro_imagen
            FROM resenas r
            JOIN libros l ON l.id = r.libro_id
            WHERE r.libro_id = ?
            ORDER BY r.creado_en DESC, r.id DESC
            """,
            (book_id,),
        ).fetchall()
    conn.close()
    return rows


def review_stats(book_id):
    conn = connect()
    row = conn.execute(
        """
        SELECT COUNT(*) AS total, COALESCE(AVG(calificacion), 0) AS promedio
        FROM resenas WHERE libro_id = ? AND respuesta_a IS NULL
        """,
        (book_id,),
    ).fetchone()
    conn.close()
    return (row["total"], round(row["promedio"], 1)) if row else (0, 0.0)


# --- Respuestas a reseñas ----------------------------------------------------


def add_reply(book_id, parent_review_id, autor_nombre, texto, usuario_id=None,
              creado_en=""):
    conn = connect()
    with conn:
        cur = conn.execute(
            """
            INSERT INTO resenas
                (libro_id, usuario_id, autor_nombre, calificacion, titulo, texto,
                 creado_en, respuesta_a)
            VALUES (?, ?, ?, 5, '', ?, ?, ?)
            """,
            (book_id, usuario_id, autor_nombre, texto, creado_en, parent_review_id),
        )
    conn.close()
    return cur.lastrowid


def get_review(review_id):
    conn = connect()
    row = conn.execute("SELECT * FROM resenas WHERE id = ?", (review_id,)).fetchone()
    conn.close()
    return row


def group_reviews(rows):
    """Separa las reseñas raíz de sus respuestas y anida el árbol."""
    replies = {}
    for row in rows:
        if row["respuesta_a"]:
            replies.setdefault(row["respuesta_a"], []).append(row)

    roots = []
    for row in rows:
        if row["respuesta_a"]:
            continue
        item = dict(row)
        item["respuestas"] = replies.get(row["id"], [])
        roots.append(item)
    return roots


def reply_count(book_id):
    conn = connect()
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM resenas WHERE libro_id = ? AND respuesta_a IS NOT NULL",
        (book_id,),
    ).fetchone()
    conn.close()
    return row["n"] if row else 0


# --- Favoritos por usuario ---------------------------------------------------


def toggle_favorite_user(user_id, book_id, creado_en=""):
    conn = connect()
    with conn:
        existing = conn.execute(
            "SELECT id FROM favoritos WHERE usuario_id = ? AND libro_id = ?",
            (user_id, book_id),
        ).fetchone()
        if existing:
            conn.execute("DELETE FROM favoritos WHERE id = ?", (existing["id"],))
            activo = False
        else:
            conn.execute(
                "INSERT INTO favoritos (usuario_id, libro_id, creado_en) VALUES (?, ?, ?)",
                (user_id, book_id, creado_en),
            )
            activo = True
    conn.close()
    return activo


def favorite_ids(user_id):
    conn = connect()
    rows = conn.execute(
        "SELECT libro_id FROM favoritos WHERE usuario_id = ?", (user_id,)
    ).fetchall()
    conn.close()
    return {row["libro_id"] for row in rows}


def list_favorite_books(user_id):
    conn = connect()
    rows = conn.execute(
        """
        SELECT l.* FROM favoritos f
        JOIN libros l ON l.id = f.libro_id
        WHERE f.usuario_id = ?
        ORDER BY l.titulo COLLATE NOCASE
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


# --- Perfil y moderación -----------------------------------------------------


def list_books_by_user(user_id):
    conn = connect()
    rows = conn.execute(
        """
        SELECT * FROM libros
        WHERE usuario_id = ?
        ORDER BY titulo COLLATE NOCASE
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def list_reviews_by_user(user_id):
    conn = connect()
    rows = conn.execute(
        """
        SELECT r.*, l.titulo AS libro_titulo, l.autor AS libro_autor
        FROM resenas r
        JOIN libros l ON l.id = r.libro_id
        WHERE r.usuario_id = ?
        ORDER BY r.creado_en DESC, r.id DESC
        """,
        (user_id,),
    ).fetchall()
    conn.close()
    return rows


def user_stats(user_id):
    conn = connect()
    row = conn.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM favoritos WHERE usuario_id = :uid) AS favoritos,
            (SELECT COUNT(*) FROM resenas WHERE usuario_id = :uid AND respuesta_a IS NULL)
                AS resenas,
            (SELECT COUNT(*) FROM resenas WHERE usuario_id = :uid AND respuesta_a IS NOT NULL)
                AS respuestas,
            (SELECT COUNT(*) FROM libros WHERE usuario_id = :uid) AS libros
        """,
        {"uid": user_id},
    ).fetchone()
    conn.close()
    return dict(row) if row else {"favoritos": 0, "resenas": 0, "respuestas": 0, "libros": 0}


def list_users():
    conn = connect()
    rows = conn.execute(
        """
        SELECT u.*,
            (SELECT COUNT(*) FROM resenas WHERE usuario_id = u.id) AS total_resenas,
            (SELECT COUNT(*) FROM libros WHERE usuario_id = u.id) AS total_libros
        FROM usuarios u
        ORDER BY u.creado_en DESC, u.id DESC
        """
    ).fetchall()
    conn.close()
    return rows


def set_user_blocked(user_id, bloqueado):
    conn = connect()
    with conn:
        conn.execute(
            "UPDATE usuarios SET bloqueado = ? WHERE id = ?",
            (1 if bloqueado else 0, user_id),
        )
    conn.close()


def delete_user(user_id):
    conn = connect()
    with conn:
        conn.execute("DELETE FROM favoritos WHERE usuario_id = ?", (user_id,))
        conn.execute("DELETE FROM resenas WHERE usuario_id = ?", (user_id,))
        conn.execute("UPDATE libros SET usuario_id = NULL WHERE usuario_id = ?", (user_id,))
        cur = conn.execute("DELETE FROM usuarios WHERE id = ?", (user_id,))
    conn.close()
    return cur.rowcount


def admin_stats():
    conn = connect()
    row = conn.execute(
        """
        SELECT
            (SELECT COUNT(*) FROM libros) AS libros,
            (SELECT COUNT(*) FROM usuarios) AS usuarios,
            (SELECT COUNT(*) FROM usuarios WHERE verificado = 1) AS verificados,
            (SELECT COUNT(*) FROM usuarios WHERE bloqueado = 1) AS bloqueados,
            (SELECT COUNT(*) FROM resenas WHERE respuesta_a IS NULL) AS resenas,
            (SELECT COUNT(*) FROM resenas WHERE respuesta_a IS NOT NULL) AS respuestas
        """
    ).fetchone()
    conn.close()
    return dict(row) if row else {}