"""Pipeline principal: limpieza y preprocesamiento.

Uso:
    python main.py

"""

from config.columnas import COLUMNAS
from config.rutas import TABLES_DIR, crear_directorios
from src.cleaning.preprocesamiento import (
    analizar_calidad,
    cargar_datos_crudos,
    convertir_tipos,
    eliminar_duplicados,
    guardar_procesado,
    normalizar_texto,
    tratar_nulos,
)


def main() -> None:
    print("=" * 70)
    print(" Practica 3: polars")
    print("=" * 70)
    crear_directorios()

    print("\n[1/7] Carga de datos crudos")
    df = cargar_datos_crudos()

    print("\n[2/7] Analisis de calidad")
    calidad = analizar_calidad(df)
    calidad.write_csv(TABLES_DIR / "calidad_datos.csv")

    print("\n[3/7] Eliminacion de duplicados")
    df, n_duplicados = eliminar_duplicados(df)

    print("\n[4/7] Conversion de tipos")
    df = convertir_tipos(df)

    print("\n[5/7] Normalizacion de texto")
    df = normalizar_texto(df)

    print("\n[6/7] Tratamiento de nulos")
    df, imputacion = tratar_nulos(df)
    imputacion.write_csv(TABLES_DIR / "reporte_imputacion.csv")

    print("\n[7/7] Guardado de datos procesados")
    guardar_procesado(df)

    violencia = df[COLUMNAS["sufrio_violencia_pareja"]]
    print("\n" + "=" * 70)
    print("RESUMEN FINAL")
    print("=" * 70)
    print(f"Registros limpios: {df.height:,} (duplicados eliminados: {n_duplicados})")
    print(
        "Mujeres que reportaron violencia de pareja: "
        f"{violencia.sum():,} ({violencia.mean() * 100:.1f}% sin ponderar)"
    )
    peso = df[COLUMNAS["factor_expansion"]]
    proporcion_ponderada = (violencia * peso).sum() / peso.sum()
    print(f"Proporcion ponderada por factor de expansion: {proporcion_ponderada * 100:.1f}%")
    print(f"Tablas de limpieza en {TABLES_DIR}")
    print("Datos listos para el EDA.")


if __name__ == "__main__":
    main()
