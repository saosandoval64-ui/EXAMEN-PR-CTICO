from flask import Blueprint, flash, redirect, render_template, request, url_for

import models

web_bp = Blueprint("web", __name__)


def parse_year(raw_year):
    try:
        year = int(raw_year)
    except (TypeError, ValueError):
        return None
    if year < 1000 or year > 3000:
        return None
    return year


@web_bp.route("/")
def index():
    search = request.args.get("q", "").strip()
    books = models.list_books(search) if search else models.list_books()
    return render_template("index.html", books=books, search=search)


@web_bp.route("/nuevo", methods=["GET", "POST"])
def add_book():
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        anio = parse_year(request.form.get("anio_publicacion"))

        if not all([titulo, autor, genero]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("web.add_book"))

        if anio is None:
            flash("El año de publicación debe ser un número válido.", "error")
            return redirect(url_for("web.add_book"))

        models.add_book(titulo, autor, genero, anio)
        flash("Libro agregado correctamente.", "success")
        return redirect(url_for("web.index"))

    return render_template("add_book.html")


@web_bp.route("/editar/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    book = dict(models.get_book(book_id)) if models.get_book(book_id) else None
    if not book:
        flash("El libro no existe.", "error")
        return redirect(url_for("web.index"))

    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        autor = request.form.get("autor", "").strip()
        genero = request.form.get("genero", "").strip()
        anio = parse_year(request.form.get("anio_publicacion"))

        if not all([titulo, autor, genero]):
            flash("Todos los campos son obligatorios.", "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        if anio is None:
            flash("El año de publicación debe ser un número válido.", "error")
            return redirect(url_for("web.edit_book", book_id=book_id))

        models.update_book(book_id, titulo, autor, genero, anio)
        flash("Libro actualizado correctamente.", "success")
        return redirect(url_for("web.index"))

    return render_template("edit_book.html", book=book)


@web_bp.route("/eliminar/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    if models.delete_book(book_id) == 0:
        flash("El libro no existe.", "error")
    else:
        flash("Libro eliminado correctamente.", "success")
    return redirect(url_for("web.index"))