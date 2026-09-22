# Práctica 3 — Polars

Se procesa  la **Encuesta Nacional sobre la Dinámica de las Relacionesen los Hogares (ENDIREH) 2021** del INEGI para limpiar los datos, analizarlos exploratoriamente y calcular medidas de localización, variabilidad y medias ponderadas por el factor de expansión.

## Objetivo

Construir un pipeline reproducible que:

1. Cargue y valide el consolidado crudo de ENDIREH 2021.
2. Analice la calidad de los datos (nulos, duplicados, categorías, rangos).
3. Limpie, convierta tipos y normalice texto y nulos.
4. Genere tablas y figuras de EDA, incluidas medidas ponderadas.
5. Deje los datos listos para una etapa posterior de modelado.

## Fuente de datos

- **ENDIREH 2021**, INEGI: <https://www.inegi.org.mx/programas/endireh/2021/>
- Archivo consolidado esperado: `data/data-raw/endireh_2021.csv`


## Estructura de carpetas

```
Practica-3---Polars/
├── config/
│   ├── rutas.py              # rutas absolutas del proyecto
│   └── columnas.py           # mapeo y validación de columnas
├── data/
│   ├── data-raw/             # CSV crudo 
│   ├── data-processed/       # endireh_2021_clean.parquet
│   ├── data-input-model/     # endireh_2021_features.parquet
│   └── data-model/           
├── src/
│   ├── cleaning/preprocesamiento.py
│   ├── visualization/eda.py
│   └── models/
├── notebooks/01_eda_endireh.ipynb
├── reports/
│   ├── figures/              
│   ├── tables/               
│   └── reporte_practica3.md
├── main.py
├── requirements.txt
└── README.md
```

## Instalación

```bash
python -m venv venv
source venv/bin/activate        
pip install -r requirements.txt
```
## Ejecución

```bash
python main.py
jupyter notebook notebooks/01_eda_endireh.ipynb
```



## Decisiones de limpieza
 
- **Duplicados:** Se eliminan duplicados exactos con `unique()`.
- **Tipos:** edad, hijos y factor de expansión se manejan como. La binaria de violencia se mapea a 0/1.
- **Texto:** categorías en minúsculas y sin acentos. 
- **Nulos estructurales:** `edad_primer_union` solo tiene valor válido en
  ~8% de los registros.


