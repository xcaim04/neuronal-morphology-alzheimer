# src/visualization/plots.py
import os
import matplotlib.pyplot as plt
import seaborn as sns

from config import COLORES, DPI, PLOT_STYLE

class PlotGenerator:
    """
    Generador de graficas para el analisis morfologico.
    """

    def __init__(self, output_dir):
        """
        Inicializa el generador de graficas.

        Args:
            output_dir: directorio donde guardar las graficas
        """
        self.output_dir = output_dir
        sns.set_style(PLOT_STYLE)

    def generar_todas(self, df):
        """Genera todas las graficas."""
        if df is None or df.empty:
            print("No hay datos para generar graficas.")
            return

        # Con un solo grupo las barras de medias tendrian una sola barra y no comparan nada
        if df["grupo"].nunique() > 1:
            self.grafica_barras_comparativa(df)
        self.grafica_dispersion_bifurcaciones_longitud(df)
        self.grafica_boxplot_strahler(df)

    def grafica_barras_comparativa(self, df):
        """Genera graficas de barras comparativas."""
        metricas = [
            ("longitud_total_um", "Longitud Total (um)", "Comparacion de Longitud Total"),
            ("bifurcaciones", "Numero de Bifurcaciones", "Comparacion de Bifurcaciones"),
            ("terminales", "Numero de Terminales", "Comparacion de Terminales"),
            ("strahler_max", "Orden de Strahler Maximo", "Comparacion de Strahler"),
        ]

        for col, ylabel, titulo in metricas:
            if col not in df.columns:
                continue

            plt.figure(figsize=(10, 6))

            promedio = df.groupby("grupo")[col].mean().reset_index()
            colores_barra = [COLORES.get(g, "gray") for g in promedio["grupo"]]

            barras = plt.bar(promedio["grupo"], promedio[col], color=colores_barra, alpha=0.7)
            plt.gca().bar_label(barras, fmt="%.1f", fontsize=12, fontweight="bold")
            plt.ylabel(ylabel)
            plt.title(titulo)

            plt.tight_layout()
            ruta_salida = os.path.join(self.output_dir, f"comparacion_{col}.png")
            plt.savefig(ruta_salida, dpi=DPI)
            plt.close()

    def grafica_dispersion_bifurcaciones_longitud(self, df):
        """Genera grafica de dispersion."""
        plt.figure(figsize=(12, 8))

        for grupo in df["grupo"].unique():
            subset = df[df["grupo"] == grupo]
            color = COLORES.get(grupo, "gray")
            plt.scatter(
                subset["bifurcaciones"],
                subset["longitud_total_um"],
                label=grupo.capitalize(),
                c=color,
                s=80,
                alpha=0.7
            )

        plt.xlabel("Numero de Bifurcaciones")
        plt.ylabel("Longitud Total (um)")
        plt.title("Relacion entre Bifurcaciones y Longitud Total")
        plt.legend()
        plt.tight_layout()

        ruta_salida = os.path.join(self.output_dir, "bifurcaciones_vs_longitud.png")
        plt.savefig(ruta_salida, dpi=DPI)
        plt.close()

    def grafica_boxplot_strahler(self, df):
        """Genera boxplot de Strahler."""
        # Se pasa ax para que pandas no abra una segunda figura que quedaria sin cerrar
        fig, ax = plt.subplots(figsize=(8, 6))

        df.boxplot(column="strahler_max", by="grupo", ax=ax)
        plt.ylabel("Orden de Strahler Maximo")
        plt.title("Distribucion del Orden de Strahler por Grupo")
        plt.suptitle("")
        plt.tight_layout()

        ruta_salida = os.path.join(self.output_dir, "strahler_boxplot.png")
        plt.savefig(ruta_salida, dpi=DPI)
        plt.close(fig)
