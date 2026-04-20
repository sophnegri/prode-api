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
@usuarios_bp.route('/<int:id>', methods=['GET'])
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

        return jsonify({
            "errors": [{
                "code": "USR-404",
                "message": "Usuario no encontrado",
                "level": "error",
                "description": f"El usuario con ID {id} no existe"
            }]
        }), 404

    except Exception:
        return jsonify({
            "errors": [{
                "code": "SYS-500",
                "message": "Error de servidor",
                "level": "error",
                "description": "No se pudo conectar a la Base de datos"
            }]
        }), 500

# PUT /usuarios/id (Sophia)
@usuarios_bp.route('/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.get_json()
    nombre = data.get("nombre")
    email = data.get("email")

    if not nombre or not email:
        return jsonify({
            "errors": [{
                "code": "REQ-400",
                "message": "Faltan datos",
                "level": "error",
                "description": "Se deben ingresar los siguientes datos: Nombre y Mail"
            }]
        }), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM usuarios WHERE id = %s", (id,))
        existe = cursor.fetchone()

        if existe:
            cursor.execute("UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s", (nombre, email, id))
        else:
            cursor.execute("INSERT INTO usuarios (id, nombre, email) VALUES (%s, %s, %s)", (id, nombre, email))

        conn.commit()
        cursor.close()
        conn.close()
        return '', 204

    except Exception:
        return jsonify({
            "errors": [{
                "code": "SYS-500",
                "message": "Error de conexion",
                "level": "error",
                "description": "No se pudo conectar a la Base de datos"
            }]
        }), 500

# DELETE /usuarios/id (Sophia)
@usuarios_bp.route('/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        conn.commit()

        if cursor.rowcount == 0:
            cursor.close()
            conn.close()
            return jsonify({
                "errors": [{
                    "code": "USR-404",
                    "message": "No encontrado",
                    "level": "error",
                    "description": "No se encontró el usuario para eliminar"
                }]
            }), 404

        cursor.close()
        conn.close()
        return '', 204

    except Exception:
        return jsonify({
            "errors": [{
                "code": "SYS-500",
                "message": "Error de conexion",
                "level": "error",
                "description": "No se pudo conectar a la Base de datos"
            }]
        }), 500
