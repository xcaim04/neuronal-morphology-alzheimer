# Neuronal Morphology Analysis for Alzheimer's Disease

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-Custom-red.svg)](LICENSE)
[![Morphio](https://img.shields.io/badge/morphio-3.3.6-green.svg)](https://github.com/BlueBrain/morphio)

A machine learning pipeline for analyzing neuronal morphology and classifying healthy vs. Alzheimer's-affected neurons using dendrite biomarkers.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Dataset](#dataset)
- [Usage](#usage)
- [Biomarkers](#biomarkers)
- [Machine Learning](#machine-learning)
- [Results](#results)
- [Limitations](#limitations)
- [License](#license)
- [Author](#author)

## 🧠 Overview

This project implements a complete pipeline to:

1. **Extract morphological biomarkers** from neuronal reconstruction files (SWC format)
2. **Analyze dendritic arborization** patterns using Strahler order, bifurcation counts, and dendrite length
3. **Classify neurons** as healthy or Alzheimer's-affected using Random Forest machine learning
4. **Visualize results** with comparative plots and statistical summaries

The pipeline is designed for research purposes and demonstrates how quantitative morphology can aid in understanding neurodegenerative processes.

## ✨ Features

| Feature | Description |
|---------|-------------|
| **SWC Parsing** | Load and parse neuronal morphology files using `morphio` |
| **Biomarker Extraction** | Compute 7+ quantitative biomarkers per neuron |
| **Batch Processing** | Process entire folders of neurons automatically |
| **Visualization** | Generate bar charts, boxplots, and scatter plots |
| **ML Classification** | Random Forest classifier with cross-validation |
| **Model Persistence** | Save and load trained models for future predictions |
| **Multi-group Reports** | Separate reports for healthy, Alzheimer, and comparative analysis |

## 📁 Project Structure

```
neurona/
├── dataset/
│   ├── sanas/                 # Healthy neurons (control group)
│   │   └── *.swc
│   └── enfermas/              # Alzheimer-affected neurons
│       └── *.swc
├── src/
│   ├── classification/        # ML classification module
│   │   ├── classifier.py     # Random Forest implementation
│   │   └── evaluator.py      # Cross-validation & metrics
│   ├── models/                # Data models
│   │   └── neuron.py         # Neuron class with Strahler calculation
│   ├── processing/            # Processing pipeline
│   │   └── analyzer.py       # Biomarker extraction
│   ├── visualization/         # Plot generation
│   │   └── plots.py          # Bar charts, boxplots, ROC curves
│   └── utils/                 # Utilities
│       └── geometry.py       # Euclidean distance calculations
├── resultados/                # Output directory
│   ├── sanas/                # Healthy neuron reports
│   ├── enfermas/             # Alzheimer neuron reports
│   └── evaluacion/           # ML evaluation metrics
├── modelos/                   # Trained models
│   └── clasificador_neurona.pkl
├── config.py                  # Path and constant configuration
├── main.py                    # Main pipeline script
├── train.py                   # Model training script
├── predecir.py                # Prediction script
└── requirements.txt           # Python dependencies
```

## 🔧 Installation

### Prerequisites

- Python 3.11 or higher
- `uv` package manager (recommended)

### Step 1: Clone or download the project

```bash
git clone https://github.com/yourusername/neuronal-morphology-alzheimer.git
cd neuronal-morphology-alzheimer
```

### Step 2: Install `uv` (if not already installed)

```bash
pip install uv
```

### Step 3: Create virtual environment and install dependencies

```bash
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -r requirements.txt
```

## 📂 Dataset

Neurons must be in **SWC format** (`.swc` files) organized in the following structure:

```
dataset/
├── sanas/      # Healthy neurons (label: 0)
└── enfermas/   # Alzheimer-affected neurons (label: 1)
```

### Where to obtain data

- [NeuroMorpho.org](https://neuromorpho.org) - Largest public repository
- Search examples:
  - **Healthy**: `control & hippocampus & mouse & C57BL/6`
  - **Alzheimer**: `5xFAD & hippocampus & mouse`

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
| Type | 1=soma, 2=axon, 3=dendrite, 4=apical dendrite |
| X, Y, Z | Coordinates in micrometers |
| Radius | Diameter/2 in micrometers |
| Parent | ID of parent point (-1 for soma) |

## 🚀 Usage

### 1. Extract biomarkers and generate reports

Process all neurons in `dataset/sanas/` and `dataset/enfermas/`:

```bash
uv run python main.py
```

**Output** (in `resultados/` folder):
- `sanas/informe.md` - Statistical report for healthy neurons
- `enfermas/informe.md` - Statistical report for Alzheimer neurons  
- `comparativa/informe_comparativo.md` - Cross-group comparison
- `sanas/comparacion_*.png` - Bar charts and boxplots
- `enfermas/comparacion_*.png`

### 2. Train machine learning classifier

```bash
uv run python train.py
```

**Output** (in `modelos/` and `resultados/evaluacion/`):
- `clasificador_neurona.pkl` - Trained Random Forest model
- `importancia_caracteristicas.csv` - Feature importance ranking
- `curva_roc_RandomForest.png` - ROC curve
- `matriz_confusion_RandomForest.png` - Confusion matrix

### 3. Predict new neurons from CSV

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

## 📊 Biomarkers Extracted

| Biomarker | Description | Calculation |
|-----------|-------------|-------------|
| **Total Length** | Sum of all dendrite segment lengths | Euclidean distance between consecutive points |
| **Bifurcations** | Number of branching points | Sections with ≥2 children |
| **Terminals** | Number of dendrite endpoints | Sections with 0 children |
| **Strahler Order** | Hierarchical complexity | Recursive rule: terminals=1, equal children+1 |
| **Sections** | Number of segments between bifurcations | Total section count |
| **Points** | Total reconstruction points | Number of SWC points |
| **Bif/Term Ratio** | Branching balance | Bifurcations / Terminals |

### Strahler Order Rules

```
If node has no children:       Order = 1
If children have same order:   Order = children_order + 1
If children have different:    Order = max(child_orders)
```

## 🤖 Machine Learning

### Algorithm: Random Forest

| Parameter | Value | Reason |
|-----------|-------|--------|
| `n_estimators` | 100 | Good balance accuracy/speed |
| `max_depth` | 4 | Prevents overfitting |
| `random_state` | 42 | Reproducibility |

### Features (based on importance)

1. **Bifurcations** (47% importance) - Most discriminative
2. **Terminals** (39% importance) - Second most important
3. **Total Length** (14% importance) - Moderately important
4. **Strahler** (0% importance) - Non-discriminative in this dataset

### Evaluation Metrics

- **Accuracy**: Overall correct predictions
- **Precision**: True positives / (True + False positives)
- **Recall**: True positives / (True + False negatives)
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under ROC curve

### Cross-Validation

Stratified 5-fold cross-validation ensures class balance across folds.

## 📈 Results

### Sample Results (20 neurons)

| Group | N | Length (μm) | Bifurcations | Terminals | Strahler |
|-------|---|-------------|--------------|-----------|----------|
| Healthy | 7 | 3519 ± 1091 | 53 ± 17 | 58 ± 16 | 2.1 ± 0.7 |
| Alzheimer | 13 | 2391 ± 763 | 11 ± 5 | 16 ± 6 | 2.4 ± 1.0 |

### Key Findings

- **79% reduction** in bifurcations in Alzheimer neurons
- **72% reduction** in terminals
- Bifurcations and terminals are the most discriminative biomarkers
- Strahler order does not differ significantly between groups

## ⚠️ Limitations

This project acknowledges the following limitations:

| Limitation | Impact |
|------------|--------|
| **Small sample size (n=20)** | Results may not generalize |
| **Species heterogeneity** | Healthy: mouse / Alzheimer: rat |
| **Age differences** | Healthy: young / Alzheimer: adult |
| **Region differences** | Healthy: CA1 / Alzheimer: substantia nigra |
| **No clinical validation** | For research use only |

These limitations make this a **proof-of-concept** rather than a clinically validated tool.

## 📝 Citation

If you use this software in your research, please cite:

```bibtex
@software{BlancoMoreira2026Neuronal,
  author = {Blanco Moreira, Carlos Javier},
  title = {Neuronal Morphology Analysis for Alzheimer's Disease},
  year = {2026},
  url = {https://github.com/yourusername/neuronal-morphology-alzheimer},
  note = {Machine learning pipeline for Alzheimer's classification}
}
```

## 📄 License

This project is under a **custom license**. See the [LICENSE](LICENSE) file for details.

**Summary:**
- ✅ Non-commercial academic/research use allowed
- ✅ Modification for personal use allowed
- ❌ Commercial use prohibited
- ❌ Medical/clinical diagnosis prohibited
- ❌ Redistribution without permission prohibited

For commercial licensing, contact: [carlosjavierblancomoreira@gmail.com]

## 👤 Author

**Carlos Javier Blanco Moreira**

- Email: carlojbm04@gmail.com
- GitHub: [@xcaim04](https://github.com/xcaim04)

## 🙏 Acknowledgments

- [NeuroMorpho.org](https://neuromorpho.org) for providing neuronal reconstruction data
- [BlueBrain/morphio](https://github.com/BlueBrain/morphio) for SWC parsing
- [scikit-learn](https://scikit-learn.org) for machine learning tools

---

**Disclaimer:** This software is for research purposes only. Not intended for clinical diagnosis or medical decision-making.

## requirements.txt

```bash
morphio>=3.3.6
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
scikit-learn>=1.3.0
joblib>=1.3.0
```


> Milestone 8: Refine model evaluation metrics