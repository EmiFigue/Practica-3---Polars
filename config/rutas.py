from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
DATA_RAW = DATA_DIR / "data-raw"
DATA_PROCESSED = DATA_DIR / "data-processed"
DATA_INPUT_MODEL = DATA_DIR / "data-input-model"
DATA_MODEL = DATA_DIR / "data-model"
SRC_DIR = BASE_DIR / "src"
NOTEBOOKS_DIR = BASE_DIR / "notebooks"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
TABLES_DIR = REPORTS_DIR / "tables"

ARCHIVO_CRUDO = DATA_RAW / "endireh_2021.csv"
ARCHIVO_LIMPIO = DATA_PROCESSED / "endireh_2021_clean.parquet"
ARCHIVO_FEATURES = DATA_INPUT_MODEL / "endireh_2021_features.parquet"

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
