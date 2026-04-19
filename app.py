from flask import Flask, jsonify, request
from db import get_connection

app = Flask(__name__)

# FORMATO DE ERROR
def error_response(code, message, description):
    return jsonify({
        "errors": [{
            "code": str(code),
            "message": message,
            "level": "error",
            "description": description
        }]
    }), code

@app.route('/')
def inicio():
    return "hola"

# GET /usuarios
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except:
        return error_response(400, "bad request", "Parámetros inválidos")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, nombre FROM usuarios LIMIT %s OFFSET %s",
        (limit, offset)
    )
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    if not usuarios:
        return '', 204

    # HATEOAS
    base_url = request.base_url

    links = {
        "_first": {"href": f"{base_url}?_limit={limit}&_offset=0"},
        "_prev": {"href": f"{base_url}?_limit={limit}&_offset={max(offset - limit, 0)}"},
        "_next": {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}"},
        "_last": {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}"}
    }

    return jsonify({
        "usuarios": usuarios,
        "_links": links
    }), 200

# GET /usuarios/id
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()
    
    if not usuario:
        return error_response(404, "not found", "Usuario inexistente")

    return jsonify(usuario), 200

# POST /usuarios
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json

    if not data:
        return error_response(400, "bad request", "Body requerido")

    nombre = data.get("nombre")
    email = data.get("email")

    if not isinstance(nombre, str) or not isinstance(email, str):
        return error_response(400, "bad request", "Tipos inválidos")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
            (nombre, email)
        )
        conn.commit()

    except:
        cursor.close()
        conn.close()
        return error_response(409, "conflict", "Usuario duplicado")

    cursor.close()
    conn.close()

    return jsonify({"ok": True}), 201

# PUT /usuarios/id
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.json

    if not data or not data.get("nombre") or not data.get("email"):
        return error_response(400, "bad request", "Faltan datos")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Usuario inexistente")

    cursor.execute(
        "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s",
        (data.get("nombre"), data.get("email"), id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return '', 204

# DELETE /usuarios/id
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Usuario inexistente")

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return '', 204

# GET /partidos
@app.route('/partidos', methods=['GET'])
def obtener_partidos():
    try:
        limit = int(request.args.get('_limit', 10))
        offset = int(request.args.get('_offset', 0))
    except:
        return error_response(400, "bad request", "Parámetros inválidos")

    equipo = request.args.get('equipo')
    fecha = request.args.get('fecha')
    fase = request.args.get('fase')

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM partidos WHERE 1=1"
    params = []

    if equipo:
        query += " AND (equipo_local = %s OR equipo_visitante = %s)"
        params.extend([equipo, equipo])

    if fecha:
        query += " AND fecha = %s"
        params.append(fecha)

    if fase:
        query += " AND fase = %s"
        params.append(fase)

    query += " LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        cursor.execute(query, tuple(params))
        partidos = cursor.fetchall()
    except:
        cursor.close()
        conn.close()
        return error_response(500, "internal error", "Error al obtener partidos")

    cursor.close()
    conn.close()

    if not partidos:
        return '', 204

    # HATEOAS
    base_url = request.base_url
    
    links = {
        "_first": {"href": f"{base_url}?_limit={limit}&_offset=0"},
        "_prev": {"href": f"{base_url}?_limit={limit}&_offset={max(offset - limit, 0)}"},
        "_next": {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}"},
        "_last": {"href": f"{base_url}?_limit={limit}&_offset={offset + limit}"}
    }
    
    return jsonify({
        "partidos": partidos,
        "_links": links
    }), 200

# POST /partidos 
@app.route('/partidos', methods=['POST'])
def crear_partido():
    data = request.json

    if not data:
        return error_response(400, "bad request", "Body requerido")
    
    if not data.get("equipo_local") or not data.get("equipo_visitante") or not data.get("fecha") or not data.get("fase"):
        return error_response(400, "bad request", "Faltan campos obligatorios")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase) VALUES (%s, %s, %s, %s)",
            (
                data.get("equipo_local"),
                data.get("equipo_visitante"),
                data.get("fecha"),
                data.get("fase")
            )
        )
        conn.commit()

        partido_id = cursor.lastrowid

    except:
        cursor.close()
        conn.close()
        return error_response(500, "internal error", "Error al crear partido")

    cursor.close()
    conn.close()

    return jsonify({
        "ok": True,
        "id": partido_id
    }), 201

# GET /partidos/id
@app.route('/partidos/<int:id>', methods=['GET'])
def obtener_partido(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    cursor.close()
    conn.close()

    if not partido:
        return error_response(404, "not found", "Partido inexistente")

    if partido.get("goles_local") is not None and partido.get("goles_visitante") is not None:
        partido["resultado"] = {
            "local": partido.get("goles_local"),
            "visitante": partido.get("goles_visitante")
        }

    return jsonify(partido), 200

# PUT /partidos/id
@app.route('/partidos/<int:id>', methods=['PUT'])
def actualizar_partido(id):
    data = request.json

    if not data:
        return error_response(400, "bad request", "Body requerido")

    nombre_campos = ["equipo_local", "equipo_visitante", "fecha", "fase"]

    if not any(campo in data for campo in nombre_campos):
        return error_response(400, "bad request", "No hay campos para actualizar")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    if not partido:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Partido inexistente")

    campos = []
    valores = []

    for campo in nombre_campos:
        if campo in data:
            campos.append(f"{campo} = %s")
            valores.append(data[campo])

    valores.append(id)

    query = f"UPDATE partidos SET {', '.join(campos)} WHERE id = %s"

    cursor.execute(query, tuple(valores))
    conn.commit()

    cursor.close()
    conn.close()

    return '', 204

# PATCH/partidos/id
@app.route('/partidos/<int:id>', methods=['PATCH'])
def patch_partido(id):
    data = request.json

    if not data:
        return error_response(400, "bad request", "Body requerido")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    if not partido:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Partido inexistente")

    campos = []
    valores = []

    for campo in ["equipo_local", "equipo_visitante", "fecha", "fase"]:
        if campo in data:
            campos.append(f"{campo}=%s")
            valores.append(data[campo])

    if not campos:
        cursor.close()
        conn.close()
        return error_response(400, "bad request", "No hay campos para actualizar")

    valores.append(id)

    query = f"UPDATE partidos SET {', '.join(campos)} WHERE id=%s"

    cursor.execute(query, tuple(valores))
    conn.commit()

    cursor.close()
    conn.close()

    return '', 204

# PUT/partidos/id/resultado
@app.route('/partidos/<int:id>/resultado', methods=['PUT'])
def actualizar_resultado(id):
    data = request.json

    if not data or "goles_local" not in data or "goles_visitante" not in data:
        return error_response(400, "bad request", "Faltan goles")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    if not partido:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Partido inexistente")

    cursor.execute(
        "UPDATE partidos SET goles_local=%s, goles_visitante=%s WHERE id=%s",
        (data["goles_local"], data["goles_visitante"], id)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return '', 204

# POST/partidos/id/prediccion

@app.route('/partidos/<int:id>/prediccion', methods=['POST'])
def crear_prediccion(id):
    data = request.json

    usuario_id = data.get("usuario_id")
    goles_local = data.get("goles_local")
    goles_visitante = data.get("goles_visitante")

    if not usuario_id or goles_local is None or goles_visitante is None:
        return error_response(400, "bad request", "Faltan datos")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Validar partido
    cursor.execute("SELECT * FROM partidos WHERE id = %s", (id,))
    partido = cursor.fetchone()

    if not partido:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Partido inexistente")

    # Validar que no tenga resultado
    if partido["goles_local"] is not None:
        cursor.close()
        conn.close()
        return error_response(400, "bad request", "El partido ya tiene resultado")

    # Validar usuario
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()

    if not usuario:
        cursor.close()
        conn.close()
        return error_response(404, "not found", "Usuario inexistente")

    # Validar duplicado
    cursor.execute(
        "SELECT * FROM predicciones WHERE usuario_id = %s AND partido_id = %s",
        (usuario_id, id)
    )
    existe = cursor.fetchone()

    if existe:
        cursor.close()
        conn.close()
        return error_response(409, "conflict", "Predicción duplicada")

    cursor.execute(
        "INSERT INTO predicciones (usuario_id, partido_id, goles_local, goles_visitante) VALUES (%s, %s, %s, %s)",
        (usuario_id, id, goles_local, goles_visitante)
    )

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"ok": True}), 201

# GET/ranking

@app.route('/ranking', methods=['GET'])
def obtener_ranking():
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT p.usuario_id, p.goles_local, p.goles_visitante,
               pa.goles_local AS real_local, pa.goles_visitante AS real_visitante
        FROM predicciones p
        JOIN partidos pa ON p.partido_id = pa.id
        WHERE pa.goles_local IS NOT NULL
    """)

    datos = cursor.fetchall()

    puntos = {}

    for d in datos:
        pred_local = d["goles_local"]
        pred_visit = d["goles_visitante"]
        real_local = d["real_local"]
        real_visit = d["real_visitante"]

        # exacto
        if pred_local == real_local and pred_visit == real_visit:
            pts = 3
        else:
            pred_diff = pred_local - pred_visit
            real_diff = real_local - real_visit

            if (pred_diff > 0 and real_diff > 0) or \
               (pred_diff < 0 and real_diff < 0) or \
               (pred_diff == 0 and real_diff == 0):
                pts = 1
            else:
                pts = 0

        puntos[d["usuario_id"]] = puntos.get(d["usuario_id"], 0) + pts

    ranking = [{"usuario_id": k, "puntos": v} for k, v in puntos.items()]
    ranking.sort(key=lambda x: x["puntos"], reverse=True)

    total = len(ranking)
    data = ranking[offset:offset + limit]

    cursor.close()
    conn.close()

    return jsonify({
        "total": total,
        "data": data
    }), 200

#MAIN
if __name__ == '__main__':
    app.run(port=8080)
