"""Medidas de heterogeneidad para variables cualitativas.

Gini-Simpson, índice de variación cualitativa (IQV) y entropía de Shannon
calculados sobre conteos de categorías. Usa polars y numpy.
"""

import numpy as np
import polars as pl


def _a_arreglo(conteos: dict | pl.Series) -> np.ndarray:
    """Convierte conteos en arreglo unidimensional de float."""
    if isinstance(conteos, pl.Series):
        return conteos.to_numpy().astype(float)
    if isinstance(conteos, dict):
        return np.array(list(conteos.values()), dtype=float)
    return np.asarray(conteos, dtype=float)


def gini_simpson(conteos: dict | pl.Series) -> float:
    """Gini-Simpson = 1 - sum(p_i^2)."""
    valores = _a_arreglo(conteos)
    total = valores.sum()
    if total == 0:
        return float("nan")
    p = valores / total
    return float(1.0 - np.sum(p**2))


def iqv(conteos: dict | pl.Series) -> float:
    """Índice de Variación Cualitativa (Wilcox 1973)."""
    valores = _a_arreglo(conteos)
    k = int(np.count_nonzero(valores))
    if k <= 1:
        return float("nan")
    return float(k * gini_simpson(valores) / (k - 1))


def entropia_shannon(conteos: dict | pl.Series, base: float = 2.0) -> float:
    """Entropía de Shannon en bits (base 2 por defecto)."""
    valores = _a_arreglo(conteos)
    total = valores.sum()
    if total == 0:
        return float("nan")
    p = valores[valores > 0] / total
    return float(-np.sum(p * np.log(p) / np.log(base)))


def entropia_maxima(k: int, base: float = 2.0) -> float:
    """Entropía máxima posible para k categorías."""
    if k <= 0:
        return float("nan")
    return float(np.log(k) / np.log(base))


def tabla_heterogeneidad(
    df: pl.DataFrame,
    variables: list[str],
) -> pl.DataFrame:
    """Tabla de k, Gini-Simpson, IQV, Shannon, Shannon máximo y relativo por variable."""
    filas = []
    for variable in variables:
        conteos = df.group_by(variable).agg(pl.len().alias("n"))["n"]
        shannon = entropia_shannon(conteos)
        shannon_max = entropia_maxima(conteos.len())
        filas.append(
            {
                "variable": variable,
                "k": conteos.len(),
                "gini_simpson": gini_simpson(conteos),
                "iqv": iqv(conteos),
                "shannon": shannon,
                "shannon_max": shannon_max,
                "shannon_rel": shannon / shannon_max if shannon_max > 0 else float("nan"),
            }
        )
    return pl.DataFrame(filas)
