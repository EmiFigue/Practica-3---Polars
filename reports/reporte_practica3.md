# Reporte — Práctica 3: ENDIREH 2021

**Almacenes y Minería de Datos (UNAM)**
**Caso de estudio:** Encuesta Nacional sobre la Dinámica de las Relaciones en
los Hogares (ENDIREH) 2021, INEGI — violencia contra las mujeres.

---

## Resumen ejecutivo

Se construyó un pipeline reproducible en **polars** que carga, limpia,
documenta y analiza el consolidado ENDIREH 2021 (110 127 registros × 24
columnas). Tras eliminar 4 376 duplicados exactos y 455 registros sin factor
de expansión, quedaron **105 296 registros limpios**. El **18.1%** de las
mujeres reportó violencia de pareja (17.8% ponderado por el factor de
expansión). La edad a la primera unión (casos válidos) promedia 28.6 años
(mediana 21, media ponderada 28.68) y el número de hijos promedia 2.52
(mediana y moda 3, media ponderada 2.48). Se detectaron dos problemas reales
de datos: **nulos estructurales** en `edad_primer_union` (~92%) y
**mojibake** en los nombres de entidades, ambos tratados y documentados.

---

## 1. Introducción

El objetivo es aplicar el ciclo completo de minería de datos sobre ENDIREH
2021: auditoría de calidad, limpieza, normalización, análisis exploratorio y
cálculo de medidas descriptivas (localización, variabilidad y medias
ponderadas por el diseño muestral), dejando los datos listos para una etapa
de modelado.

## 2. Fuente de datos

- **ENDIREH 2021**, INEGI: <https://www.inegi.org.mx/programas/endireh/2021/>
- Archivo consolidado: `data/data-raw/endireh_2021.csv`
  (no versionado en Git; se entrega por separado).
- Variables clave: `edad_primer_union`, `num_hijos`, `nom_entidad`,
  `nivel_escolaridad`, `estado_civil_desc`, `sufrio_violencia_pareja` y
  `factor_expansion`. El mapeo y la validación están en
  `config/columnas.py`; si el CSV cambia de encabezados, el pipeline falla
  indicando la columna faltante.

## 3. Consideraciones éticas

1. **No estigmatizar** a mujeres, entidades ni grupos; los resultados son
   agregados y no señalan casos individuales.
2. **No afirmar causalidad**: se trata de un estudio observacional con datos
   auto-reportados; todas las diferencias son asociaciones descriptivas.
3. **Proteger la identidad**: no se publican microdatos ni combinaciones que
   permitan reidentificar personas.
4. **Reconocer sesgos**: subregistro por miedo, memoria o deseabilidad
   social; la ausencia de reporte **no** implica ausencia de violencia.
5. **Lenguaje respetuoso** y enfoque de derechos humanos en todo el reporte.

## 4. Comparación de frameworks y justificación

| Criterio | pandas | **polars** | PySpark |
|---|---|---|---|
| Rendimiento 1 máquina | Medio | **Muy alto** (multihilo, Arrow) | Alto con overhead de clúster |
| Evaluación perezosa | No | **Sí** (`LazyFrame`) | Sí |
| Sintaxis | Clásica | **Moderna y expresiva** | Tipo SQL |
| Infraestructura | 1 máquina | **1 máquina** | Clúster/JVM |
| Tipado estricto | Parcial | **Sí** | Sí |

**Decisión:** el consolidado pesa ≈10 MB y cabe en una sola máquina; usar
PySpark sería sobredimensionado. Polars da el mejor balance de rendimiento,
tipado y ergonomía, con interoperabilidad Arrow/parquet. pandas se usa
únicamente para las gráficas de seaborn.

## 5. Arquitectura y reproducibilidad

```
main.py                          # orquesta el pipeline
config/rutas.py                  # rutas absolutas (pathlib)
config/columnas.py               # mapeo y validación de columnas
src/cleaning/preprocesamiento.py # carga, calidad, limpieza, nulos, guardado
src/visualization/eda.py         # clasificación, medidas, figuras
notebooks/01_eda_endireh.ipynb   # narrativa ejecutada con outputs
reports/figures/ y reports/tables/
```

Ejecución: `python -m venv venv && source venv/bin/activate &&
pip install -r requirements.txt && python main.py`. Verificado con Python
3.14 y `polars==1.9.0`.

## 6. Preprocesamiento

### 6.1 Calidad inicial (110 127 registros)

| Variable | Nulos | % nulos | Únicos |
|---|---|---|---|
| edad_primer_union | 85 567 | 77.70 | 71 |
| num_hijos | 19 436 | 17.65 | 5 |
| ingreso_pareja | 61 147 | 55.52 | 546 |
| factor_expansion | 482 | 0.44 | 3 002 |
| nom_entidad | 0 | 0.00 | 32 |
| nivel_escolaridad | 0 | 0.00 | 6 |
| estado_civil_desc | 0 | 0.00 | 6 |
| sufrio_violencia_pareja | 0 | 0.00 | 2 |

Tabla completa: `reports/tables/calidad_datos.csv`.

### 6.2 Duplicados

El consolidado no incluye llave primaria (`id_vivienda` + `id_mujer`), por lo
que solo se eliminaron duplicados exactos con `unique()`: **4 376 registros**
(3.97%), quedando 105 751.

### 6.3 Conversión de tipos y normalización de texto

- `edad_primer_union`, `num_hijos`, `factor_expansion`: `Float64` durante la
  limpieza (el CSV trae `"98.0"`, `"99.0"`) y `Int64` tras imputar.
- `sufrio_violencia_pareja`: 0/1 (`Int8`); se soporta también el mapeo
  "Sí"/"No" a 1/0.
- `nom_entidad`, `nivel_escolaridad`, `estado_civil_desc`: categóricas en
  minúsculas y sin acentos.
- **Hallazgo:** el CSV mezcla UTF-8 correcto con texto doblemente codificado
  (*mojibake*): `QUER` + `Ã` + U+0089 + `TARO`. Se repararon los pares
  `Ã` + carácter de control antes de normalizar, evitando categorías
  duplicadas como `queretaro` vs `querã©taro`.

### 6.4 Tratamiento de nulos

| Variable | Nulos antes | % | Estrategia |
|---|---|---|---|
| edad_primer_union | 96 895 | 92.02 | mediana (21) + bandera |
| num_hijos | 19 190 | 18.22 | mediana (3) + bandera |
| nom_entidad | 0 | 0.00 | moda (tlaxcala) |
| nivel_escolaridad | 0 | 0.00 | moda (a1) |
| estado_civil_desc | 0 | 0.00 | moda (casada) |

Tabla completa: `reports/tables/reporte_imputacion.csv`.

Reglas adicionales: centinelas de `edad` (< 12 o > 98) y de `num_hijos`
(≥ 99) se tratan como nulos antes de imputar; `factor_expansion` **no se
imputa** (es un peso muestral) y sus 455 registros nulos se eliminaron.

**Nulos estructurales.** `edad_primer_union` solo tiene valor válido en
~8% de los registros: es una variable "no aplica" para la mayoría, no un
faltante aleatorio. Imputar el 92% con la mediana concentraría toda la
distribución en 21 años (IQR = 0), por lo que se crearon banderas
`edad_primer_union_imputada` y `num_hijos_imputado`; el EDA descriptivo se
calcula sobre **casos válidos** y la imputación se conserva en los parquet
para la etapa de modelado.

### 6.5 Salidas

- `data/data-processed/endireh_2021_clean.parquet` (dataset limpio completo).
- `data/data-input-model/endireh_2021_features.parquet` (variables
  seleccionadas, sin banderas de imputación).

## 7. Clasificación de variables

| Variable | Tipo de dato | Justificación |
|---|---|---|
| edad_primer_union | Cuantitativa discreta/continua | Edad en años; numérica |
| num_hijos | Cuantitativa discreta | Conteo entero de hijos |
| nom_entidad | Cualitativa nominal | Entidad federativa sin orden |
| nivel_escolaridad | Cualitativa ordinal | Orden educativo A1 < A2 < B1 < B2 < C1 < C2 |
| estado_civil_desc | Cualitativa nominal | Estado civil sin orden |
| sufrio_violencia_pareja | Cualitativa nominal/binaria | Indicador 0/1 |
| factor_expansion | Cuantitativa continua | Peso muestral |
| estrato_socioeconomico | Cualitativa ordinal | Estratos ordenados |
| ingreso_pareja | Cuantitativa continua | Pesos; incluye centinelas |

Tabla: `reports/tables/clasificacion_variables.csv`.

## 8. Medidas de localización

Calculadas sobre casos válidos (sin imputación). La media ponderada usa
`numpy.average(valores, weights=factor_expansion)`.

| Variable | n válido | % imputado | Media | Mediana | Moda | Q1 | Q2 | Q3 | P10 | P90 | Media ponderada | Diferencia |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| edad_primer_union | 8 401 | 92.02 | 28.61 | 21 | 20 | 16 | 21 | 30 | 13 | 46 | 28.68 | +0.07 |
| num_hijos | 86 106 | 18.22 | 2.52 | 3 | 3 | 1 | 3 | 3 | 1 | 4 | 2.48 | -0.03 |

**Interpretación.** En la edad a la primera unión la media (28.6) supera a la
mediana (21) y a la moda (20): la distribución tiene cola derecha por uniones
tardías; el 80% central va de 13 a 46 años. En hijos, media 2.52 y mediana 3
sugieren ligera asimetría izquierda. Las diferencias entre media simple y
ponderada son pequeñas (+0.07 años, −0.03 hijos) porque los pesos no están
fuertemente correlacionados con estas variables, pero la ponderada es la
medida representativa a nivel poblacional.

Tabla: `reports/tables/medidas_localizacion.csv`.

## 9. Medidas de variabilidad

| Variable | Grupo | n | Rango | Varianza | Desv. est. | CV (%) | IQR |
|---|---|---|---|---|---|---|---|
| edad_primer_union | Global | 8 401 | 86 | 485.19 | 22.03 | 77.00 | 14 |
| edad_primer_union | No violencia | 5 414 | 86 | 539.93 | 23.24 | 78.21 | 14 |
| edad_primer_union | Sí violencia | 2 987 | 86 | 379.92 | 19.49 | 73.25 | 15 |
| num_hijos | Global | 86 106 | 3 | 1.41 | 1.19 | 47.23 | 2 |
| num_hijos | No violencia | 68 763 | 3 | 1.40 | 1.18 | 46.96 | 2 |
| num_hijos | Sí violencia | 17 343 | 3 | 1.45 | 1.21 | 48.33 | 2 |

**Interpretación.** El CV es alto en todas las variables (>47%), lo que
indica poblaciones heterogéneas. En el grupo que reportó violencia la
varianza de la edad es **menor** (379.9 vs 539.9; CV 73.3% vs 78.2%),
mientras que el CV de hijos es **ligeramente mayor** (48.3% vs 47.0%),
consistente con mayor diversidad de condiciones de vida en ese grupo.

Tabla: `reports/tables/medidas_variabilidad.csv`.

## 10. Análisis visual

### 10.1 Histogramas

![Histograma de edad a la primera unión](figures/hist_edad_primer_union.png)

![Histograma del número de hijos](figures/hist_num_hijos.png)

### 10.2 Boxplots por grupo de violencia

![Boxplot de edad por violencia](figures/boxplot_edad_por_violencia.png)

![Boxplot de hijos por violencia](figures/boxplot_hijos_por_violencia.png)

### 10.3 Distribuciones categóricas

![Barras de nivel de escolaridad](figures/barras_nivel_escolaridad.png)

![Barras de estado civil](figures/barras_estado_civil.png)

![Top 10 entidades](figures/top10_entidades.png)

### 10.4 Violencia de pareja por entidad (ponderada)

![Violencia por entidad](figures/violencia_por_entidad.png)

Mayores proporciones ponderadas: **Guerrero (23.0%)**, Querétaro (21.4%) e
Hidalgo (21.3%). Menores: Chiapas (11.2%), Baja California (11.5%) y Nuevo
León (12.7%). Estas diferencias son descriptivas y no deben interpretarse
como causalidad; pueden reflejar composición socioeconómica, cultura de
denuncia o subregistro. Tabla: `reports/tables/violencia_por_entidad.csv`.

## 11. Respuestas al cuestionario

1. **Consideraciones éticas.** No estigmatizar ni revictimizar; evitar
   conclusiones causales (datos observacionales y auto-reportados); proteger
   la identidad con resultados agregados; usar lenguaje respetuoso;
   reconocer subregistro y sesgo de auto-reporte; recordar que no reportar
   no equivale a no vivir violencia.
2. **Media simple vs ponderada.** El factor de expansión indica cuántas
   personas de la población representa cada registro; la media ponderada
   reproduce el diseño muestral y es la estimación nacional, mientras que la
   simple solo describe la muestra. En este caso difieren poco
   (edad: 28.61 vs 28.68; hijos: 2.52 vs 2.48), lo que sugiere pesos
   relativamente homogéneos en estas variables, pero la ponderada sigue
   siendo la medida válida para inferencia.
3. **CV alto en el grupo con violencia.** El CV de hijos es mayor en el
   grupo que reportó violencia (48.33% vs 46.96%), y en la edad el CV es
   alto en ambos grupos (73–78%). Hipótesis: heterogeneidad por región,
   escolaridad, estrato socioeconómico y etapa de vida. Variables para
   confirmarlo: `nivel_escolaridad`, `nom_entidad`, `estrato_socioeconomico`
   y `num_hijos`, mediante análisis estratificados y pruebas de hipótesis.
4. Igual que la 2: la ponderación incorpora el diseño muestral y corrige la
   sobrerrepresentación de ciertos estratos; por eso es la medida de
   referencia.
5. Igual que la 3: antes de atribuir la dispersión a la violencia deben
   controlarse los estratos mencionados.

## 12. Decisiones de arquitectura y cálculo

- Separación `config/`, `src/cleaning/`, `src/visualization/`, `main.py` y
  notebook para reutilización y pruebas.
- Validación temprana de columnas: si el descriptor de ENDIREH cambia, el
  error es explícito.
- Duplicados solo exactos por ausencia de llave primaria.
- Centinelas y mojibake tratados antes de cualquier estadística.
- Medias ponderadas con `numpy.average` y pesos = `factor_expansion`.
- Tablas y figuras exportadas automáticamente por `main.py`.

## 13. Conclusiones

1. El pipeline en polars procesa 110 mil registros en segundos y genera
   artefactos reproducibles (parquet, CSV, PNG, notebook ejecutado).
2. La calidad de las variables categóricas y de violencia es alta; el reto
   está en `edad_primer_union`, con nulos estructurales que obligaron a
   usar banderas de imputación y análisis sobre casos válidos.
3. Se corrigió un problema real de codificación de texto y se documentó.
4. Los hallazgos son asociaciones descriptivas: no debe inferirse causalidad
   ni estigmatizar entidades con mayores proporciones.

## 14. Referencias

- INEGI. *ENDIREH 2021. Encuesta Nacional sobre la Dinámica de las
  Relaciones en los Hogares*. <https://www.inegi.org.mx/programas/endireh/2021/>
- Polars Documentation. <https://docs.pola.rs/>
- Apache Arrow. <https://arrow.apache.org/>
- McKinney, W. (2010). *Data Structures for Statistical Computing in
  Python*. SciPy.
- Documentación de seaborn y matplotlib.
