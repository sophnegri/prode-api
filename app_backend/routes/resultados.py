from flask import Blueprint, jsonify, request
from carpetas_opcionales.services.resultado_service import (
    cargar_o_actualizar_resultado,
    validar_resultado,
)

resultados_bp = Blueprint("resultados", __name__)


@resultados_bp.route(
    "/partidos/<int:id_partido>/resultado", methods=["PUT"]
)  ##cargar o actualizar resultado
def put_resultado(id_partido):
    datos_resultado = request.json

    errores = validar_resultado(datos_resultado)
    if errores:
        return jsonify({"errors": errores}), 400

    resultado_guardado, error = cargar_o_actualizar_resultado(
        id_partido=id_partido, datos_resultado=datos_resultado
    )

    if not resultado_guardado:
        return jsonify({"errors": [error]}), 404

    return "", 204
