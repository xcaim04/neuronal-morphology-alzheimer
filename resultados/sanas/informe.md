# Informe de Analisis Morfologico - Neuronas Sanas

**Fecha del informe:** 2026-11-15 20:27:57

**Grupo:** Sana

## Resumen General

| Indicador | Valor |
|-----------|-------|
| Total de neuronas analizadas | 31 |

## Estadisticas del Grupo

| Metrica | Media | Desv. Std | Min | Max |
|---------|-------|-----------|-----|-----|
| puntos_totales | 13398.29 | 5155.23 | 3558.00 | 26629.00 |
| secciones | 112.61 | 27.05 | 66.00 | 163.00 |
| longitud_total_um | 6345.98 | 1651.98 | 3325.60 | 9288.32 |
| bifurcaciones | 53.52 | 13.60 | 30.00 | 79.00 |
| terminales | 59.10 | 13.48 | 36.00 | 84.00 |
| strahler_max | 3.61 | 0.50 | 3.00 | 4.00 |
| ratio_bifurcacion_terminal | 0.90 | 0.03 | 0.83 | 0.94 |

## Distribucion de Strahler

| Orden de Strahler | Cantidad | Porcentaje |
|-------------------|----------|------------|
| 3 | 12 | 38.7% |
| 4 | 19 | 61.3% |

## Archivos Procesados

| Archivo | Longitud (um) | Bifurcaciones | Terminales | Strahler |
|---------|---------------|---------------|------------|----------|
| 230316-0120x568633_CELL2_R_NEW_Merged.CNG.swc | 7353.4 | 52 | 59 | 4 |
| 230316-0320x568633_cell_1left_NEW_Merged.CNG.swc | 4046.39 | 32 | 37 | 3 |
| 230316-0420x568633_left_NEW_Merged.CNG.swc | 3993.86 | 34 | 40 | 4 |
| 230323-0420x568633_new_Merged.CNG.swc | 7526.89 | 57 | 63 | 4 |
| 230328-0120x568633_new_Merged.CNG.swc | 3706.44 | 43 | 46 | 4 |
| 230328-0320x568633_new_Merged.CNG.swc | 6216.49 | 45 | 52 | 4 |
| 230516-0320x568633_new_Merged.CNG.swc | 8019.25 | 65 | 69 | 4 |
| 230516-0420x568633_new_Merged.CNG.swc | 4897.28 | 46 | 54 | 3 |
| 230519-01AB568CELL63320x-1_Merged.CNG.swc | 5207.63 | 37 | 42 | 3 |
| 230519-0220x568633_new_Merged.CNG.swc | 4480.82 | 38 | 45 | 3 |
| 230526-02AB568CELL63320x-1_Merged.CNG.swc | 8679.85 | 54 | 60 | 3 |
| 230526-0320x568633_new_Merged.CNG.swc | 6665.66 | 61 | 69 | 3 |
| 230824-0156863320x-1_Merged.CNG.swc | 7051.67 | 62 | 68 | 4 |
| 230824-0256863320x2cells-1_OUTER_Merged.CNG.swc | 7918.58 | 65 | 72 | 3 |
| 230824-0356863320x2cells-1_INNER_Merged.CNG.swc | 3325.6 | 35 | 40 | 3 |
| 230824-0356863320x2cells-1_Merged.CNG.swc | 7149.89 | 79 | 84 | 4 |
| 230824-0420x-1_BR_Merged.CNG.swc | 5294.43 | 37 | 43 | 4 |
| 230824-0420x-1_DIM_Merged.CNG.swc | 5991.55 | 51 | 56 | 4 |
| 230914-0256863320x-1_Merged.CNG.swc | 7280.88 | 60 | 64 | 4 |
| 230914-052cells20xnew-1_BR_Merged.CNG.swc | 4437.11 | 38 | 44 | 3 |
| 230914-052cells20xnew-1_DIM_merged.CNG.swc | 7055.5 | 61 | 68 | 4 |
| 230919-0156863320x_Merged.CNG.swc | 8248.56 | 62 | 67 | 4 |
| 230919-0356863320x_Merged.CNG.swc | 4091.41 | 30 | 36 | 3 |
| 230920-0256863320x_Merged.CNG.swc | 9288.32 | 71 | 77 | 4 |
| 230921-0356863320x_INNERDIM_Merged.CNG.swc | 6409.55 | 52 | 56 | 4 |
| 230921-0356863320x_OUTERBR_comp_Merged.CNG.swc | 6930.67 | 65 | 69 | 4 |
| 231010-0120x_Merged.CNG.swc | 8798.96 | 67 | 72 | 3 |
| 231219-012cells20x_BR_Merged.CNG.swc | 6790.56 | 73 | 78 | 4 |
| 231219-012cells20x_DIM_Merged.CNG.swc | 5141.49 | 56 | 61 | 3 |
| 231219-0220x_Merged.CNG.swc | 7365.98 | 63 | 69 | 4 |
| 231219-0320x_Merged.CNG.swc | 7360.64 | 68 | 72 | 4 |

## Notas

- Los datos fueron extraidos de archivos SWC usando morphio
- La longitud se calcula como suma de distancias euclidianas entre puntos
- El orden de Strahler se calcula recursivamente desde las terminales hasta la raiz

## Procedencia

Neuronas con metadatos en el manifest: 31 de 31

| Campo | Valores (n) |
|-------|-------------|
| especie | mouse (31) |
| cepa | C57BL/6J (31) |
| region | hippocampus/CA1/stratum pyramidale (31) |
| tipo_celular | principal cell/pyramidal (31) |
| edad | 12.0 Month (18), 6.0 Month (13) |
| condicion | Control (31) |

