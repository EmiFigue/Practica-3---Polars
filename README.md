# Práctica 4 — Medidas de concentración, heterogeneidad y comparación

### Notebooks

| Notebook | Contenido 
| --- | --- | --- |
| `notebooks/01b_medidas_localizacion.ipynb` | Media, mediana, moda, cuantiles y media ponderada por `factor_expansion`. 
| `notebooks/02b_medidas_variabilidad.ipynb` | Rango, varianza, desviación estándar, coeficiente de variación e IQR. 
| `notebooks/03_medidas_heterogeneidad.ipynb` | Riqueza de categorías, Shannon y Gini-Simpson. 
| `notebooks/04_medidas_concentracion.ipynb` | Curva de Lorenz, Gini territorial ponderado, Gini sobre frecuencias y top-10 de entidades. 
| `notebooks/05_comparacion_gini_entropia.ipynb` | Comparación entre el Gini y los índices de entropía (Shannon / Gini-Simpson). 


### Cómo correr los notebooks

Los notebooks importan `config.rutas` y `src.*`,deben
ejecutarse con la raíz del proyecto como directorio de trabajo:

```bash
source venv/bin/activate
pip install -r requirements.txt

jupyter notebook
```

o de forma no interactiva:

```bash
jupyter nbconvert --to notebook --execute --inplace notebooks/04_medidas_concentracion.ipynb
```

Las figuras se guardan en `reports/figures/` y las tablas en
`reports/tables/`.
