from flask import Blueprint

inicio_bp = Blueprint("inicio", __name__)


@inicio_bp.route("/")
def inicio():
    return {
        "status": "ok",
        "message": "API levantada",
    }  # acá cambié el mensaje, antes decia hola
