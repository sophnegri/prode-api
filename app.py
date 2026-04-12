from flask import Flask, jsonify, request
from db import get_connection

app = Flask(__name__)

@app.route('/')
def inicio():
    return "hola"

# GET todos
@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios)

# GET por id
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
    usuario = cursor.fetchone()

    cursor.close()
    conn.close()

    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({"error": "no existe"})

# POST
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
        (data.get("nombre"), data.get("email"))
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"ok": True})

# DELETE
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM usuarios WHERE id = %s", (id,))
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"ok": True})

if __name__ == '__main__':
    app.run(port=8080)
