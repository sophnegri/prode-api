from flask import Blueprint, request, jsonify
from db import get_connection
import mysql.connector

predicciones_bp = Blueprint("predicciones", __name__)


@predicciones_bp.route("/<int:id>/prediccion", methods=["POST"])
def crear_prediccion(id):
    data = request.get_json()
    id_usuario = data.get("id_usuario")
    local_goles = data.get("local")
    visitante_goles = data.get("visitante")

    if not id_usuario or local_goles is None or visitante_goles is None:
        return jsonify({"error": "faltan datos"}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "partido no encontrado"}), 404

        cursor.execute(
            "INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante) VALUES (%s, %s, %s, %s)",
            (id_usuario, id, local_goles, visitante_goles),
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"ok": True}), 201

    except mysql.connector.Error as err:
        if err.errno == 1062:
            return jsonify({"error": "ya existe prediccion"}), 409
        return jsonify({"error": str(err)}), 500
