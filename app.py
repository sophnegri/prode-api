from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = [
    {"id": 1, "nombre": "Sophia"},
    {"id": 2, "nombre": "Joel"}
]

# ruta principal
@app.route('/')
def inicio():
    return "hola"

# GET todos
from db import get_connection

@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios_db = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(usuarios_db)

# GET por id
@app.route('/usuarios/<int:id>', methods=['GET'])
def obtener_usuario(id):
    for usuario in usuarios:
        if usuario["id"] == id:
            return jsonify(usuario)
    return jsonify({"error": "Usuario no encontrado"})

# POST crear
@app.route('/usuarios', methods=['POST'])
def crear_usuario():
    data = request.json
    nombre = data.get("nombre")
    email = data.get("email")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO usuarios (nombre, email) VALUES (%s, %s)",
        (nombre, email)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Usuario guardado en DB"})

# DELETE usuario
@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    for usuario in usuarios:
        if usuario["id"] == id:
            usuarios.remove(usuario)
            return jsonify({"mensaje": "Usuario eliminado"})
    return jsonify({"error": "Usuario no encontrado"})

if __name__ == '__main__':
    app.run(port=8080)
