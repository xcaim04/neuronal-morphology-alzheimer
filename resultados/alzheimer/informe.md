# Informe de Analisis Morfologico - Neuronas con Alzheimer

**Fecha del informe:** 2026-05-07 10:29:19

**Grupo:** Alzheimer

## Resumen General

| Indicador | Valor |
|-----------|-------|
| Total de neuronas analizadas | 13 |

## Estadisticas del Grupo

| Metrica | Media | Desv. Std | Min | Max |
|---------|-------|-----------|-----|-----|
| longitud_total_um | 2391.34 | 763.27 | 1313.87 | 3770.16 |
| bifurcaciones | 11.00 | 4.71 | 2.00 | 18.00 |
| terminales | 16.15 | 5.51 | 9.00 | 29.00 |
| strahler_max | 2.38 | 0.96 | 1.00 | 4.00 |

## Distribucion de Strahler

| Orden de Strahler | Cantidad | Porcentaje |
|-------------------|----------|------------|
| 1 | 3 | 23.1% |
| 2 | 3 | 23.1% |
| 3 | 6 | 46.2% |
| 4 | 1 | 7.7% |

## Archivos Procesados

| Archivo | Longitud (um) | Bifurcaciones | Terminales | Strahler |
|---------|---------------|---------------|------------|----------|
| SNc-071220-121B.CNG.swc | 2600.02 | 18 | 29 | 3 |
| SNc-080225-123.CNG.swc | 3770.16 | 18 | 23 | 3 |
| 1a_5xFAD_DG_GC_9.CNG.swc | 1776.08 | 13 | 15 | 3 |
| SNc-071214-118A.CNG.swc | 1694.0 | 8 | 12 | 3 |
| SNc-071220-120.CNG.swc | 3677.44 | 13 | 20 | 3 |
| SNc-071220-121A.CNG.swc | 1313.87 | 9 | 15 | 1 |
| SNc-080226-127.CNG.swc | 2126.61 | 8 | 18 | 3 |
| 1a_5xFAD_DG_GC_11.CNG.swc | 1696.69 | 17 | 18 | 4 |
| SNc-080311-131.CNG.swc | 2546.48 | 11 | 14 | 2 |
| SNc-071214-118B.CNG.swc | 2085.53 | 2 | 9 | 1 |
| SNc-080311-129.CNG.swc | 2647.49 | 9 | 11 | 2 |
| SNc-080312-132.CNG.swc | 2046.36 | 7 | 11 | 1 |
| SNc-080311-130.CNG.swc | 3106.66 | 10 | 15 | 2 |

## Notas

- Los datos fueron extraidos de archivos SWC usando morphio
- La longitud se calcula como suma de distancias euclidianas entre puntos
- El orden de Strahler se calcula recursivamente desde las terminales hasta la raiz


## Nota sobre el modelo

Estas neuronas provienen del modelo 5xFAD de Alzheimer, que sobreexpresa 5 mutaciones humanas asociadas a la enfermedad.

