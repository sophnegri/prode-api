from db import get_connection


def validar_resultado(datos_resultado):
    errores = []

    if datos_resultado.get("local") is None:
        errores.append("local es requerido")

    if datos_resultado.get("visitante") is None:
        errores.append("visitante es requerido")

    if datos_resultado.get("local") is not None and datos_resultado.get("local") < 0:
        errores.append("local no puede ser negativo")

    if (
        datos_resultado.get("visitante") is not None
        and datos_resultado.get("visitante") < 0
    ):
        errores.append("visitante no puede ser negativo")

    return errores


def existe_partido(cursor, id_partido):
    cursor.execute(
        """
        SELECT id
        FROM partidos
        WHERE id = %s
    """,
        (id_partido,),
    )
    return cursor.fetchone() is not None


def existe_resultado(cursor, id_partido):
    cursor.execute(
        """
        SELECT id
        FROM resultados
        WHERE partido_id = %s
    """,
        (id_partido,),
    )
    return cursor.fetchone() is not None


def cargar_o_actualizar_resultado(id_partido, datos_resultado):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    # Verificar que el partido existe antes de operar
    if not existe_partido(cursor, id_partido):
        cursor.close()
        conexion.close()
        return False, "Partido no encontrado"

    # Si ya tiene resultado lo actualiza, si no lo crea
    if existe_resultado(cursor, id_partido):
        cursor.execute(
            """
            UPDATE resultados
            SET goles_local = %s,
                goles_visitante = %s
            WHERE partido_id = %s
        """,
            (datos_resultado["local"], datos_resultado["visitante"], id_partido),
        )
    else:
        cursor.execute(
            """
            INSERT INTO resultados (partido_id, goles_local, goles_visitante)
            VALUES (%s, %s, %s)
        """,
            (id_partido, datos_resultado["local"], datos_resultado["visitante"]),
        )

    conexion.commit()
    cursor.close()
    conexion.close()
    return True, None
