# Informe de Analisis Morfologico - Neuronas con Alzheimer

**Fecha del informe:** 2026-11-15 20:27:58

**Grupo:** Alzheimer

## Resumen General

| Indicador | Valor |
|-----------|-------|
| Total de neuronas analizadas | 31 |

## Estadisticas del Grupo

| Metrica | Media | Desv. Std | Min | Max |
|---------|-------|-----------|-----|-----|
| puntos_totales | 14534.48 | 4913.18 | 5132.00 | 26908.00 |
| secciones | 113.16 | 35.43 | 26.00 | 171.00 |
| longitud_total_um | 6869.00 | 1977.02 | 3318.82 | 9401.27 |
| bifurcaciones | 54.06 | 17.51 | 11.00 | 83.00 |
| terminales | 59.10 | 17.94 | 15.00 | 88.00 |
| strahler_max | 3.77 | 0.43 | 3.00 | 4.00 |
| ratio_bifurcacion_terminal | 0.90 | 0.05 | 0.73 | 0.95 |

## Distribucion de Strahler

| Orden de Strahler | Cantidad | Porcentaje |
|-------------------|----------|------------|
| 3 | 7 | 22.6% |
| 4 | 24 | 77.4% |

## Archivos Procesados

| Archivo | Longitud (um) | Bifurcaciones | Terminales | Strahler |
|---------|---------------|---------------|------------|----------|
| 230323-0120x568633_NEW_Merged.CNG.swc | 4020.26 | 35 | 39 | 4 |
| 230323-0320x568633_new_Merged.CNG.swc | 5309.75 | 40 | 47 | 3 |
| 230324-0120x568633_new_Merged.CNG.swc | 8621.43 | 68 | 73 | 4 |
| 230328-0220x568633_new_Merged.CNG.swc | 5082.24 | 46 | 50 | 3 |
| 230328-0420x568633_new_Merged.CNG.swc | 4160.93 | 37 | 41 | 4 |
| 230328-0520x568633merged_new_Merged.CNG.swc | 7228.7 | 46 | 52 | 4 |
| 230517-02AB568CELL63320x-1_Merged.CNG.swc | 8981.63 | 58 | 63 | 4 |
| 230517-0320x568633_new_Merged.CNG.swc | 9401.27 | 67 | 74 | 4 |
| 230518-01AB568CELL63320x-1_Merged.CNG.swc | 4145.75 | 22 | 26 | 3 |
| 230518-0220x568633_new_Merged.CNG.swc | 3318.82 | 16 | 21 | 3 |
| 230518-03AB568CELL63320x-1_Merged.CNG.swc | 6902.15 | 56 | 60 | 4 |
| 230525-01AB568CELL63320x-1_Merged.CNG.swc | 7993.97 | 64 | 67 | 4 |
| 230525-02AB568CELL63320x-1_Merged.CNG.swc | 9341.97 | 66 | 73 | 3 |
| 230831-0156863320x-1_Merged.CNG.swc | 6248.1 | 59 | 64 | 4 |
| 230831-0256863320x-1_Merged.CNG.swc | 8346.95 | 83 | 88 | 4 |
| 230831-0456863320x-1_Merged.CNG.swc | 9359.36 | 58 | 63 | 4 |
| 230914-0356863320x-1_Merged.CNG.swc | 7899.45 | 71 | 76 | 4 |
| 230918-0156863320x-1_Merged.CNG.swc | 8682.16 | 66 | 72 | 4 |
| 230918-0320xnew-1_Merged.CNG.swc | 8386.51 | 61 | 67 | 4 |
| 230920-0120xnew-1_Merged.CNG.swc | 3681.08 | 11 | 15 | 3 |
| 230928-0120x2cells-1_L_Merged.CNG.swc | 8025.07 | 69 | 75 | 4 |
| 230928-0120x2cells-1_R_Merged.CNG.swc | 8184.07 | 72 | 78 | 4 |
| 230928-0220x-1_Merged.CNG.swc | 8949.43 | 79 | 85 | 4 |
| 230928-0420x-1_Merged.CNG.swc | 5629.42 | 51 | 55 | 4 |
| 231123-0120x-1_Merged.CNG.swc | 5186.54 | 49 | 53 | 4 |
| 231123-0220x-1_Merged.CNG.swc | 4358.04 | 38 | 43 | 4 |
| 231130-0120x-1_Merged.CNG.swc | 6593.28 | 57 | 61 | 4 |
| 231130-0320x-1_Merged.CNG.swc | 6915.32 | 65 | 70 | 4 |
| 231130-0420x-1_Merged.CNG.swc | 4826.16 | 41 | 45 | 3 |
| 231218-042cells20x-1_INNER_Merged.CNG.swc | 9268.98 | 61 | 67 | 4 |
| 231218-042cells20x-1_OUTER_Merged.CNG.swc | 7890.18 | 64 | 69 | 4 |

## Notas

- Los datos fueron extraidos de archivos SWC usando morphio
- La longitud se calcula como suma de distancias euclidianas entre puntos
- El orden de Strahler se calcula recursivamente desde las terminales hasta la raiz

## Procedencia

Neuronas con metadatos en el manifest: 31 de 31

| Campo | Valores (n) |
|-------|-------------|
| especie | mouse (31) |
| cepa | APP/PS1 (31) |
| region | hippocampus/CA1/stratum pyramidale (31) |
| tipo_celular | principal cell/pyramidal (31) |
| edad | 12.0 Month (18), 6.0 Month (13) |
| condicion | APP/PS1 transgenic (31) |

