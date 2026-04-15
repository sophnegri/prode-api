from flask import Blueprint, request, jsonify
from db import get_connection

predicciones_bp = Blueprint("predicciones", __name__)


# POST/partidos/id/prediccion
@predicciones_bp.route("/partidos/<int:id>/prediccion", methods=["POST"])
def crear_prediccion(id):
    data = request.json
    id_usuario = data.get("id_usuario")
    local_goles = data.get("local")
    visitante_goles = data.get("visitante")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if not id_usuario or local_goles is None or visitante_goles is None:
        return jsonify({"error": "faltan datos"}), 400

    if local_goles < 0 or visitante_goles < 0:
        return jsonify({"error": "Los goles no pueden ser negativos"}), 400

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()
    if not partido:
        cursor.close()
        conn.close()
        return jsonify({"error": "partido no encontrado"}), 404

    cursor.execute("SELECT * FROM resultados WHERE partido_id = %s", (id,))
    resultado = cursor.fetchone()
    if resultado:
        cursor.close()
        conn.close()
        return jsonify({"error": "el partido ya se jugó"}), 400

    cursor.execute(
        "SELECT * FROM predicciones WHERE usuario_id = %s AND partido_id = %s",
        (id_usuario, id),
    )
    prediccion = cursor.fetchone()
    if prediccion:
        cursor.close()
        conn.close()
        return jsonify({"error": "ya existe prediccion"}), 409

    cursor.execute(
        """
                   INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante)
                   VALUES (%s, %s, %s, %s)
                   """,
        (id_usuario, id, local_goles, visitante_goles),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"ok": True}), 201
