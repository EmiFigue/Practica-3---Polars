"""Medidas de concentración sobre datos de la ENDIREH 2021.

Incluye la curva de Lorenz, el coeficiente de Gini clásico, el Gini
aplicado a frecuencias de categorías y la concentración territorial de
casos por entidad federativa. Se apoya en polars y numpy; no usa pandas.
"""

import numpy as np
import polars as pl


def lorenz_curve(valores: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Calcula la curva de Lorenz de una distribución.

    Ordena los valores de forma ascendente y devuelve la proporción
    acumulada de observaciones (población) y la proporción acumulada de
    la cantidad total. Ambas series inician en (0, 0).

    Parámetros:
        valores: arreglo unidimensional de cantidades no negativas.

    Regresa:
        Tupla (poblacion_acumulada, cantidad_acumulada) normalizada en
        [0, 1]. Un arreglo vacío devuelve ([0.0], [0.0]). Si la suma es
        cero, la cantidad acumulada se devuelve como NaN, igual que en
        gini().
    """
    valores = np.asarray(valores, dtype=float)
    n = valores.size
    if n == 0:
        return np.array([0.0]), np.array([0.0])

    ordenados = np.sort(valores)
    total = ordenados.sum()
    poblacion = np.concatenate(([0.0], np.arange(1, n + 1) / n))

    if total == 0:
        cantidad = np.full(n + 1, np.nan)
        cantidad[0] = 0.0
        return poblacion, cantidad

    cantidad = np.concatenate(([0.0], np.cumsum(ordenados) / total))
    return poblacion, cantidad


def gini(valores: np.ndarray) -> float:
    """Calcula el coeficiente de Gini clásico de una distribución.

    Aplica la fórmula ordenada ascendente:
        G = (2 * sum(i * x_i) - (n + 1) * sum(x_i)) / (n * sum(x_i))
    con i = 1..n. G = 0 indica igualdad perfecta y G cercano a 1 indica
    concentración máxima.

    Parámetros:
        valores: arreglo unidimensional de cantidades no negativas.

    Regresa:
        Coeficiente de Gini como float, o NaN si el arreglo está vacío o
        si la suma es cero.
    """
    valores = np.asarray(valores, dtype=float)
    n = valores.size
    if n == 0:
        return float("nan")

    ordenados = np.sort(valores)
    suma = ordenados.sum()
    if suma == 0:
        return float("nan")

    indices = np.arange(1, n + 1, dtype=float)
    numerador = 2.0 * np.sum(indices * ordenados) - (n + 1) * suma
    return float(numerador / (n * suma))


def gini_sobre_frecuencias(conteos: dict | pl.Series) -> float:
    """Calcula el Gini a partir de las frecuencias de una variable categórica.

    Parámetros:
        conteos: diccionario categoría -> conteo o polars.Series con los
            conteos (por ejemplo, la columna de un group_by().len()).

    Regresa:
        Coeficiente de Gini de la distribución de frecuencias.
    """
    if isinstance(conteos, pl.Series):
        valores = conteos.to_numpy()
    elif isinstance(conteos, dict):
        valores = np.array(list(conteos.values()), dtype=float)
    else:
        valores = np.asarray(conteos, dtype=float)
    return gini(valores)


def concentracion_por_entidad(
    df: pl.DataFrame,
    col_entidad: str = "nom_entidad",
    col_peso: str | None = "factor_expansion",
) -> pl.DataFrame:
    """Mide la concentración de casos por entidad federativa.

    Agrupa por col_entidad y calcula el número de casos sin ponderar, los
    casos ponderados por col_peso y la proporción ponderada de cada
    entidad. Si col_peso es None, los casos ponderados son iguales a los
    casos sin ponderar. Ordena de mayor a menor por casos ponderados y,
    para desempatar de forma reproducible, por nombre de entidad.

    Parámetros:
        df: datos a nivel registro.
        col_entidad: columna categórica de agrupación.
        col_peso: columna de ponderación; None desactiva la ponderación.

    Regresa:
        DataFrame con las columnas casos_sin_ponderar, casos_ponderados
        y proporcion_ponderada.
    """
    if col_peso is None:
        agrupado = df.group_by(col_entidad).agg(
            pl.len().alias("casos_sin_ponderar")
        )
        agrupado = agrupado.with_columns(
            pl.col("casos_sin_ponderar").alias("casos_ponderados")
        )
    else:
        agrupado = df.group_by(col_entidad).agg(
            pl.len().alias("casos_sin_ponderar"),
            pl.col(col_peso).sum().alias("casos_ponderados"),
        )

    total = agrupado["casos_ponderados"].sum()
    if total is not None and total > 0:
        agrupado = agrupado.with_columns(
            (pl.col("casos_ponderados") / total).alias("proporcion_ponderada")
        )
    else:
        agrupado = agrupado.with_columns(
            pl.lit(None, dtype=pl.Float64).alias("proporcion_ponderada")
        )

    return agrupado.sort(
        ["casos_ponderados", col_entidad], descending=[True, False]
    )
