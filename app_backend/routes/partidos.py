import mysql.connector
from flask import Blueprint, request, jsonify
from db import get_connection

partidos_bp = Blueprint("partidos", __name__)


# --- ENDPOINTS ---


@partidos_bp.route("/", methods=["GET"])
def get_partidos():
    """Listar partidos desde la base de datos con paginación"""
    limit = request.args.get("_limit", default=10, type=int)
    offset = request.args.get("_offset", default=0, type=int)
    equipo = request.args.get("equipo")

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        # Query básica
        query = "SELECT * FROM partidos"
        params = []

        if equipo:
            query += " WHERE equipo_local = %s OR equipo_visitante = %s"
            params.extend([equipo, equipo])

        query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])

        cursor.execute(query, params)
        partidos = cursor.fetchall()

        cursor.close()
        conn.close()

        if not partidos:
            return "", 204

        return jsonify({"partidos": partidos}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": "Error en la base de datos", "details": str(err)}), 500


@partidos_bp.route("/", methods=["POST"])
def crear_partido():
    """Crear un nuevo partido en MySQL"""
    data = request.get_json()

    # Validaciones básicas
    campos = ["equipo_local", "equipo_visitante", "estadio", "ciudad", "fecha", "fase"]
    if not all(data.get(c) for c in campos):
        return jsonify({"error": "Faltan datos obligatorios"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """INSERT INTO partidos (equipo_local, equipo_visitante, estadio, ciudad, fecha, fase)
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        valores = (
            data.get("equipo_local"),
            data.get("equipo_visitante"),
            data.get("estadio"),
            data.get("ciudad"),
            data.get("fecha"),
            data.get("fase"),
        )

        cursor.execute(query, valores)
        conn.commit()
        nuevo_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return jsonify({"id": nuevo_id, "mensaje": "Partido creado con éxito"}), 201
    except mysql.connector.Error as err:
        return (
            jsonify({"error": "No se pudo guardar el partido", "details": str(err)}),
            500,
        )


@partidos_bp.route("/<int:id_partido>", methods=["GET"])
def get_partido(id_partido):
    """Obtener un partido específico por ID"""
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM partidos WHERE id = %s", (id_partido,))
        partido = cursor.fetchone()
        cursor.close()
        conn.close()

        if not partido:
            return jsonify({"error": "Partido no encontrado"}), 404

        return jsonify(partido), 200
    except mysql.connector.Error as err:
        return jsonify({"error": "Error de conexión", "details": str(err)}), 500


@partidos_bp.route("/<int:id_partido>", methods=["DELETE"])
def delete_partido(id_partido):
    """Eliminar un partido de la base de datos"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM partidos WHERE id = %s", (id_partido,))
        conn.commit()

        filas_afectadas = cursor.rowcount
        cursor.close()
        conn.close()

        if filas_afectadas == 0:
            return jsonify({"error": "Partido no encontrado"}), 404

        return "", 204
    except mysql.connector.Error as err:
        return jsonify({"error": "Error al eliminar", "details": str(err)}), 500
