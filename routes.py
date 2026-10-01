import os
import uuid

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

import models

web_bp = Blueprint("web", __name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
ALLOWED_PDF_EXT = {".pdf"}

os.makedirs(UPLOAD_DIR, exist_ok=True)
PDF_DIR = os.path.join(BASE_DIR, "static", "pdf")
os.makedirs(PDF_DIR, exist_ok=True)


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
    books = [dict(book) for book in models.list_books(search)] if search else [
        dict(book) for book in models.list_books()
    ]
    fav_count = sum(1 for book in books if book["favorito"])
    return render_template("index.html", books=books, search=search, fav_count=fav_count)


@web_bp.route("/libro/<int:book_id>")
def book_detail(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))
    return render_template("book_detail.html", book=dict(book))


@web_bp.route("/leer/<int:book_id>")
def read_book(book_id):
    book = models.get_book(book_id)
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))
    return render_template("read_book.html", book=dict(book))


@web_bp.route("/nuevo", methods=["GET", "POST"])
def add_book():
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

        models.add_book(titulo, autor, genero, anio, descripcion, imagen, pdf)
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

    favorito = models.toggle_favorite(book_id) == 1
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"id": book_id, "favorito": favorito})

    if favorito:
        flash(f"Te gusta «{book['titulo']}».", "success")
    else:
        flash(f"Quitaste «{book['titulo']}» de tus favoritos.", "success")
    return redirect(request.referrer or url_for("web.index"))


@web_bp.route("/proceso")
def proceso():
    return render_template("proceso.html")