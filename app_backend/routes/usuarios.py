import mysql.connector
from flask import request, jsonify, Blueprint
from db import get_connection

usuarios_bp = Blueprint("usuarios", __name__)


# POST /usuarios (VERSION JOEL)
@usuarios_bp.route("/", methods=["POST"])
def crear_usuario():
    datos_igresados = request.get_json()
    nombre_usuario = datos_igresados.get("nombre")
    email_usuario = datos_igresados.get("email")

    if nombre_usuario == "" or email_usuario == "":
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "REQ-400",
                            "message": "Faltan datos",
                            "level": "error",
                            "description": "Se deben ingresar los siguientes datos: Nombre y Mail",
                        }
                    ]
                }
            ),
            400,
        )

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)"
        cursor.execute(query, (nombre_usuario, email_usuario))

        conn.commit()

        id_usuario = cursor.lastrowid

        cursor.close()
        conn.close()

        return (
            jsonify(
                {"mensaje": "Se creo el usuario con exito", "id_usuario": id_usuario}
            ),
            201,
        )

    except mysql.connector.Error as err:
        if err.errno == 1062:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "code": "USR-409",
                                "message": "Datos duplicados",
                                "level": "error",
                                "description": "Uno de los datos ingresados ya se encuentra registrado",
                            }
                        ]
                    }
                ),
                409,
            )

        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "SYS-500",
                            "message": "Error de conexion",
                            "level": "error",
                            "description": "No se pudo conectar a la Base de datos",
                        }
                    ]
                }
            ),
            500,
        )


# GET /usuarios (VERSION JOEL)
@usuarios_bp.route("/", methods=["GET"])
def listar_usuarios():
    limit = request.args.get("_limit", default=10, type=int)
    offset = request.args.get("_offset", default=0, type=int)

    if limit <= 0 or offset < 0:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "USR-400",
                            "message": "Parametros de paginacion invalidos",
                            "level": "error",
                            "description": "El limit no puede ser menor o igual a 0",
                        }
                    ]
                }
            ),
            400,
        )
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nombre FROM usuarios LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        usuarios = cursor.fetchall()

        cursor.close()
        conn.close()

        if not usuarios:
            return "", 204

        base_url = request.base_url

        links = {
            "_first": {"href": f"{base_url}?_offset=0&_limit={limit}"},
            "_prev": {
                "href": f"{base_url}?_offset={max(0, offset - limit)}&_limit={limit}"
            },
            "_next": {"href": f"{base_url}?_offset={offset + limit}&_limit={limit}"},
            "_last": {"href": f"{base_url}?_offset=100&_limit={limit}"},
        }
        return jsonify({"_links": links, "usuarios": usuarios}), 200

    except mysql.connector.Error as err:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "SYS-500",
                            "message": "Error en la Base de Datos",
                            "level": "error",
                            "description": "No se conecto a la Base de Datos",
                        }
                    ]
                }
            ),
            500,
        )


# GET /usuarios/id (Sophia)
@usuarios_bp.route("/<int:id>", methods=["GET"])
def obtener_usuario(id):
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email FROM usuarios WHERE id = %s", (id,))
        usuario = cursor.fetchone()
        cursor.close()
        conn.close()

        if usuario:
            return jsonify(usuario), 200

        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "USR-404",
                            "message": "Usuario no encontrado",
                            "level": "error",
                            "description": f"El usuario con ID {id} no existe",
                        }
                    ]
                }
            ),
            404,
        )

    except Exception:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "SYS-500",
                            "message": "Error de servidor",
                            "level": "error",
                            "description": "No se pudo conectar a la Base de datos",
                        }
                    ]
                }
            ),
            500,
        )


# PUT /usuarios/id (joel)
@usuarios_bp.route("/<int:id>", methods=["PUT"])
def reemplazar_usuario(id):
    nombre_nuevo = request.get_json().get("nombre")
    email_nuevo = request.get_json().get("email")

    if not nombre_nuevo or not email_nuevo:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "USR-400",
                            "message": "Datos incompletos",
                            "level": "error",
                            "description": "Asegurese de ingresar Nombre y Email",
                        }
                    ]
                }
            ),
            400,
        )
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM usuarios WHERE id = %s "
        cursor.execute(query, (id,))
        usuario_buscado = cursor.fetchone()

        if not usuario_buscado:
            return "", 404

        if (
            usuario_buscado["nombre"] == nombre_nuevo
            and usuario_buscado["email"] == email_nuevo
        ):
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "code": "USR-409",
                                "message": "No hay cambios en los datos anteriores",
                                "level": "error",
                                "description": "Ingrese datos diferentes a los anteriores",
                            }
                        ]
                    }
                ),
                409,
            )

        query = "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s"
        cursor.execute(query, (nombre_nuevo, email_nuevo, id))

        conn.commit()
        cursor.close()
        conn.close()

        return "", 204

    except mysql.connector.Error as err:
        if err.errno == 1062:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "code": "USR-409",
                                "message": "Email duplicado",
                                "level": "error",
                                "description": "El email ingresado ya está en uso por otro usuario.",
                            }
                        ]
                    }
                ),
                409,
            )

        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "SYS-500",
                            "message": "Error de conexion",
                            "level": "error",
                            "description": "No se pudo conectar a la Base de datos",
                        }
                    ]
                }
            ),
            500,
        )


# DELETE /usuarios/id (Sophia)
@usuarios_bp.route("/<int:id>", methods=["DELETE"])
def eliminar_usuario(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            return (
                jsonify(
                    {
                        "errors": [
                            {
                                "code": "USR-404",
                                "message": "No encontrado",
                                "level": "error",
                                "description": "No se encontró el usuario para eliminar",
                            }
                        ]
                    }
                ),
                404,
            )

        cursor.close()
        conn.close()
        return "", 204

    except:
        return (
            jsonify(
                {
                    "errors": [
                        {
                            "code": "SYS-500",
                            "message": "Error de conexion",
                            "level": "error",
                            "description": "No se pudo conectar a la Base de datos",
                        }
                    ]
                }
            ),
            500,
        )
