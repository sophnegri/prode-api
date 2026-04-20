import mysql.connector
from flask import request, jsonify, Blueprint
from db import get_connection

ranking_bp = Blueprint("ranking", __name__)


# GET /ranking
@ranking_bp.route("/", methods=["GET"])
def obtener_ranking():
    limit = int(request.args.get("_limit", 10))
    offset = int(request.args.get("_offset", 0))

    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
                       SELECT p.usuario_id,
                              p.goles_local,
                              p.goles_visitante,
                              r.goles_local     AS real_local,
                              r.goles_visitante AS real_visitante
                       FROM predicciones p
                                JOIN resultados r ON p.partido_id = r.partido_id
                       """
        )

        datos = cursor.fetchall()

        puntos = {}

        for d in datos:
            pred_local = d["goles_local"]
            pred_visit = d["goles_visitante"]
            real_local = d["real_local"]
            real_visit = d["real_visitante"]

            if pred_local == real_local and pred_visit == real_visit:
                pts = 3
            else:
                pred_diff = pred_local - pred_visit
                real_diff = real_local - real_visit

                if (
                    (pred_diff > 0 and real_diff > 0)
                    or (pred_diff < 0 and real_diff < 0)
                    or (pred_diff == 0 and real_diff == 0)
                ):
                    pts = 1
                else:
                    pts = 0

            puntos[d["usuario_id"]] = puntos.get(d["usuario_id"], 0) + pts

        ranking = [{"usuario_id": k, "puntos": v} for k, v in puntos.items()]
        ranking.sort(key=lambda x: x["puntos"], reverse=True)

        total = len(ranking)
        data = ranking[offset : offset + limit]

        cursor.close()
        conn.close()

        return jsonify({"total": total, "data": data}), 200

    except mysql.connector.Error as err:
        return jsonify({"errors": [f"Error de base de datos: {err}"]}), 500
