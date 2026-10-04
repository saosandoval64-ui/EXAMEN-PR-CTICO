import os
import uuid
from datetime import datetime, timezone

from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import models
from auth import current_user, login_required

web_bp = Blueprint("web", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_PDF_EXT = {".pdf"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
PDF_DIR = os.path.join(BASE_DIR, "static", "pdf")
os.makedirs(PDF_DIR, exist_ok=True)


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def admin_required(view):
    from functools import wraps

    @wraps(view)
    @login_required
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user["es_admin"]:
            abort(403)
        return view(*args, **kwargs)

    return wrapper


def parse_year(raw_year):
    try:
        year = int(raw_year)
    except (TypeError, ValueError):
        return None
    if year < 1000 or year > 3000:
        return None
    return year


def process_image(request):
    file = request.files.get("imagen_file")
    url = request.form.get("imagen_url", "").strip()

    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXT:
            return None, "Formato de imagen no válido. Usa JPG, PNG, GIF, WEBP o SVG."
        fname = uuid.uuid4().hex + ext
        file.save(os.path.join(UPLOAD_DIR, fname))
        return "uploads/" + fname, None

    if url:
        if not url.startswith(("http://", "https://")):
            return None, "La URL de la imagen debe comenzar con http:// o https://"
        return url, None

    return "", None


def remove_image(imagen):
    if imagen and imagen.startswith("uploads/"):
        path = os.path.join(BASE_DIR, "static", imagen)
        if os.path.exists(path):
            os.remove(path)


def remove_pdf(pdf):
    if pdf and pdf.startswith("pdf/"):
        path = os.path.join(BASE_DIR, "static", pdf.lstrip("/"))
        if os.path.exists(path):
            os.remove(path)


def process_pdf(request):
    file = request.files.get("pdf_file")
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_PDF_EXT:
            return None, "Formato de PDF no válido. Usa archivo .pdf."
        fname = uuid.uuid4().hex + ext
        file.save(os.path.join(PDF_DIR, fname))
        return "pdf/" + fname, None
    return "", None


@web_bp.route("/")
def index():
    search = request.args.get("q", "").strip()
    books = [dict(book) for book in models.list_books(search)]
    user = current_user()
    fav_ids = models.favorite_ids(user["id"]) if user else set()

    if user:
        for book in books:
            book["favorito"] = book["id"] in fav_ids

    top_books = [dict(book) for book in models.top_read_books(5)] if not search else []
    if user:
        for book in top_books:
            book["favorito"] = book["id"] in fav_ids

    fav_count = len(fav_ids) if user else sum(1 for book in books if book["favorito"])
    review_count = sum(models.review_stats(book["id"])[0] for book in books)
    return render_template(
        "index.html",
        books=books,
        top_books=top_books,
        search=search,
        fav_count=fav_count,
        review_count=review_count,
    )


@web_bp.route("/mi-cuenta")
@login_required
def mi_cuenta():
    user = current_user()
    stats = models.user_stats(user["id"])
    return render_template(
        "mi_cuenta.html",
        user=user,
        stats=stats,
        favoritos=[dict(b) for b in models.list_favorite_books(user["id"])],
        resenas=[dict(r) for r in models.list_reviews_by_user(user["id"])],
        libros=[dict(b) for b in models.list_books_by_user(user["id"])],
    )


@web_bp.route("/resenas")
def resenas():
    todas = [dict(review) for review in models.list_reviews()]
    raices = [r for r in todas if not r["respuesta_a"]]
    replies = {}
    for review in todas:
        if review["respuesta_a"]:
            replies.setdefault(review["respuesta_a"], []).append(review)

    libros_revisados = {}
    for review in raices:
        entry = libros_revisados.setdefault(
            review["libro_id"],
            {
                "id": review["libro_id"],
                "titulo": review["libro_titulo"],
                "autor": review["libro_autor"],
                "imagen": review["libro_imagen"],
                "total": 0,
                "suma": 0,
                "reseñas": [],
            },
        )
        entry["total"] += 1
        entry["suma"] += review["calificacion"]
        item = dict(review)
        item["respuestas"] = replies.get(review["id"], [])
        entry["reseñas"].append(item)

    grupos = []
    for entry in libros_revisados.values():
        entry["promedio"] = round(entry["suma"] / entry["total"], 1)
        grupos.append(entry)
    grupos.sort(key=lambda item: (-item["total"], -item["promedio"], item["titulo"]))

    promedio_general = (
        round(sum(g["suma"] for g in grupos) / sum(g["total"] for g in grupos), 1)
        if grupos
        else 0.0
    )
    return render_template(
        "resenas.html",
        grupos=grupos,
        total_reviews=len(raices),
        total_replies=len(todas) - len(raices),
        promedio_general=promedio_general,
    )


@web_bp.route("/libro/<int:book_id>")
def book_detail(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))
    total, promedio = models.review_stats(book_id)
    reviews = models.group_reviews(models.list_reviews(book_id))
    return render_template(
        "book_detail.html",
        book=dict(book),
        reviews=reviews,
        review_total=total,
        review_promedio=promedio,
        reply_total=models.reply_count(book_id),
        user=current_user(),
    )


@web_bp.route("/libro/<int:book_id>/resena", methods=["POST"])
def add_review(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))

    user = current_user()
    autor_nombre = request.form.get("autor_nombre", "").strip()
    titulo = request.form.get("titulo", "").strip()
    texto = request.form.get("texto", "").strip()

    if user:
        autor_nombre = user["nombre"]
    elif not autor_nombre:
        flash("Escribe tu nombre para firmar la reseña.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    if not texto:
        flash("La reseña no puede estar vacía.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    try:
        calificacion = int(request.form.get("calificacion", 5))
    except (TypeError, ValueError):
        calificacion = 5
    calificacion = max(1, min(5, calificacion))

    models.add_review(
        book_id=book_id,
        autor_nombre=autor_nombre,
        calificacion=calificacion,
        titulo=titulo,
        texto=texto,
        usuario_id=user["id"] if user else None,
        creado_en=now_iso(),
    )
    flash("¡Reseña publicada! Gracias por compartir tu opinión.", "success")
    return redirect(url_for("web.book_detail", book_id=book_id) + "#resenas")


@web_bp.route("/libro/<int:book_id>/resena/<int:review_id>/responder", methods=["POST"])
def reply_review(book_id, review_id):
    book = models.get_book(book_id)
    parent = models.get_review(review_id)
    if not book or not parent or parent["respuesta_a"]:
        flash("La reseña que quieres responder ya no está disponible.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    user = current_user()
    texto = request.form.get("texto", "").strip()
    autor_nombre = user["nombre"] if user else request.form.get(
        "autor_nombre", ""
    ).strip()

    if not texto:
        flash("La respuesta no puede estar vacía.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    if not user and not autor_nombre:
        flash("Escribe tu nombre para firmar la respuesta.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    models.add_reply(
        book_id=book_id,
        parent_review_id=review_id,
        autor_nombre=autor_nombre,
        texto=texto,
        usuario_id=user["id"] if user else None,
        creado_en=now_iso(),
    )
    flash("Respuesta publicada.", "success")
    return redirect(url_for("web.book_detail", book_id=book_id) + f"#resena-{review_id}")


@web_bp.route("/libro/<int:book_id>/resena/<int:review_id>", methods=["POST"])
def delete_review(book_id, review_id):
    user = current_user()
    review = models.get_review(review_id)
    if not review or review["libro_id"] != book_id:
        flash("La reseña no existe.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    es_autor = user and review["usuario_id"] == user["id"]
    if not (es_autor or (user and user["es_admin"])):
        flash("Solo puedes borrar tus propias reseñas.", "error")
        return redirect(url_for("web.book_detail", book_id=book_id))

    conn = models.connect()
    with conn:
        conn.execute("DELETE FROM resenas WHERE id = ? OR respuesta_a = ?", (review_id, review_id))
    conn.close()
    flash("Reseña eliminada.", "success")
    return redirect(url_for("web.book_detail", book_id=book_id))


@web_bp.route("/leer/<int:book_id>")
def read_book(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))
    if book["pdf"]:
        models.register_read(book_id)
    return render_template("read_book.html", book=dict(book))


@web_bp.route("/nuevo", methods=["GET", "POST"])
def add_book():
    user = current_user()
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        anio = parse_year(request.form.get("anio_publicacion"))
        descripcion = request.form.get("descripcion", "").strip()
        imagen, error = process_image(request)
        pdf, pdf_error = process_pdf(request)

        if pdf_error:
            flash(pdf_error, "error")
            return redirect(url_for("web.add_book"))

        if error:
            flash(error, "error")
            return redirect(url_for("web.add_book"))

        if not all([titulo, autor, genero]):
            flash("Título, autor y género son obligatorios.", "error")
            return redirect(url_for("web.add_book"))

        if anio is None:
            flash("El año de publicación debe ser un número válido.", "error")
            return redirect(url_for("web.add_book"))

        models.add_book(
            titulo, autor, genero, anio, descripcion, imagen, pdf,
            usuario_id=user["id"] if user else None,
        )
        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("web.index"))

    return render_template("add_book.html")


@web_bp.route("/editar/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))
    book = dict(book)

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        anio = parse_year(request.form.get("anio_publicacion"))
        descripcion = request.form.get("descripcion", "").strip()
        imagen, error = process_image(request)
        pdf, pdf_error = process_pdf(request)

        if pdf_error:
            flash(pdf_error, "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        if error:
            flash(error, "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        if not all([titulo, autor, genero]):
            flash("Título, autor y género son obligatorios.", "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        if anio is None:
            flash("El año de publicación debe ser un número válido.", "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        if imagen == "":
            imagen = book["imagen"]
        elif book["imagen"].startswith("uploads/"):
            remove_image(book["imagen"])

        if pdf and pdf != book.get("pdf", ""):
            # Remove old PDF if exists and new one uploaded
            old_pdf = book.get("pdf", "")
            if old_pdf and old_pdf.startswith("pdf/"):
                old_path = os.path.join(BASE_DIR, "static", old_pdf.lstrip("/"))
                if os.path.exists(old_path):
                    os.remove(old_path)

        models.update_book(book_id, titulo, autor, genero, anio, descripcion, imagen, pdf)
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("web.index"))

    return render_template("edit_book.html", book=book)


@web_bp.route("/eliminar/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))

    remove_image(book["imagen"])
    models.delete_book(book_id)
    flash("Libro eliminado correctamente.", "success")
    return redirect(url_for("web.index"))


@web_bp.route("/gustar/<int:book_id>", methods=["POST"])
def like_book(book_id):
    book = models.get_book(book_id)
    if not book:
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"error": "El libro no existe."}), 404
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))

    user = current_user()
    if user:
        favorito = models.toggle_favorite_user(user["id"], book_id, now_iso())
    else:
        favorito = models.toggle_favorite(book_id) == 1

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"id": book_id, "favorito": favorito})

    if favorito:
        flash(f"Te gusta «{book['titulo']}».", "success")
    else:
        flash(f"Quitaste «{book['titulo']}» de tus favoritos.", "success")
    return redirect(request.referrer or url_for("web.index"))


@web_bp.route("/admin")
@admin_required
def admin_panel():
    return render_template(
        "admin.html",
        stats=models.admin_stats(),
        usuarios=[dict(u) for u in models.list_users()],
        libros=[dict(b) for b in models.list_books()],
        resenas=[
            dict(r)
            for r in models.list_reviews()
        ],
    )


@web_bp.route("/admin/usuario/<int:user_id>/bloquear", methods=["POST"])
@admin_required
def admin_block_user(user_id):
    admin = current_user()
    if user_id == admin["id"]:
        flash("No puedes bloquear tu propia cuenta de administradora.", "error")
        return redirect(url_for("web.admin_panel"))

    target = models.get_user(user_id)
    if not target:
        flash("La cuenta no existe.", "error")
        return redirect(url_for("web.admin_panel"))

    bloquear = not target["bloqueado"]
    models.set_user_blocked(user_id, bloquear)
    verb = "bloqueada" if bloquear else "desbloqueada"
    flash(f"Cuenta de {target['nombre']} {verb}.", "success")
    return redirect(url_for("web.admin_panel"))


@web_bp.route("/admin/usuario/<int:user_id>/eliminar", methods=["POST"])
@admin_required
def admin_delete_user(user_id):
    admin = current_user()
    if user_id == admin["id"]:
        flash("No puedes eliminar tu propia cuenta de administradora.", "error")
        return redirect(url_for("web.admin_panel"))

    target = models.get_user(user_id)
    if not target:
        flash("La cuenta no existe.", "error")
        return redirect(url_for("web.admin_panel"))

    models.delete_user(user_id)
    flash(f"Cuenta de {target['nombre']} eliminada.", "success")
    return redirect(url_for("web.admin_panel"))


@web_bp.route("/admin/libro/<int:book_id>/eliminar", methods=["POST"])
@admin_required
def admin_delete_book(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.admin_panel"))

    remove_image(book["imagen"])
    remove_pdf(book["pdf"])
    models.delete_book(book_id)
    flash(f"«{book['titulo']}» se eliminó por no cumplir los términos.", "success")
    return redirect(url_for("web.admin_panel"))


@web_bp.route("/admin/resena/<int:review_id>/eliminar", methods=["POST"])
@admin_required
def admin_delete_review(review_id):
    review = models.get_review(review_id)
    if not review:
        flash("La reseña no existe.", "error")
        return redirect(url_for("web.admin_panel"))

    conn = models.connect()
    with conn:
        conn.execute(
            "DELETE FROM resenas WHERE id = ? OR respuesta_a = ?", (review_id, review_id)
        )
    conn.close()
    flash("Reseña eliminada por moderación.", "success")
    return redirect(url_for("web.admin_panel"))


@web_bp.route("/proceso")
def proceso():
    return render_template("proceso.html")