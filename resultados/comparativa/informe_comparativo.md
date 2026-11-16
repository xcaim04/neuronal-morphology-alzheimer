# Informe Comparativo: Sanas vs Alzheimer

**Fecha del informe:** 2026-11-15 20:27:58

## Resumen General

| Indicador | Sanas | Alzheimer |
|-----------|-------|-----------|
| Total de neuronas | 31 | 31 |

## Comparacion de Metricas

Test de Mann-Whitney U bilateral por metrica. P-valores ajustados por Holm-Bonferroni sobre las 7 metricas (alfa = 0.05). Tamano de efecto: delta de Cliff (rank-biserial), positivo si Alzheimer tiende a valores mayores; |delta| >= 0.147 pequeno, >= 0.33 mediano, >= 0.474 grande. Diferencia (%) = (alzheimer - sana) / sana.

| Metrica | Sana (media ± std) | Alzheimer (media ± std) | Diferencia (%) | U | p | p (Holm) | Delta de Cliff |
|---------|-------------------|------------------------|----------------|---|---|----------|----------------|
| puntos_totales | 13398.29 ± 5155.23 | 14534.48 ± 4913.18 | +8.5% | 538.0 | 0.4223 | 1.0000 | +0.12 |
| secciones | 112.61 ± 27.05 | 113.16 ± 35.43 | +0.5% | 513.0 | 0.6523 | 1.0000 | +0.07 |
| longitud_total_um | 6345.98 ± 1651.98 | 6869.00 ± 1977.02 | +8.2% | 570.0 | 0.2102 | 1.0000 | +0.19 |
| bifurcaciones | 53.52 ± 13.60 | 54.06 ± 17.51 | +1.0% | 519.5 | 0.5876 | 1.0000 | +0.08 |
| terminales | 59.10 ± 13.48 | 59.10 ± 17.94 | +0.0% | 509.5 | 0.6880 | 1.0000 | +0.06 |
| strahler_max | 3.61 ± 0.50 | 3.77 ± 0.43 | +4.5% | 558.0 | 0.1746 | 1.0000 | +0.16 |
| ratio_bifurcacion_terminal | 0.90 ± 0.03 | 0.90 ± 0.05 | +0.4% | 542.0 | 0.3904 | 1.0000 | +0.13 |

## Interpretacion

Ninguna metrica difiere significativamente entre grupos tras la correccion de Holm (alfa = 0.05).

### Limitaciones

- Muestras pequenas (sanas n=31, alzheimer n=31): potencia estadistica limitada; la ausencia de significacion no implica ausencia de efecto.
- Segun el manifest, los grupos coinciden en especie, region, tipo_celular, edad.
