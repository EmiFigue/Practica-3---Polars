"""Medidas descriptivas (localización y variabilidad) con y sin ponderar.

La ENDIREH es una encuesta con muestreo complejo: cada fila trae un
`factor_expansion` que dice a cuántas mujeres de la población representa.
Por eso, además de las medidas normales, aquí hay versiones PONDERADAS.

Todas las funciones reciben arreglos de NumPy (x = valores, w = pesos).
"""
import numpy as np


# ---------------------------------------------------------------- limpieza
def limpiar_par(x, w=None):
    """Quita los nulos de x (y de w si se da) y regresa arreglos de NumPy."""
    x = np.asarray(x, dtype=float)
    if w is None:
        return x[~np.isnan(x)], None
    w = np.asarray(w, dtype=float)
    ok = ~np.isnan(x) & ~np.isnan(w)
    return x[ok], w[ok]


# ------------------------------------------------------------ localización
def media_ponderada(x, w):
    """Media ponderada: suma(w*x) / suma(w)."""
    x, w = limpiar_par(x, w)
    return float(np.average(x, weights=w))


def cuantil_ponderado(x, w, q):
    """Cuantil ponderado (q entre 0 y 1).

    Se ordenan los datos, se acumula el peso y se toma el primer valor
    donde el peso acumulado llega a q (por ejemplo, 0.5 para la mediana).
    """
    x, w = limpiar_par(x, w)
    orden = np.argsort(x)
    x, w = x[orden], w[orden]
    acumulado = np.cumsum(w) / np.sum(w)
    return float(x[np.searchsorted(acumulado, q, side="left")])


def mediana_ponderada(x, w):
    return cuantil_ponderado(x, w, 0.5)


# ------------------------------------------------------------ variabilidad
def varianza_ponderada(x, w):
    """Varianza ponderada: suma(w*(x - media_w)^2) / suma(w)."""
    x, w = limpiar_par(x, w)
    m = np.average(x, weights=w)
    return float(np.sum(w * (x - m) ** 2) / np.sum(w))


def desv_ponderada(x, w):
    return float(np.sqrt(varianza_ponderada(x, w)))


def cv_ponderado(x, w):
    """Coeficiente de variación ponderado (en %)."""
    return desv_ponderada(x, w) / media_ponderada(x, w) * 100


def iqr_ponderado(x, w):
    return cuantil_ponderado(x, w, 0.75) - cuantil_ponderado(x, w, 0.25)


# ------------------------------------------------- versiones sin ponderar
def resumen_localizacion(x):
    """Media, mediana, moda, Q1, Q3, P10 y P90 SIN ponderar."""
    x, _ = limpiar_par(x)
    valores, cuentas = np.unique(x, return_counts=True)
    return {
        "media": float(np.mean(x)),
        "mediana": float(np.median(x)),
        "moda": float(valores[np.argmax(cuentas)]),
        "Q1": float(np.percentile(x, 25)),
        "Q3": float(np.percentile(x, 75)),
        "P10": float(np.percentile(x, 10)),
        "P90": float(np.percentile(x, 90)),
    }


def resumen_localizacion_pond(x, w):
    """Lo mismo pero PONDERADO por factor_expansion."""
    return {
        "media_pond": media_ponderada(x, w),
        "mediana_pond": mediana_ponderada(x, w),
        "Q1_pond": cuantil_ponderado(x, w, 0.25),
        "Q3_pond": cuantil_ponderado(x, w, 0.75),
        "P10_pond": cuantil_ponderado(x, w, 0.10),
        "P90_pond": cuantil_ponderado(x, w, 0.90),
    }


def resumen_variabilidad(x):
    """Rango, varianza, desviación, CV (%) e IQR SIN ponderar."""
    x, _ = limpiar_par(x)
    media = np.mean(x)
    desv = np.std(x, ddof=1)
    return {
        "rango": float(np.max(x) - np.min(x)),
        "varianza": float(np.var(x, ddof=1)),
        "desv_est": float(desv),
        "CV_%": float(desv / media * 100),
        "IQR": float(np.percentile(x, 75) - np.percentile(x, 25)),
    }


def resumen_variabilidad_pond(x, w):
    """Lo mismo pero PONDERADO por factor_expansion."""
    xx, _ = limpiar_par(x)
    return {
        "rango": float(np.max(xx) - np.min(xx)),   # el rango no usa pesos
        "varianza_pond": varianza_ponderada(x, w),
        "desv_est_pond": desv_ponderada(x, w),
        "CV_%_pond": cv_ponderado(x, w),
        "IQR_pond": iqr_ponderado(x, w),
    }


def proporcion_valor(x, valor):
    """Proporción de filas que valen exactamente `valor` (sirve para detectar imputación)."""
    x, _ = limpiar_par(x)
    return float(np.mean(x == valor))
