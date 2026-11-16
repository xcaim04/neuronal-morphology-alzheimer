# Changelog

## 2026-06-03
- Initial project foundation

## 2026-06-03
- Dataset structure and preprocessing plan

## 2026-06-05
- SWC parser and neuron data model

## 2026-06-05
- Add morphology geometry utilities

## 2026-06-18
- Prototype biomarker extraction pipeline

## 2026-06-18
- Validate healthy vs Alzheimer features

## 2026-07-02
- Train first classification baseline

## 2026-07-02
- Refine model evaluation metrics

## 2026-07-21
- Prepare comparative study reports

## 2026-07-21
- Improve visualization outputs

## 2026-08-12
- Stabilize model persistence workflow

## 2026-08-12
- Add prediction pipeline for new samples

## 2026-09-01
- Compare performance across groups

## 2026-09-01
- Document biomarker definitions

## 2026-09-23
- Refine training and report generation

## 2026-10-08
- Finalize dataset handling and validations

## 2026-10-08
- Improve reproducibility and documentation

## 2026-10-29
- Prepare final reproducible release notes

## 2026-10-29
- Release candidate for morphology analysis

## 2026-11-03
- Finalize project status and reporting

## 2026-11-03
- Project complete and documented

## 2026-11-15
- Replace the dataset: 31 control (C57BL/6J) vs 31 APP/PS1 mouse CA1 pyramidal neurons, 6 and 12 months, all from the NeuroMorpho Booker archive (PMID 41651661). Remove the 20 previous files (rat SNc, 5xFAD dentate gyrus, controls from another lab) because the groups were not comparable
- Add `dataset/manifest.csv` with per-file provenance and `scripts/descargar_dataset.py` to reproduce the dataset
- Fix Strahler order: computed over all dendritic roots instead of only the first tree
- Fix biomarkers: count dendrites only (SWC types 3 and 4), not axons
- Make the output deterministic
- Evaluation: repeated stratified CV (5 folds x 10 repeats) with a `DummyClassifier` baseline, out-of-fold confusion matrix and ROC, `informe_evaluacion.json`; Random Forest only
- Comparative report: Mann-Whitney U, Holm correction, Cliff's delta, interpretation and limitations generated from the data and the manifest
- Store biomarkers and training runs in SQLite (`data/neurona.sqlite3`)
- Add Streamlit dashboard (`app.py`) and pytest suite
- Result: no biomarker differs significantly between groups (all Holm-adjusted p = 1.0) and the classifier performs at chance level (CV accuracy 0.50 ± 0.13, AUC 0.50 ± 0.15). The previous results (79% fewer bifurcations, accuracy 1.0) were an artifact of non-comparable groups and the Strahler bug
- Update README and requirements.txt
