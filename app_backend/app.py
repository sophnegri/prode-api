from flask import Flask
from app_backend.routes.inicio import inicio_bp
from app_backend.routes.usuarios import usuarios_bp

app = Flask(__name__)

app.register_blueprint(inicio_bp, url_prefix="/inicio")
app.register_blueprint(usuarios_bp, url_prefix="/partidos")
app.register_blueprint(usuarios_bp, url_prefix="/predicciones")
app.register_blueprint(usuarios_bp, url_prefix="/ranking")
app.register_blueprint(usuarios_bp, url_prefix="/resultados")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")

# se encarga de correr la app
if __name__ == "__main__":
    app.run(
        port=8080, debug=True
    )  # podemos usar el port por defecto de flask que seria el 5000 o el 8080
    # Para usar el 5000 simplente hay que borrar lo de port(super opcional)
