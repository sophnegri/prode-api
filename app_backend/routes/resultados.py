import mysql.connector
from flask import Blueprint, jsonify, request
from db import get_connection

resultados_bp = Blueprint("resultados", __name__)


@resultados_bp.route("/partidos/<int:id_partido>/resultado", methods=["PUT"])
def put_resultado(id_partido):
    datos_resultado = request.json
    goles_local = datos_resultado.get("goles_local")
    goles_visitante = datos_resultado.get("goles_visitante")

    if goles_local is None or goles_visitante is None:
        return jsonify({"errors": ["Faltan los goles del resultado"]}), 400

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT id FROM partidos WHERE id = %s", (id_partido,))
        partido = cursor.fetchone()

        if not partido:
            cursor.close()
            conn.close()
            return jsonify({"errors": ["Partido no encontrado"]}), 404

        query = """
                INSERT INTO resultados (partido_id, goles_local, goles_visitante)
                VALUES (%s, %s, %s) ON DUPLICATE KEY \
                UPDATE goles_local = %s, goles_visitante = %s \
                """
        cursor.execute(
            query,
            (id_partido, goles_local, goles_visitante, goles_local, goles_visitante),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return "", 204

    except mysql.connector.Error as err:
        return jsonify({"errors": [f"Error de base de datos: {err}"]}), 500
