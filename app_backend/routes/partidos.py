from flask import Blueprint
from db import get_connection
from carpetas_opcionales.services.resultado_service import (
    cargar_o_actualizar_resultado,
    validar_resultado,
)

partidos_bp = Blueprint("partidos", __name__)


@partidos_bp.route("/partidos", methods=["GET"])  ##listar partidos
def get_partidos():
    filtro_equipo = request.args.get("equipo")
    filtro_fecha = request.args.get("fecha")
    filtro_fase = request.args.get("fase")
    cantidad = int(request.args.get("_limit", 10))
    desde = int(request.args.get("_offset", 0))

    partidos, error = obtener_todos_los_partidos(
        equipo=filtro_equipo,
        fecha=filtro_fecha,
        fase=filtro_fase,
        limit=cantidad,
        offset=desde,
    )

    if error:
        return jsonify({"errors": [error]}), 400

    if not partidos:
        return "", 204

    total_partidos = contar_partidos(
        equipo=filtro_equipo, fecha=filtro_fecha, fase=filtro_fase
    )

    links = construir_links_paginacion(
        url_base=request.base_url,
        offset_actual=desde,
        limit=cantidad,
        total_registros=total_partidos,
    )

    return jsonify({"partidos": partidos, "_links": links}), 200


@partidos_bp.route(
    "/partidos", methods=["POST"]
)  # Endpoint para crear un nuevo partido
def crear_partido():
    global contador_partido

    data = request.get_json()  # Datos enviados por el usuario

    nuevo = {  # Crea el nuevo partido con los datos recibidos y un ID único
        "id": contador_partido,
        "equipo_local": data.get("equipo_local"),
        "equipo_visitante": data.get("equipo_visitante"),
        "estadio": data.get("estadio"),
        "ciudad": data.get("ciudad"),
        "fecha": data.get("fecha"),
        "fase": data.get("fase"),
        "resultado": None,
    }

    partidos.append(nuevo)  # Guardo el partido en la lista

    contador_partido += 1

    return (
        jsonify(nuevo),
        201,
    )  # Devuelve el partido creado con el código de estado 201 (creado)


@partidos_bp.route(
    "/partidos/<int:id_partido>", methods=["GET"]
)  ## obtener partido por id
def get_partido(id_partido):
    partido = obtener_partido_por_id(id_partido)

    if not partido:
        return jsonify({"errors": ["Partido no encontrado"]}), 404

    return jsonify(partido), 200


@partidos_bp.route("/partidos/<int:id_partido>", methods=["DELETE"])  ##eliminar partido
def delete_partido(id_partido):
    partido_eliminado = eliminar_partido(id_partido)

    if not partido_eliminado:
        return jsonify({"errors": ["Partido no encontrado"]}), 404

    return "", 204


@partidos_bp.route(
    "/partidos/<int:id>", methods=["PUT"]
)  # Endpoint para actualizar un partido completo
def actualizar_partido(id):
    for p in partidos:
        if p["id"] == id:
            data = request.get_json()

            p["equipo_local"] = data.get("equipo_local")
            p["equipo_visitante"] = data.get("equipo_visitante")
            p["estadio"] = data.get("estadio")
            p["ciudad"] = data.get("ciudad")
            p["fecha"] = data.get("fecha")
            p["fase"] = data.get("fase")

            return jsonify(p), 200

    return {"Error": "Partido no encontrado"}, 404


@partidos_bp.route("/partidos", methods=["POST"])
def post_partido():
    datos_nuevo_partido = request.json

    errores = validar_partido(datos_nuevo_partido)
    if errores:
        return jsonify({"errors": errores}), 400

    id_partido_creado = crear_partido(datos_nuevo_partido)
    return jsonify({"id": id_partido_creado}), 201


# `GET/partidos
# POST/partidos
# GET/partidos/id
# PUT/partidos/id
# PATCH/partidos/id
# DELETE/partidos/id
