# Informe de Analisis Morfologico - Neuronas Sanas

**Fecha del informe:** 2026-05-07 10:29:18

**Grupo:** Sana

## Resumen General

| Indicador | Valor |
|-----------|-------|
| Total de neuronas analizadas | 7 |

## Estadisticas del Grupo

| Metrica | Media | Desv. Std | Min | Max |
|---------|-------|-----------|-----|-----|
| longitud_total_um | 3519.71 | 1091.46 | 1968.79 | 5416.03 |
| bifurcaciones | 52.57 | 16.88 | 29.00 | 73.00 |
| terminales | 58.43 | 16.34 | 35.00 | 78.00 |
| strahler_max | 2.14 | 0.69 | 1.00 | 3.00 |

## Distribucion de Strahler

| Orden de Strahler | Cantidad | Porcentaje |
|-------------------|----------|------------|
| 1 | 1 | 14.3% |
| 2 | 4 | 57.1% |
| 3 | 2 | 28.6% |

## Archivos Procesados

| Archivo | Longitud (um) | Bifurcaciones | Terminales | Strahler |
|---------|---------------|---------------|------------|----------|
| control-8-wt.CNG.swc | 3764.81 | 62 | 67 | 2 |
| control-20-wt.CNG.swc | 2637.02 | 33 | 40 | 3 |
| control-19-wt.CNG.swc | 4017.44 | 68 | 74 | 2 |
| control-9-wt.CNG.swc | 3278.59 | 48 | 55 | 2 |
| control-15-wt.CNG.swc | 5416.03 | 73 | 78 | 1 |
| control-5-wt.CNG.swc | 3555.3 | 55 | 60 | 3 |
| control-12-wt.CNG.swc | 1968.79 | 29 | 35 | 2 |

## Notas

- Los datos fueron extraidos de archivos SWC usando morphio
- La longitud se calcula como suma de distancias euclidianas entre puntos
- El orden de Strahler se calcula recursivamente desde las terminales hasta la raiz


## Nota sobre la edad

Estas neuronas provienen de animales jovenes ('young'), lo que explica los valores moderados de Strahler y complejidad dendritica.

