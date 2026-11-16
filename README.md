# Neuronal Morphology Analysis for Alzheimer's Disease

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Custom-red.svg)](License)
[![Morphio](https://img.shields.io/badge/morphio-3.4.2+-green.svg)](https://github.com/BlueBrain/morphio)

A pipeline for extracting dendritic biomarkers from neuronal reconstructions (SWC) and comparing healthy vs. Alzheimer-model neurons, with statistical tests and a Random Forest classifier.

> **Main result (negative):** on a dataset of comparable groups (31 control vs. 31 APP/PS1 CA1 pyramidal neurons from the same study), **no biomarker differs significantly** between groups and **the classifier performs at chance level**. See [Results](#-results).

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Dataset](#-dataset)
- [Usage](#-usage)
- [Biomarkers](#-biomarkers-extracted)
- [Machine Learning](#-machine-learning)
- [Results](#-results)
- [Limitations](#️-limitations)
- [License](#-license)
- [Author](#-author)

## 🧠 Overview

This project implements a pipeline to:

1. **Extract morphological biomarkers** from the dendrites of neuronal reconstructions (SWC format)
2. **Compare groups statistically** (Mann-Whitney U, Holm correction, Cliff's delta)
3. **Evaluate a Random Forest classifier** with repeated stratified cross-validation against a dummy baseline
4. **Store and visualize results** in a local SQLite database, static reports and a Streamlit dashboard

It is a research/teaching tool. With the current dataset it is an analysis pipeline that reports a negative result, not a working classifier.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **SWC Parsing** | Load neuronal morphologies with `morphio` |
| **Biomarker Extraction** | 7 dendritic biomarkers per neuron (SWC types 3 and 4 only) |
| **Reproducible Dataset** | `scripts/descargar_dataset.py` downloads the data and writes `dataset/manifest.csv` with provenance |
| **Statistical Comparison** | Mann-Whitney U, Holm-Bonferroni correction, Cliff's delta, auto-generated interpretation and limitations |
| **ML Evaluation** | Random Forest, repeated stratified 5-fold CV (10 repeats), `DummyClassifier` baseline, out-of-fold confusion matrix and ROC |
| **Persistence** | Biomarkers and training runs stored in SQLite (`data/neurona.sqlite3`) |
| **Dashboard** | Streamlit app with Biomarcadores / Comparativa / Modelo / Predecir tabs |
| **Tests** | `pytest` suite under `tests/` |

## 📁 Project Structure

```
neuronal-morphology-alzheimer/
├── dataset/
│   ├── sanas/                  # Control neurons (label 0)
│   ├── enfermas/               # APP/PS1 neurons (label 1)
│   └── manifest.csv            # Provenance of every SWC file
├── scripts/
│   └── descargar_dataset.py    # Downloads the dataset from NeuroMorpho.org
├── src/
│   ├── classification/
│   │   ├── classifier.py       # Random Forest wrapper
│   │   └── evaluator.py        # Repeated CV, confusion matrix, ROC, JSON report
│   ├── models/
│   │   └── neuron.py           # Neuron class: biomarkers and Strahler order
│   ├── processing/
│   │   ├── analyzer.py         # Batch biomarker extraction
│   │   └── storage.py          # SQLite persistence
│   ├── visualization/
│   │   └── plots.py            # Bar charts, scatter plot, Strahler boxplot
│   └── utils/
│       └── geometry.py         # Euclidean distance / section length
├── tests/                      # pytest suite
├── resultados/                 # Generated outputs
│   ├── sanas/
│   ├── alzheimer/
│   ├── comparativa/
│   └── evaluacion/
├── modelos/
│   └── clasificador_neurona.pkl
├── data/                       # SQLite database (generated, git-ignored)
├── app.py                      # Streamlit dashboard
├── config.py                   # Paths and constants
├── main.py                     # Biomarker extraction + reports
├── train.py                    # Classifier evaluation and training
├── predecir.py                 # Prediction from CSV
├── datos_a_predecir.csv        # Example input for predecir.py
├── pyproject.toml
└── requirements.txt
```

## 🔧 Installation

### Prerequisites

- Python 3.12 or higher
- [`uv`](https://docs.astral.sh/uv/) package manager (recommended)

### Steps

```bash
git clone https://github.com/xcaim04/neuronal-morphology-alzheimer.git
cd neuronal-morphology-alzheimer
uv sync
```

`uv sync` creates the virtual environment and installs the dependencies from `pyproject.toml` / `uv.lock` (including the `dev` group with `pytest`).

Without `uv`:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 📂 Dataset

The dataset contains **31 control vs. 31 Alzheimer-model neurons**, all from the **Booker archive** of [NeuroMorpho.org](https://neuromorpho.org) (PMID 41651661, doi [10.1523/ENEURO.0099-23.2025](https://doi.org/10.1523/ENEURO.0099-23.2025)):

| | Control (`dataset/sanas/`) | Alzheimer (`dataset/enfermas/`) |
|---|---|---|
| Species | Mouse | Mouse |
| Strain | C57BL/6J | APP/PS1 transgenic |
| Region / cell type | CA1, stratum pyramidale / pyramidal | CA1, stratum pyramidale / pyramidal |
| Age 6 months | 13 | 13 |
| Age 12 months | 18 | 18 |

Selection (see the docstring of `scripts/descargar_dataset.py`): only `_Merged` reconstructions (full dendritic tree), only 6- and 12-month animals, and files that `morphio` cannot open are discarded.

`dataset/manifest.csv` records the provenance of each file (species, strain, region, cell type, age, condition, URL). To reproduce the dataset:

```bash
uv run python scripts/descargar_dataset.py
```

The previous dataset (20 files: rat substantia nigra neurons, 5xFAD dentate gyrus granule cells and controls from another lab) was removed because the groups were not comparable.

### SWC file format

The SWC format contains 7 columns per line:

```
ID  Type    X       Y       Z       Radius  Parent
1   1       0.0     0.0     0.0     5.0     -1
2   3       10.0    5.0     2.0     0.5     1
...
```

| Column | Description |
|--------|-------------|
| ID | Unique point identifier |
| Type | 1=soma, 2=axon, 3=basal dendrite, 4=apical dendrite |
| X, Y, Z | Coordinates in micrometers |
| Radius | Diameter/2 in micrometers |
| Parent | ID of parent point (-1 for root) |

## 🚀 Usage

### 1. Extract biomarkers and generate reports

```bash
uv run python main.py
```

Processes `dataset/sanas/` and `dataset/enfermas/` and stores the biomarkers in `data/neurona.sqlite3`.

**Output** (in `resultados/`):
- `sanas/` and `alzheimer/`: `dataset_biomarcadores.csv`, `informe.md` (with provenance from the manifest), `bifurcaciones_vs_longitud.png`, `strahler_boxplot.png`
- `comparativa/`: `informe_comparativo.md` (statistical tests, interpretation, limitations), `comparacion_<biomarker>.png`, `bifurcaciones_vs_longitud.png`, `strahler_boxplot.png`

### 2. Evaluate and train the classifier

Requires the CSVs produced by `main.py`.

```bash
uv run python train.py
```

**Output** (in `modelos/` and `resultados/evaluacion/`):
- `clasificador_neurona.pkl` - Random Forest trained on all data
- `metricas_RandomForest.csv` - CV metrics (columns `metrica,mean,std`)
- `informe_evaluacion.json` - CV metrics for the model and the baseline, class counts, hyperparameters, features
- `importancia_caracteristicas.csv` - Feature importances
- `matriz_confusion_RandomForest.png`, `curva_roc_RandomForest.png` - Out-of-fold confusion matrix and ROC curve

The training run is also stored in `data/neurona.sqlite3`.

### 3. Dashboard

```bash
uv run streamlit run app.py
```

Reads the SQLite database and the files in `resultados/`; run `main.py` and `train.py` first.

### 4. Predict new neurons from CSV

> ⚠️ With the current model, predictions have **no value**: cross-validated performance is at chance level (see [Results](#-results)).

Create a CSV file with the following columns:

```csv
longitud_total_um,bifurcaciones,terminales,strahler_max
3500,50,55,3
2000,10,15,2
2800,30,35,2
```

Then run:

```bash
uv run python predecir.py datos_a_predecir.csv -s resultados.csv
```

**Or from Python:**

```python
from predecir import predecir_desde_csv

df_resultado = predecir_desde_csv("datos.csv", "predicciones.csv")
print(df_resultado[["prediccion", "confianza_porcentaje"]])
```

### 5. Tests

```bash
uv run pytest
```

## 📊 Biomarkers Extracted

All biomarkers are computed over dendritic sections only (SWC types 3 and 4); axons are ignored.

| Biomarker | Column | Calculation |
|-----------|--------|-------------|
| **Total Length** | `longitud_total_um` | Sum of Euclidean distances between consecutive points of each section |
| **Bifurcations** | `bifurcaciones` | Sections with ≥2 children |
| **Terminals** | `terminales` | Sections with 0 children |
| **Strahler Order** | `strahler_max` | Maximum over all dendritic root sections |
| **Sections** | `secciones` | Number of dendritic sections |
| **Points** | `puntos_totales` | Number of points in dendritic sections |
| **Bif/Term Ratio** | `ratio_bifurcacion_terminal` | Bifurcations / Terminals |

### Strahler Order Rules

```
If node has no children:                    Order = 1
If ≥2 children share the maximum order:     Order = max + 1
Otherwise:                                  Order = max(child_orders)
```

## 🤖 Machine Learning

### Algorithm: Random Forest

| Parameter | Value |
|-----------|-------|
| `n_estimators` | 100 |
| `max_depth` | 4 |
| `random_state` | 42 |

Features: `longitud_total_um`, `bifurcaciones`, `terminales`, `strahler_max`.

### Evaluation

- **Repeated stratified k-fold CV**: 5 folds x 10 repeats; mean ± std over the 50 folds of accuracy, precision, recall, F1 and ROC AUC
- **Baseline**: `DummyClassifier(strategy="most_frequent")` evaluated with the same CV
- **Confusion matrix and ROC curve**: out-of-fold predictions from a single stratified 5-fold split
- The final model is then trained on all data and saved to `modelos/`

## 📈 Results

### Group comparison (`resultados/comparativa/informe_comparativo.md`)

Two-sided Mann-Whitney U per biomarker, Holm-Bonferroni correction over the 7 biomarkers (α = 0.05). Difference = (Alzheimer − control) / control.

| Biomarker | Control (mean ± std) | Alzheimer (mean ± std) | Difference | p | p (Holm) | Cliff's δ |
|-----------|----------------------|------------------------|------------|---|----------|-----------|
| puntos_totales | 13398.29 ± 5155.23 | 14534.48 ± 4913.18 | +8.5% | 0.4223 | 1.0000 | +0.12 |
| secciones | 112.61 ± 27.05 | 113.16 ± 35.43 | +0.5% | 0.6523 | 1.0000 | +0.07 |
| longitud_total_um | 6345.98 ± 1651.98 | 6869.00 ± 1977.02 | +8.2% | 0.2102 | 1.0000 | +0.19 |
| bifurcaciones | 53.52 ± 13.60 | 54.06 ± 17.51 | +1.0% | 0.5876 | 1.0000 | +0.08 |
| terminales | 59.10 ± 13.48 | 59.10 ± 17.94 | +0.0% | 0.6880 | 1.0000 | +0.06 |
| strahler_max | 3.61 ± 0.50 | 3.77 ± 0.43 | +4.5% | 0.1746 | 1.0000 | +0.16 |
| ratio_bifurcacion_terminal | 0.90 ± 0.03 | 0.90 ± 0.05 | +0.4% | 0.3904 | 1.0000 | +0.13 |

**No biomarker differs significantly between groups.** All differences in means are between 0% and +8.5%, with small or negligible effect sizes.

### Classifier (`resultados/evaluacion/informe_evaluacion.json`)

| Model | Accuracy | Precision | Recall | F1 | ROC AUC |
|-------|----------|-----------|--------|----|---------|
| Random Forest | 0.498 ± 0.130 | 0.502 ± 0.160 | 0.489 ± 0.208 | 0.480 ± 0.156 | 0.501 ± 0.151 |
| Baseline (most frequent) | 0.485 ± 0.019 | 0.092 ± 0.185 | 0.200 ± 0.400 | 0.126 ± 0.253 | 0.500 ± 0.000 |

**The classifier performs at chance level**: its accuracy and AUC are indistinguishable from the baseline. Feature importances (`importancia_caracteristicas.csv`) are not meaningful for a model that does not discriminate.

### About earlier results

Previous versions of this README reported a 79% reduction in bifurcations and a perfect classification accuracy. Those results were an artifact of comparing different cell types and species (rat substantia nigra / mouse dentate gyrus vs. mouse CA1), combined with a bug that computed the Strahler order on the first tree only. They should not be cited.

## ⚠️ Limitations

- **Sex is confounded with genotype within each age**: at 6 months all 13 APP/PS1 neurons come from males vs. 9 male / 4 female controls; at 12 months APP/PS1 is 12 female / 6 male vs. 12 male / 6 female controls.
- **Non-independent samples**: several neurons may come from the same animal or slice, and the NeuroMorpho API provides no animal ID, so the CV does not group by animal.
- **No diameters**: the reconstructions do not contain real radii, so no diameter-based biomarkers are possible.
- **Truncated trees**: dendrites are partially cut by the slicing (NeuroMorpho integrity: "Dendrites Moderate").
- **Excluded data**: 1-month animals were excluded (no amyloid pathology yet), and 5 SWC files were discarded because `morphio` cannot open them.
- **Unverified study details**: it was not checked in the original article whether controls are littermates or which APP/PS1 line was used.
- **Length definition**: total length does not include the segment from the soma to the first point of each dendrite (`morphio` behavior).
- **Low statistical power**: with n=31 per group, absence of significance does not demonstrate absence of effect.
- **No clinical validation**: mouse model data, for research use only.

## 📝 Citation

If you use this software in your research, please cite:

```bibtex
@software{BlancoMoreira2026Neuronal,
  author = {Blanco Moreira, Carlos Javier},
  title = {Neuronal Morphology Analysis for Alzheimer's Disease},
  year = {2026},
  url = {https://github.com/xcaim04/neuronal-morphology-alzheimer},
  note = {Dendritic morphology analysis pipeline, healthy vs. Alzheimer-model neurons}
}
```

## 📄 License

This project is under a **custom license**. See the [License](License) file for details.

**Summary:**
- ✅ Non-commercial academic/research use allowed
- ✅ Modification for personal use allowed
- ❌ Commercial use prohibited
- ❌ Medical/clinical diagnosis prohibited
- ❌ Redistribution without permission prohibited

For commercial licensing, contact: [carlojbm04@gmail.com]

## 👤 Author

**Carlos Javier Blanco Moreira**

- Email: carlojbm04@gmail.com
- GitHub: [@xcaim04](https://github.com/xcaim04)

## 🙏 Acknowledgments

- [NeuroMorpho.org](https://neuromorpho.org) for providing neuronal reconstruction data, and the authors of the Booker archive
- [BlueBrain/morphio](https://github.com/BlueBrain/morphio) for SWC parsing
- [scikit-learn](https://scikit-learn.org) for machine learning tools

---

**Disclaimer:** This software is for research purposes only. Not intended for clinical diagnosis or medical decision-making.
