"""Rutas absolutas del proyecto, todas derivadas de ROOT."""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = ROOT

CONFIG_DIR = ROOT / "config"
DATA_DIR = ROOT / "data"
DATA_RAW = DATA_DIR / "data-raw"
DATA_PROCESSED = DATA_DIR / "data-processed"
DATA_INPUT_MODEL = DATA_DIR / "data-input-model"
DATA_MODEL = DATA_DIR / "data-model"
SRC_DIR = ROOT / "src"
NOTEBOOKS_DIR = ROOT / "notebooks"
REPORTS_DIR = ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

RUTA_PARQUET_CRUDO = DATA_RAW / "endireh_2021.csv"
RUTA_PARQUET_LIMPIO = DATA_PROCESSED / "endireh_2021_clean.parquet"
RUTA_PARQUET_MODELO = DATA_INPUT_MODEL / "endireh_2021_features.parquet"
RUTA_FIGURAS = FIGURES_DIR
RUTA_TABLAS = TABLES_DIR

# Alias retrocompatibles de la Practica 3.
ARCHIVO_CRUDO = RUTA_PARQUET_CRUDO
ARCHIVO_LIMPIO = RUTA_PARQUET_LIMPIO
ARCHIVO_FEATURES = RUTA_PARQUET_MODELO

DIRECTORIOS = (
    DATA_RAW,
    DATA_PROCESSED,
    DATA_INPUT_MODEL,
    DATA_MODEL,
    SRC_DIR / "models",
    NOTEBOOKS_DIR,
    FIGURES_DIR,
    TABLES_DIR,
)


def crear_directorios() -> None:
    """Crea las carpetas del proyecto si no existen."""
    for directorio in DIRECTORIOS:
        directorio.mkdir(parents=True, exist_ok=True)
