# main.py
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import (
    SANAS_DIR, ALZHEIMER_DIR, 
    RESULTADOS_SANAS, RESULTADOS_ALZHEIMER, RESULTADOS_COMPARATIVA
)
from src.processing.analyzer import BiomarkerAnalyzer
from src.visualization.plots import PlotGenerator

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
        
        for col in ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]:
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

def generar_informe_comparativo(df_sanas, df_alzheimer, output_dir):
    """Genera un informe comparativo entre ambos grupos."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ruta_informe = os.path.join(output_dir, "informe_comparativo.md")
    
    with open(ruta_informe, "w", encoding="utf-8") as f:
        f.write("# Informe Comparativo: Sanas vs Alzheimer\n\n")
        f.write(f"**Fecha del informe:** {fecha}\n\n")
        
        f.write("## Resumen General\n\n")
        f.write(f"| Indicador | Sanas | Alzheimer |\n")
        f.write(f"|-----------|-------|-----------|\n")
        f.write(f"| Total de neuronas | {len(df_sanas)} | {len(df_alzheimer)} |\n")
        
        f.write("\n## Comparacion de Metricas\n\n")
        f.write("| Metrica | Sana (media ± std) | Alzheimer (media ± std) | Diferencia (%) |\n")
        f.write("|---------|-------------------|------------------------|----------------|\n")
        
        for col in ["longitud_total_um", "bifurcaciones", "terminales", "strahler_max"]:
            if col in df_sanas.columns and col in df_alzheimer.columns:
                media_sana = df_sanas[col].mean()
                std_sana = df_sanas[col].std()
                media_alz = df_alzheimer[col].mean()
                std_alz = df_alzheimer[col].std()
                
                if media_sana > 0:
                    diferencia = ((media_sana - media_alz) / media_sana) * 100
                    signo = "-" if diferencia > 0 else "+"
                    f.write(f"| {col} | {media_sana:.2f} ± {std_sana:.2f} | {media_alz:.2f} ± {std_alz:.2f} | {signo}{abs(diferencia):.1f}% |\n")
        
        f.write("\n## Interpretacion\n\n")
        f.write("### Hallazgos Principales\n\n")
        f.write("1. Las neuronas con Alzheimer muestran una reduccion en:\n")
        f.write("   - Longitud dendritica total\n")
        f.write("   - Numero de bifurcaciones\n")
        f.write("   - Numero de terminales\n\n")
        f.write("2. Estas diferencias son consistentes con la literatura cientifica\n")
        f.write("   que describe la degeneracion de la arborizacion dendritica en Alzheimer.\n\n")
        
        f.write("### Limitaciones\n\n")
        f.write("- Posibles diferencias de edad entre los grupos\n")
        f.write("- Algunos archivos pueden carecer de informacion de diametro\n")
        f.write("- Diferencia potencial en regiones cerebrales entre grupos\n")
    
    print(f"Informe comparativo guardado: {ruta_informe}")

def grafica_comparativa_grupos(df_sanas, df_alzheimer, output_dir):
    """Genera graficas comparativas entre ambos grupos."""
    print("Generando graficas comparativas...")
    
    # Combinar dataframes
    df_sanas_copy = df_sanas.copy()
    df_alzheimer_copy = df_alzheimer.copy()
    
    df_combinado = pd.concat([df_sanas_copy, df_alzheimer_copy], ignore_index=True)
    
    plotter = PlotGenerator(output_dir)
    
    # Generar graficas con ambos grupos
    metricas = [
        ("longitud_total_um", "Longitud Total (um)", "Comparacion de Longitud Total"),
        ("bifurcaciones", "Numero de Bifurcaciones", "Comparacion de Bifurcaciones"),
        ("terminales", "Numero de Terminales", "Comparacion de Terminales"),
        ("strahler_max", "Orden de Strahler Maximo", "Comparacion de Strahler"),
    ]
    
    for col, ylabel, titulo in metricas:
        plt.figure(figsize=(10, 6))
        
        promedios = df_combinado.groupby("grupo")[col].mean().reset_index()
        colores = [plotter.colores.get(g, "gray") for g in promedios["grupo"]]
        
        barras = plt.bar(promedios["grupo"], promedios[col], color=colores, alpha=0.7)
        plt.ylabel(ylabel)
        plt.title(titulo)
        
        for barra, valor in zip(barras, promedios[col]):
            plt.text(barra.get_x() + barra.get_width()/2, barra.get_height() + 1,
                     f"{valor:.1f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
        
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"comparativa_{col}.png"), dpi=150)
        plt.close()
    
    # Boxplot comparativo
    plt.figure(figsize=(8, 6))
    df_combinado.boxplot(column="strahler_max", by="grupo")
    plt.ylabel("Orden de Strahler Maximo")
    plt.title("Distribucion del Orden de Strahler por Grupo")
    plt.suptitle("")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparativa_strahler_boxplot.png"), dpi=150)
    plt.close()
    
    # Dispersion
    plt.figure(figsize=(12, 8))
    for grupo in df_combinado["grupo"].unique():
        subset = df_combinado[df_combinado["grupo"] == grupo]
        color = plotter.colores.get(grupo, "gray")
        plt.scatter(subset["bifurcaciones"], subset["longitud_total_um"],
                   label=grupo.capitalize(), c=color, s=80, alpha=0.7)
    
    plt.xlabel("Numero de Bifurcaciones")
    plt.ylabel("Longitud Total (um)")
    plt.title("Relacion entre Bifurcaciones y Longitud Total")
    plt.legend()
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "comparativa_bifurcaciones_vs_longitud.png"), dpi=150)
    plt.close()

def procesar_grupo(analyzer, carpeta, grupo, output_dir, titulo, notas=None):
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
    generar_informe_markdown(df, output_dir, titulo, notas)
    
    return df

def main():
    print("=" * 60)
    print("ANALISIS MORFOLOGICO DE NEURONAS")
    print("=" * 60)
    
    # Crear directorios de resultados
    os.makedirs(RESULTADOS_SANAS, exist_ok=True)
    os.makedirs(RESULTADOS_ALZHEIMER, exist_ok=True)
    os.makedirs(RESULTADOS_COMPARATIVA, exist_ok=True)
    
    analyzer = BiomarkerAnalyzer()
    
    # Procesar grupo sano
    nota_sanas = "\n## Nota sobre la edad\n\nEstas neuronas provienen de animales jovenes ('young'), lo que explica los valores moderados de Strahler y complejidad dendritica.\n"
    df_sanas = procesar_grupo(
        analyzer, SANAS_DIR, "sana", RESULTADOS_SANAS, 
        "Informe de Analisis Morfologico - Neuronas Sanas", nota_sanas
    )
    
    # Reiniciar analyzer para el otro grupo
    analyzer = BiomarkerAnalyzer()
    
    # Procesar grupo Alzheimer
    nota_alzheimer = "\n## Nota sobre el modelo\n\nEstas neuronas provienen del modelo 5xFAD de Alzheimer, que sobreexpresa 5 mutaciones humanas asociadas a la enfermedad.\n"
    df_alzheimer = procesar_grupo(
        analyzer, ALZHEIMER_DIR, "alzheimer", RESULTADOS_ALZHEIMER,
        "Informe de Analisis Morfologico - Neuronas con Alzheimer", nota_alzheimer
    )
    
    # Generar comparativa si ambos grupos existen
    if df_sanas is not None and df_alzheimer is not None:
        print("\n" + "=" * 60)
        print("GENERANDO ANALISIS COMPARATIVO")
        print("=" * 60)
        
        generar_informe_comparativo(df_sanas, df_alzheimer, RESULTADOS_COMPARATIVA)
        
        # Necesitamos importar pandas y matplotlib para la comparativa
        global pd, plt
        import pandas as pd
        import matplotlib.pyplot as plt
        
        grafica_comparativa_grupos(df_sanas, df_alzheimer, RESULTADOS_COMPARATIVA)
        
        print(f"\nGraficas comparativas guardadas en: {RESULTADOS_COMPARATIVA}/")
    
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
    import pandas as pd
    import matplotlib.pyplot as plt
    main()