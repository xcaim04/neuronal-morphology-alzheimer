# main.py
import os
from datetime import datetime

import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu

from config import (
    SANAS_DIR, ALZHEIMER_DIR, MANIFEST_PATH, BIOMARCADORES,
    RESULTADOS_SANAS, RESULTADOS_ALZHEIMER, RESULTADOS_COMPARATIVA
)
from src.processing.analyzer import BiomarkerAnalyzer
from src.processing.storage import BiomarkerStore
from src.visualization.plots import PlotGenerator

COLUMNAS_PROCEDENCIA = ["especie", "cepa", "region", "tipo_celular", "edad", "condicion"]
ALFA = 0.05


def cargar_manifest():
    """Lee el manifest de procedencia; None si no existe."""
    if not os.path.exists(MANIFEST_PATH):
        print(f"Aviso: no existe {MANIFEST_PATH}, los informes no tendran procedencia.")
        return None
    return pd.read_csv(MANIFEST_PATH, dtype=str).fillna("desconocido")


def procedencia_de(df, manifest):
    """Filas del manifest correspondientes a los archivos de df."""
    if manifest is None:
        return None
    return manifest[manifest["archivo"].map(os.path.basename).isin(df["archivo"])]


def seccion_procedencia(df, manifest):
    """Markdown con la procedencia de las neuronas de df segun el manifest."""
    meta = procedencia_de(df, manifest)
    if meta is None:
        return "## Procedencia\n\nNo hay metadatos de procedencia (no existe el manifest del dataset).\n"
    lineas = ["## Procedencia\n", f"Neuronas con metadatos en el manifest: {len(meta)} de {len(df)}\n"]
    lineas += ["| Campo | Valores (n) |", "|-------|-------------|"]
    for col in COLUMNAS_PROCEDENCIA:
        conteos = ", ".join(f"{valor} ({n})" for valor, n in meta[col].value_counts().items())
        lineas.append(f"| {col} | {conteos or '-'} |")
    return "\n".join(lineas) + "\n"


def generar_informe_markdown(df, output_dir, titulo, notas_adicionales=None):
    """Genera un informe en formato markdown."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ruta_informe = os.path.join(output_dir, "informe.md")

    grupo = df["grupo"].iloc[0] if not df.empty else "desconocido"

    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write(f"# {titulo}\n\n")
        f.write(f"**Fecha del informe:** {fecha}\n\n")
        f.write(f"**Grupo:** {grupo.capitalize()}\n\n")

        f.write("## Resumen General\n\n")
        f.write(f"| Indicador | Valor |\n")
        f.write(f"|-----------|-------|\n")
        f.write(f"| Total de neuronas analizadas | {len(df)} |\n")

        f.write("\n## Estadisticas del Grupo\n\n")
        f.write("| Metrica | Media | Desv. Std | Min | Max |\n")
        f.write("|---------|-------|-----------|-----|-----|\n")

        for col in BIOMARCADORES:
            if col in df.columns:
                stats = df[col].describe()
                f.write(f"| {col} | {stats['mean']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['max']:.2f} |\n")

        f.write("\n## Distribucion de Strahler\n\n")
        strahler_counts = df["strahler_max"].value_counts().sort_index()
        f.write("| Orden de Strahler | Cantidad | Porcentaje |\n")
        f.write("|-------------------|----------|------------|\n")
        for orden, count in strahler_counts.items():
            porcentaje = (count / len(df)) * 100
            f.write(f"| {orden} | {count} | {porcentaje:.1f}% |\n")

        f.write("\n## Archivos Procesados\n\n")
        f.write("| Archivo | Longitud (um) | Bifurcaciones | Terminales | Strahler |\n")
        f.write("|---------|---------------|---------------|------------|----------|\n")

        for _, row in df.iterrows():
            f.write(f"| {row['archivo']} | {row['longitud_total_um']} | {row['bifurcaciones']} | {row['terminales']} | {row['strahler_max']} |\n")

        f.write("\n## Notas\n\n")
        f.write("- Los datos fueron extraidos de archivos SWC usando morphio\n")
        f.write("- La longitud se calcula como suma de distancias euclidianas entre puntos\n")
        f.write("- El orden de Strahler se calcula recursivamente desde las terminales hasta la raiz\n")

        if notas_adicionales:
            f.write(f"\n{notas_adicionales}\n")

    print(f"Informe guardado: {ruta_informe}")
    return ruta_informe


def holm(pvalores):
    """P-valores ajustados por Holm-Bonferroni."""
    p = np.asarray(pvalores, dtype=float)
    m = len(p)
    orden = np.argsort(p)
    ajustados = np.empty(m)
    ajustados[orden] = np.minimum(1.0, np.maximum.accumulate((m - np.arange(m)) * p[orden]))
    return ajustados


def contrastes(df_sanas, df_alzheimer):
    """Mann-Whitney U bilateral por metrica, con Holm y delta de Cliff (alzheimer vs sana)."""
    filas = []
    for col in BIOMARCADORES:
        sana, alz = df_sanas[col], df_alzheimer[col]
        u, p = mannwhitneyu(alz, sana, alternative="two-sided")
        media_sana, media_alz = sana.mean(), alz.mean()
        filas.append({
            "metrica": col,
            "media_sana": media_sana, "std_sana": sana.std(),
            "media_alz": media_alz, "std_alz": alz.std(),
            "dif_pct": (media_alz - media_sana) / media_sana * 100 if media_sana else np.nan,
            "u": u,
            # scipy da p=nan si todos los valores son identicos: no hay diferencia
            "p": 1.0 if np.isnan(p) else p,
            # delta de Cliff = P(alz > sana) - P(alz < sana) = 2U/(n1*n2) - 1
            "delta": 2 * u / (len(alz) * len(sana)) - 1,
        })
    resultados = pd.DataFrame(filas)
    resultados["p_holm"] = holm(resultados["p"])
    return resultados


def limitaciones(df_sanas, df_alzheimer, manifest):
    """Lista de limitaciones derivadas de los tamanos y la composicion de los grupos."""
    items = [f"- Muestras pequenas (sanas n={len(df_sanas)}, alzheimer n={len(df_alzheimer)}): "
             "potencia estadistica limitada; la ausencia de significacion no implica ausencia de efecto."]
    meta_sana, meta_alz = procedencia_de(df_sanas, manifest), procedencia_de(df_alzheimer, manifest)
    if manifest is None:
        items.append("- No hay metadatos de procedencia (no existe el manifest del dataset): "
                     "no se puede comprobar si los grupos son comparables en especie, region, edad, etc.")
        return items
    for nombre, df, meta in (("sanas", df_sanas, meta_sana), ("alzheimer", df_alzheimer, meta_alz)):
        if len(meta) < len(df):
            items.append(f"- {len(df) - len(meta)} neuronas del grupo {nombre} no aparecen en el manifest.")
    # condicion es la variable que se compara, no un factor de confusion
    # cepa codifica el propio genotipo comparado (control vs transgenico), igual que condicion
    confusores = [col for col in COLUMNAS_PROCEDENCIA if col not in ("condicion", "cepa")]
    distintas = [col for col in confusores if set(meta_sana[col]) != set(meta_alz[col])]
    for col in distintas:
        items.append(f"- Los grupos difieren en {col} (sanas: {', '.join(sorted(set(meta_sana[col]))) or '-'}; "
                     f"alzheimer: {', '.join(sorted(set(meta_alz[col]))) or '-'}): las diferencias morfologicas "
                     f"pueden deberse a {col} y no a la enfermedad.")
    if not distintas:
        items.append("- Segun el manifest, los grupos coinciden en " + ", ".join(confusores) + ".")
    return items


def generar_informe_comparativo(df_sanas, df_alzheimer, output_dir, manifest):
    """Genera un informe comparativo entre ambos grupos."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ruta_informe = os.path.join(output_dir, "informe_comparativo.md")
    res = contrastes(df_sanas, df_alzheimer)

    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write("# Informe Comparativo: Sanas vs Alzheimer\n\n")
        f.write(f"**Fecha del informe:** {fecha}\n\n")

        f.write("## Resumen General\n\n")
        f.write(f"| Indicador | Sanas | Alzheimer |\n")
        f.write(f"|-----------|-------|-----------|\n")
        f.write(f"| Total de neuronas | {len(df_sanas)} | {len(df_alzheimer)} |\n")

        f.write("\n## Comparacion de Metricas\n\n")
        f.write("Test de Mann-Whitney U bilateral por metrica. P-valores ajustados por Holm-Bonferroni "
                f"sobre las {len(res)} metricas (alfa = {ALFA}). Tamano de efecto: delta de Cliff "
                "(rank-biserial), positivo si Alzheimer tiende a valores mayores; |delta| >= 0.147 pequeno, "
                ">= 0.33 mediano, >= 0.474 grande. Diferencia (%) = (alzheimer - sana) / sana.\n\n")
        f.write("| Metrica | Sana (media ± std) | Alzheimer (media ± std) | Diferencia (%) | U | p | p (Holm) | Delta de Cliff |\n")
        f.write("|---------|-------------------|------------------------|----------------|---|---|----------|----------------|\n")
        for r in res.itertuples():
            f.write(f"| {r.metrica} | {r.media_sana:.2f} ± {r.std_sana:.2f} | {r.media_alz:.2f} ± {r.std_alz:.2f} | "
                    f"{r.dif_pct:+.1f}% | {r.u:.1f} | {r.p:.4f} | {r.p_holm:.4f} | {r.delta:+.2f} |\n")

        f.write("\n## Interpretacion\n\n")
        significativas = res[res["p_holm"] < ALFA]
        if significativas.empty:
            f.write(f"Ninguna metrica difiere significativamente entre grupos tras la correccion de Holm (alfa = {ALFA}).\n")
        else:
            f.write(f"Metricas con diferencia significativa tras la correccion de Holm (alfa = {ALFA}):\n\n")
            for r in significativas.itertuples():
                direccion = "mayor" if r.delta > 0 else "menor"
                f.write(f"- {r.metrica}: {direccion} en Alzheimer (diferencia de medias {r.dif_pct:+.1f}%, "
                        f"delta de Cliff {r.delta:+.2f}, p ajustado {r.p_holm:.4f})\n")
        no_significativas = res[res["p_holm"] >= ALFA]["metrica"]
        if not no_significativas.empty and not significativas.empty:
            f.write(f"\nSin diferencia significativa: {', '.join(no_significativas)}.\n")

        f.write("\n### Limitaciones\n\n")
        f.write("\n".join(limitaciones(df_sanas, df_alzheimer, manifest)) + "\n")

    print(f"Informe comparativo guardado: {ruta_informe}")


def procesar_grupo(analyzer, carpeta, grupo, output_dir, titulo, manifest):
    """Procesa un grupo completo de neuronas."""
    print(f"\nProcesando neuronas {grupo} desde: {carpeta}")

    if not os.path.exists(carpeta):
        print(f"  Carpeta no encontrada: {carpeta}")
        return None

    os.makedirs(output_dir, exist_ok=True)

    procesadas = analyzer.procesar_carpeta(carpeta, grupo)
    print(f"  Procesadas {procesadas} neuronas {grupo}")

    if procesadas == 0:
        print(f"  No se encontraron neuronas {grupo} para procesar.")
        return None

    df = analyzer.generar_dataframe()
    analyzer.guardar_csv(os.path.join(output_dir, "dataset_biomarcadores.csv"))

    print(f"  Generando graficas para {grupo}...")
    plotter = PlotGenerator(output_dir)
    plotter.generar_todas(df)

    print(f"  Generando informe para {grupo}...")
    generar_informe_markdown(df, output_dir, titulo, seccion_procedencia(df, manifest))

    return df


def main():
    print("=" * 60)
    print("ANALISIS MORFOLOGICO DE NEURONAS")
    print("=" * 60)

    # Crear directorios de resultados
    os.makedirs(RESULTADOS_SANAS, exist_ok=True)
    os.makedirs(RESULTADOS_ALZHEIMER, exist_ok=True)
    os.makedirs(RESULTADOS_COMPARATIVA, exist_ok=True)

    manifest = cargar_manifest()

    df_sanas = procesar_grupo(
        BiomarkerAnalyzer(), SANAS_DIR, "sana", RESULTADOS_SANAS,
        "Informe de Analisis Morfologico - Neuronas Sanas", manifest
    )
    df_alzheimer = procesar_grupo(
        BiomarkerAnalyzer(), ALZHEIMER_DIR, "alzheimer", RESULTADOS_ALZHEIMER,
        "Informe de Analisis Morfologico - Neuronas con Alzheimer", manifest
    )

    # Generar comparativa si ambos grupos existen
    if df_sanas is not None and df_alzheimer is not None:
        print("\n" + "=" * 60)
        print("GENERANDO ANALISIS COMPARATIVO")
        print("=" * 60)

        generar_informe_comparativo(df_sanas, df_alzheimer, RESULTADOS_COMPARATIVA, manifest)
        PlotGenerator(RESULTADOS_COMPARATIVA).generar_todas(pd.concat([df_sanas, df_alzheimer], ignore_index=True))

        print(f"\nGraficas comparativas guardadas en: {RESULTADOS_COMPARATIVA}/")

    grupos = [df for df in (df_sanas, df_alzheimer) if df is not None]
    if grupos:
        # to_dict("records") devuelve tipos nativos de Python, que sqlite3 acepta
        run_id = BiomarkerStore().save_biomarkers(pd.concat(grupos).to_dict("records"), source="dataset")
        print(f"\nBiomarcadores guardados en la base de datos (ejecucion {run_id})")

    print("\n" + "=" * 60)
    print("PROCESO COMPLETADO")
    print("=" * 60)
    print(f"\nResultados guardados en:")
    print(f"  - Sanas: {RESULTADOS_SANAS}/")
    if df_alzheimer is not None:
        print(f"  - Alzheimer: {RESULTADOS_ALZHEIMER}/")
    if df_sanas is not None and df_alzheimer is not None:
        print(f"  - Comparativa: {RESULTADOS_COMPARATIVA}/")


if __name__ == "__main__":
    main()
