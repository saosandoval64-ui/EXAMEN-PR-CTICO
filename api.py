from flask import Blueprint, request
from flask_restful import Api, Resource

import models

api_bp = Blueprint("api", __name__)
api = Api(api_bp)

REQUIRED_FIELDS = ("titulo", "autor", "genero", "anio_publicacion")


def row_to_dict(row):
    return {
        "id": row["id"],
        "titulo": row["titulo"],
        "autor": row["autor"],
        "genero": row["genero"],
        "anio_publicacion": row["anio_publicacion"],
        "descripcion": row["descripcion"],
        "imagen": row["imagen"],
        "favorito": bool(row["favorito"]),
    }


def get_payload():
    return request.get_json(silent=True) or request.form


def clean(value):
    if isinstance(value, str):
        return value.strip()
    return value


class BookListResource(Resource):
    def get(self):
        search = request.args.get("q", "").strip()
        books = models.list_books(search) if search else models.list_books()
        return [row_to_dict(book) for book in books], 200

    def post(self):
        data = get_payload()
        fields = {field: clean(data.get(field)) for field in REQUIRED_FIELDS}

        if not all(fields.values()):
            return {
                "error": "Los campos titulo, autor, genero y anio_publicacion son obligatorios."
            }, 400

        try:
            anio = int(fields["anio_publicacion"])
        except (TypeError, ValueError):
            return {"error": "anio_publicacion debe ser un número entero."}, 400

        descripcion = clean(data.get("descripcion")) or ""
        imagen = clean(data.get("imagen")) or ""

        book_id = models.add_book(
            fields["titulo"], fields["autor"], fields["genero"], anio, descripcion, imagen
        )
        return row_to_dict(models.get_book(book_id)), 201


class BookResource(Resource):
    def get(self, book_id):
        book = models.get_book(book_id)
        if not book:
            return {"error": "Libro no encontrado."}, 404
        return row_to_dict(book), 200

    def put(self, book_id):
        book = models.get_book(book_id)
        if not book:
            return {"error": "Libro no encontrado."}, 404

        data = get_payload()
        titulo = clean(data.get("titulo")) if "titulo" in data else book["titulo"]
        autor = clean(data.get("autor")) if "autor" in data else book["autor"]
        genero = clean(data.get("genero")) if "genero" in data else book["genero"]

        if "anio_publicacion" in data and data["anio_publicacion"] not in ("", None):
            try:
                anio = int(data["anio_publicacion"])
            except (TypeError, ValueError):
                return {"error": "anio_publicacion debe ser un número entero."}, 400
        else:
            anio = book["anio_publicacion"]

        descripcion = (
            clean(data.get("descripcion")) if "descripcion" in data else book["descripcion"]
        )
        imagen = clean(data.get("imagen")) if "imagen" in data else book["imagen"]

        if not all([titulo, autor, genero]):
            return {
                "error": "Los campos titulo, autor, genero y anio_publicacion son obligatorios."
            }, 400

        models.update_book(book_id, titulo, autor, genero, anio, descripcion, imagen)
        return row_to_dict(models.get_book(book_id)), 200

    def delete(self, book_id):
        if models.delete_book(book_id) == 0:
            return {"error": "Libro no encontrado."}, 404
        return {"message": "Libro eliminado correctamente."}, 200


api.add_resource(BookListResource, "/books")
api.add_resource(BookResource, "/books/<int:book_id>")