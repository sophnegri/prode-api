from flask import Flask
from app_backend.routes.inicio import inicio_bp
from app_backend.routes.usuarios import usuarios_bp
from app_backend.routes.partidos import partidos_bp
from app_backend.routes.predicciones import predicciones_bp
from app_backend.routes.ranking import ranking_bp
from app_backend.routes.resultados import resultados_bp

app = Flask(__name__)

app.register_blueprint(inicio_bp, url_prefix="/inicio")
app.register_blueprint(partidos_bp, url_prefix="/partidos")
app.register_blueprint(predicciones_bp, url_prefix="/partidos")
app.register_blueprint(ranking_bp, url_prefix="/ranking")
app.register_blueprint(resultados_bp, url_prefix="/partidos")
app.register_blueprint(usuarios_bp, url_prefix="/usuarios")


if __name__ == "__main__":
    app.run(debug=True, port=8080)
