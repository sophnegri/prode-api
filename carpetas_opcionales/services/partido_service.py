from db import get_connection

FASES_VALIDAS = ["grupos", "dieciseisavos", "octavos", "cuartos", "semis", "final"]


def validar_partido(datos_partido):
    errores = []

    if not datos_partido.get("equipo_local"):
        errores.append("equipo_local es requerido")

    if not datos_partido.get("equipo_visitante"):
        errores.append("equipo_visitante es requerido")

    if not datos_partido.get("fecha"):
        errores.append("fecha es requerida")

    if not datos_partido.get("fase"):
        errores.append("fase es requerida")
    elif datos_partido.get("fase") not in FASES_VALIDAS:
        errores.append(
            "fase debe ser una de: grupos, dieciseisavos, octavos, cuartos, semis, final"
        )

    return errores


def obtener_todos_los_partidos(equipo=None, fecha=None, fase=None, limit=10, offset=0):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    consulta_base = """
        SELECT id, equipo_local, equipo_visitante, fecha, fase
        FROM partidos
        WHERE 1=1
    """
    filtros = []
    valores_filtros = []

    if equipo:
        filtros.append("(equipo_local = %s OR equipo_visitante = %s)")
        valores_filtros.extend([equipo, equipo])

    if fecha:
        filtros.append("fecha = %s")
        valores_filtros.append(fecha)

    if fase:
        if fase not in FASES_VALIDAS:
            cursor.close()
            conexion.close()
            return None, "fase invalida"
        filtros.append("fase = %s")
        valores_filtros.append(fase)

    # Agregar filtros a la consulta si existen
    for filtro in filtros:
        consulta_base += f" AND {filtro}"

    # Agrega paginacion al final
    consulta_base += " LIMIT %s OFFSET %s"
    valores_filtros.extend([limit, offset])

    cursor.execute(consulta_base, valores_filtros)
    partidos_encontrados = cursor.fetchall()

    for partido in partidos_encontrados:
        partido["fecha"] = str(partido["fecha"])

    cursor.close()
    conexion.close()
    return partidos_encontrados, None


def obtener_partido_por_id(id_partido):
    conexion = get_connection()
    cursor = conexion.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT id, equipo_local, equipo_visitante, fecha, fase
        FROM partidos
        WHERE id = %s
    """,
        (id_partido,),
    )
    partido_encontrado = cursor.fetchone()

    if not partido_encontrado:
        cursor.close()
        conexion.close()
        return None

    partido_encontrado["fecha"] = str(partido_encontrado["fecha"])

    cursor.execute(
        """
        SELECT goles_local, goles_visitante
        FROM resultados
        WHERE partido_id = %s
    """,
        (id_partido,),
    )
    resultado_encontrado = cursor.fetchone()

    partido_encontrado["resultado"] = resultado_encontrado

    cursor.close()
    conexion.close()
    return partido_encontrado


def crear_partido(datos_partido):
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        INSERT INTO partidos (equipo_local, equipo_visitante, fecha, fase)
        VALUES (%s, %s, %s, %s)
    """,
        (
            datos_partido["equipo_local"],
            datos_partido["equipo_visitante"],
            datos_partido["fecha"],
            datos_partido["fase"],
        ),
    )

    conexion.commit()
    id_partido_creado = cursor.lastrowid

    cursor.close()
    conexion.close()
    return id_partido_creado


def eliminar_partido(id_partido):
    conexion = get_connection()
    cursor = conexion.cursor()

    cursor.execute(
        """
        DELETE FROM partidos
        WHERE id = %s
    """,
        (id_partido,),
    )

    conexion.commit()
    partido_fue_eliminado = cursor.rowcount > 0

    cursor.close()
    conexion.close()
    return partido_fue_eliminado


def contar_partidos(equipo=None, fecha=None, fase=None):
    conexion = get_connection()
    cursor = conexion.cursor()

    consulta_conteo = "SELECT COUNT(*) FROM partidos WHERE 1=1"
    valores_filtros = []

    if equipo:
        consulta_conteo += " AND (equipo_local = %s OR equipo_visitante = %s)"
        valores_filtros.extend([equipo, equipo])
    if fecha:
        consulta_conteo += " AND fecha = %s"
        valores_filtros.append(fecha)
    if fase:
        consulta_conteo += " AND fase = %s"
        valores_filtros.append(fase)

    cursor.execute(consulta_conteo, valores_filtros)
    total = cursor.fetchone()[0]

    cursor.close()
    conexion.close()
    return total
