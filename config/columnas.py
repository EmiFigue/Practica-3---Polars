"""Mapeo de columnas 
"""

COLUMNAS = {
    "edad_primer_union": "edad_primer_union",
    "num_hijos": "num_hijos",
    "nom_entidad": "nom_entidad",
    "nivel_escolaridad": "nivel_escolaridad",
    "estado_civil_desc": "estado_civil_desc",
    "sufrio_violencia_pareja": "sufrio_violencia_pareja",
    "factor_expansion": "factor_expansion",
}


COLUMNAS_EXTRA = (
    "cve_entidad",
    "cve_municipio",
    "nom_municipio",
    "estado_civil_id",
    "estrato_socioeconomico",
    "pareja_trabaja_id",
    "pareja_trabaja_desc",
    "ingreso_pareja",
    "dinero_propio_id",
    "dinero_propio_desc",
    "apoyo_gobierno_id",
    "apoyo_gobierno_desc",
    "tiene_ahorros_id",
    "tiene_ahorros_desc",
    "propietaria_vivienda_id",
    "propietaria_vivienda_desc",
    "anio_encuesta",
)

# eliminar duplicados exactos.
CLAVE_PRIMARIA = None

VARIABLES_NUMERICAS = ("edad_primer_union", "num_hijos", "factor_expansion")
VARIABLES_CATEGORICAS = (
    "nom_entidad",
    "nivel_escolaridad",
    "estado_civil_desc",
    "sufrio_violencia_pareja",
)


def validar_columnas(columnas_presentes) -> None:
    """Verifica que el CSV contenga las variables clave del analisis."""
    faltantes = [c for c in COLUMNAS.values() if c not in columnas_presentes]
    if faltantes:
        raise ValueError(
            "El archivo crudo no contiene las columnas esperadas: "
            f"{faltantes}. Revise el descriptor de ENDIREH 2021 y ajuste "
            "config/columnas.py."
        )
