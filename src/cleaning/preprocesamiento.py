"""Limpieza y preprocesamiento
"""

import re

import numpy as np
import polars as pl

from config.columnas import (
    CLAVE_PRIMARIA,
    COLUMNAS,
    VARIABLES_CATEGORICAS,
    VARIABLES_NUMERICAS,
    validar_columnas,
)
from config.rutas import (
    ARCHIVO_CRUDO,
    ARCHIVO_FEATURES,
    ARCHIVO_LIMPIO,
    crear_directorios,
)

NULOS_CSV = ["", "NA", "N/A", "9999", "999", "98", "99"]
MIN_EDAD_UNION = 12
MAX_EDAD_UNION = 98
MAX_HIJOS_VALIDO = 98

ACENTOS = {
    "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u", "ñ": "n",
    "Á": "a", "É": "e", "Í": "i", "Ó": "o", "Ú": "u", "Ü": "u", "Ñ": "n",
}

# El consolidado mezcla UTF-8 correcto con texto doblemente codificado
# (p. ej. "QUER" + "Ã" + U+0089 + "TARO" en lugar de "QUERETARO" con É).
# Se reparan los pares "Ã" + caracter de control antes de normalizar.
MOJIBAKE = {
    "\u00c3\u0081": "a", "\u00c3\u0089": "e", "\u00c3\u008d": "i",
    "\u00c3\u0091": "n", "\u00c3\u0093": "o", "\u00c3\u009a": "u",
    "\u00c3\u009c": "u", "\u00c3\u00a1": "a", "\u00c3\u00a9": "e",
    "\u00c3\u00ad": "i", "\u00c3\u00b1": "n", "\u00c3\u00b3": "o",
    "\u00c3\u00ba": "u", "\u00c3\u00bc": "u",
}
REEMPLAZOS_TEXTO = {**MOJIBAKE, **ACENTOS}


def cargar_datos_crudos(ruta=ARCHIVO_CRUDO) -> pl.DataFrame:
    """Carga el CSV crudo y valida que exista y tenga las columnas clave."""
    if not ruta.exists():
        raise FileNotFoundError(
            f"No se encontro el archivo crudo en {ruta}.\n"
            "Descargue el consolidado ENDIREH 2021 del INEGI y coloquelo "
            "como data/data-raw/endireh_2021.csv"
        )
    df = pl.read_csv(
        ruta,
        infer_schema_length=10000,
        null_values=NULOS_CSV,
    )
    validar_columnas(df.columns)
    print(f"[carga] Registros: {df.height:,} | Columnas: {df.width}")
    print(f"[carga] Esquema detectado:\n{df.schema}")
    print(f"[carga] Primeras filas:\n{df.head(3)}")
    return df


def analizar_calidad(df: pl.DataFrame) -> pl.DataFrame:
    """Reporta nulos, duplicados, categorias y rangos de las variables clave."""
    resumen = pl.DataFrame(
        {
            "variable": list(df.columns),
            "tipo": [str(t) for t in df.schema.values()],
            "nulos": [df[c].null_count() for c in df.columns],
            "pct_nulos": [
                round(df[c].null_count() / df.height * 100, 2)
                for c in df.columns
            ],
            "valores_unicos": [df[c].n_unique() for c in df.columns],
        }
    )
    duplicados = df.height - df.unique().height
    print(f"[calidad] Duplicados exactos: {duplicados:,}")
    for col in VARIABLES_CATEGORICAS:
        print(f"[calidad] {col}: {df[col].unique(maintain_order=True).to_list()}")
    for col in VARIABLES_NUMERICAS:
        print(
            f"[calidad] {col}: min={df[col].min()} max={df[col].max()} "
            f"nulos={df[col].null_count():,}"
        )
    return resumen


def eliminar_duplicados(df: pl.DataFrame) -> tuple[pl.DataFrame, int]:
    """Elimina duplicados"""
    n_inicial = df.height
    if CLAVE_PRIMARIA:
        df = df.unique(subset=CLAVE_PRIMARIA, keep="first")
    else:
        df = df.unique()
    eliminados = n_inicial - df.height
    print(f"[duplicados] Eliminados: {eliminados:,} | Restantes: {df.height:,}")
    return df, eliminados


def convertir_tipos(df: pl.DataFrame) -> pl.DataFrame:
    """Convierte las variables clave a tipos numericos, enteros y categoricos."""
    df = df.with_columns(
        [
            pl.col(COLUMNAS["edad_primer_union"]).cast(pl.Float64, strict=False),
            pl.col(COLUMNAS["num_hijos"]).cast(pl.Float64, strict=False),
            pl.col(COLUMNAS["factor_expansion"]).cast(pl.Float64, strict=False),
        ]
    )
    violencia = COLUMNAS["sufrio_violencia_pareja"]
    if df[violencia].dtype == pl.Utf8:
        df = df.with_columns(
            pl.col(violencia)
            .str.strip_chars()
            .str.to_lowercase()
            .replace_strict(
                {"si": 1, "sí": 1, "no": 0}, default=None, return_dtype=pl.Int8
            )
            .alias(violencia)
        )
    else:
        df = df.with_columns(pl.col(violencia).cast(pl.Int8, strict=False))
    for col in ("nom_entidad", "nivel_escolaridad", "estado_civil_desc"):
        df = df.with_columns(
            pl.col(COLUMNAS[col]).cast(pl.Utf8, strict=False)
        )
    print("[tipos] Variables numericas, binaria y categoricas convertidas.")
    return df


def normalizar_texto(df: pl.DataFrame) -> pl.DataFrame:
    """Unifica categorias."""
    expresiones = []
    for col in ("nom_entidad", "nivel_escolaridad", "estado_civil_desc"):
        nombre = COLUMNAS[col]
        expr = pl.col(nombre).cast(pl.Utf8).str.strip_chars()
        for patron, reemplazo in REEMPLAZOS_TEXTO.items():
            expr = expr.str.replace_all(re.escape(patron), reemplazo)
        expr = expr.str.to_lowercase().str.replace_all(r"\s+", " ")
        expresiones.append(expr.alias(nombre))
    df = df.with_columns(expresiones)
    df = df.with_columns(
        pl.col(COLUMNAS["nom_entidad"]).cast(pl.Categorical),
        pl.col(COLUMNAS["nivel_escolaridad"]).cast(pl.Categorical),
        pl.col(COLUMNAS["estado_civil_desc"]).cast(pl.Categorical),
    )
    print("[texto] Categorias normalizadas (minusculas y sin acentos).")
    return df


def tratar_nulos(df: pl.DataFrame) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Imputa nulos y devuelve el reporte de imputacion por columna."""
    n_inicial = df.height
    edad = COLUMNAS["edad_primer_union"]
    hijos = COLUMNAS["num_hijos"]
    peso = COLUMNAS["factor_expansion"]

    
    df = df.with_columns(
        pl.when(
            (pl.col(edad) < MIN_EDAD_UNION) | (pl.col(edad) > MAX_EDAD_UNION)
        )
        .then(None)
        .otherwise(pl.col(edad))
        .alias(edad),
        pl.when(pl.col(hijos) >= MAX_HIJOS_VALIDO)
        .then(None)
        .otherwise(pl.col(hijos))
        .alias(hijos),
    )

    sin_peso = df[peso].null_count()
    df = df.filter(pl.col(peso).is_not_null())
    print(f"[nulos] Eliminados por peso de expansion nulo: {sin_peso:,}")

   
    df = df.with_columns(
        pl.col(edad).is_null().alias("edad_primer_union_imputada"),
        pl.col(hijos).is_null().alias("num_hijos_imputado"),
    )

    mediana_edad = df[edad].median()
    mediana_hijos = df[hijos].median()
    registros = {
        "variable": [],
        "nulos_antes": [],
        "pct_antes": [],
        "estrategia": [],
    }
    for col, mediana in ((edad, mediana_edad), (hijos, mediana_hijos)):
        nulos = df[col].null_count()
        registros["variable"].append(col)
        registros["nulos_antes"].append(nulos)
        registros["pct_antes"].append(round(nulos / df.height * 100, 2))
        registros["estrategia"].append(f"mediana ({mediana})")
    df = df.with_columns(
        pl.col(edad)
        .fill_null(mediana_edad)
        .round()
        .cast(pl.Int64)
        .alias(edad),
        pl.col(hijos)
        .fill_null(mediana_hijos)
        .round()
        .cast(pl.Int64)
        .alias(hijos),
    )

    for col in ("nom_entidad", "nivel_escolaridad", "estado_civil_desc"):
        nombre = COLUMNAS[col]
        serie = df[nombre].cast(pl.Utf8)
        nulos = serie.null_count()
        moda = serie.drop_nulls().mode()
        reemplazo = moda[0] if moda.len() > 0 else "no especificado"
        registros["variable"].append(nombre)
        registros["nulos_antes"].append(nulos)
        registros["pct_antes"].append(round(nulos / df.height * 100, 2))
        registros["estrategia"].append(f"moda ({reemplazo})")
        df = df.with_columns(serie.fill_null(reemplazo).alias(nombre))
    df = df.with_columns(
        pl.col(COLUMNAS["nom_entidad"]).cast(pl.Categorical),
        pl.col(COLUMNAS["nivel_escolaridad"]).cast(pl.Categorical),
        pl.col(COLUMNAS["estado_civil_desc"]).cast(pl.Categorical),
    )

    reporte = pl.DataFrame(registros)
    print(f"[nulos] Registros finales: {df.height:,} (iniciales {n_inicial:,})")
    print(f"[nulos] Reporte de imputacion:\n{reporte}")
    return df, reporte


def normalizar_escalar(
    df: pl.DataFrame, metodo: str = "zscore"
) -> pl.DataFrame:
    """Escala variables numericas (zscore o minmax). Opcional, para modelado."""
    columnas = [COLUMNAS["edad_primer_union"], COLUMNAS["num_hijos"]]
    if metodo == "zscore":
        expr = lambda c: (pl.col(c) - pl.col(c).mean()) / pl.col(c).std()
    elif metodo == "minmax":
        expr = lambda c: (pl.col(c) - pl.col(c).min()) / (
            pl.col(c).max() - pl.col(c).min()
        )
    else:
        raise ValueError("metodo debe ser 'zscore' o 'minmax'")
    df = df.with_columns([expr(c).alias(c) for c in columnas])
    print(f"[escalado] Aplicado {metodo} a {columnas}")
    return df


def guardar_procesado(df: pl.DataFrame) -> None:
    """Guarda el dataset limpio y la version de features para modelado."""
    crear_directorios()
    df.write_parquet(ARCHIVO_LIMPIO)
    features = [c for c in COLUMNAS.values()]
    columnas_extra = [
        c
        for c in ("cve_entidad", "estrato_socioeconomico", "ingreso_pareja")
        if c in df.columns
    ]
    df.select(features + columnas_extra).write_parquet(ARCHIVO_FEATURES)
    print(f"[guardado] {ARCHIVO_LIMPIO}")
    print(f"[guardado] {ARCHIVO_FEATURES}")


def ejecutar_preprocesamiento() -> pl.DataFrame:
    """Ejecuta el pipeline completo de limpieza y devuelve el DataFrame."""
    crear_directorios()
    df = cargar_datos_crudos()
    analizar_calidad(df)
    df, _ = eliminar_duplicados(df)
    df = convertir_tipos(df)
    df = normalizar_texto(df)
    df, _ = tratar_nulos(df)
    guardar_procesado(df)
    return df


if __name__ == "__main__":
    ejecutar_preprocesamiento()
