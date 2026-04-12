from flask import Flask, jsonify, request
from db import get_connection

app = Flask(__name__)

@app.route('/')
def inicio():
    return "hola"

# GET /usuarios (Joel ya lo tenia hecho)
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    limit = int(request.args.get('_limit', 10))
    offset = int(request.args.get('_offset', 0))

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT id, nombre FROM usuarios LIMIT %s OFFSET %s",
        (limit, offset)
    )
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "usuarios": usuarios,
        "_links": {
            "_self": {"href": f"/usuarios?_limit={limit}&_offset={offset}"}
        }
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

    if usuario:
        return jsonify(usuario), 200
    else:
        return jsonify({"error": "no existe"}), 404

# POST /usuarios (Joel ya lo tenia hecho)
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json

    if not data.get("nombre") or not data.get("email"):
        return jsonify({"error": "faltan datos"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
            (data.get("nombre"), data.get("email"))
        )
        conn.commit()
    except:
        return jsonify({"error": "conflicto"}), 409

    cursor.close()
    conn.close()

    return jsonify({"ok": True}), 201


# PUT /usuarios/id
@app.route('/usuarios/<int:id>', methods=['PUT'])
def actualizar_usuario(id):
    data = request.json

    if not data.get("nombre") or not data.get("email"):
        return jsonify({"error": "faltan datos"}), 400

    conn = get_connection()
    cursor = conn.cursor()

    # Verificar si existe
    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    if usuario:
        cursor.execute(
            "UPDATE usuarios SET nombre = %s, email = %s WHERE id = %s",
            (data.get("nombre"), data.get("email"), id)
        )
    else:
        cursor.execute(
            "INSERT INTO usuarios (id, nombre, email) VALUES (%s, %s, %s)",
            (id, data.get("nombre"), data.get("email"))
        )

    conn.commit()

    cursor.close()
    conn.close()

    return '', 204

# DELETE /usuarios/id
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return '', 204


if __name__ == '__main__':
    app.run(port=8080)

#falta de prode
# GET/partidos
# POST/partidos
# GET/partidos/id
# PUT/partidos/id
# PATCH/partidos/id
# DELETE/partidos/id

# PUT/partidos/id/resultado

# POST/partidos/id/prediccion

# GET/ranking
