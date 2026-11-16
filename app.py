import os

import altair as alt
import pandas as pd
import streamlit as st

from config import BIOMARCADORES, RESULTADOS_COMPARATIVA, RESULTADOS_EVALUACION
from predecir import aviso_azar
from src.processing.storage import BiomarkerStore

st.set_page_config(page_title="Morfología neuronal", layout="wide")

# Par azul/naranja validado para daltonismo; verde/rojo (config.COLORES) no lo es.
# st.context.theme puede equivocarse en la primera carga de la sesión (issue #11920).
OSCURO = st.context.theme.type == "dark"
COLOR_GRUPO = alt.Scale(
    domain=["sana", "alzheimer"],
    range=["#3987e5", "#d95926"] if OSCURO else ["#2a78d6", "#eb6834"],
)

st.title("Morfología neuronal: sanas vs Alzheimer")
st.caption("Solo para investigación. No apto para diagnóstico clínico.")

filtro = st.sidebar.selectbox("Grupo", ["Todos", "sana", "alzheimer"])
datos = BiomarkerStore().dashboard(None if filtro == "Todos" else filtro)

if datos["run"] is None:
    st.warning(
        "La base de datos está vacía: ejecuta `uv run python main.py` y "
        "`uv run python train.py` para generar los resultados."
    )
else:
    st.write(f"Última ejecución: #{datos['run']['id']} · {datos['run']['created_at']}")

for grupo, resumen in datos["summaries"].items():
    st.subheader(grupo.capitalize())
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Neuronas", resumen["count"])
    c2.metric("Longitud media (µm)", f"{resumen['mean_length']:,.1f}")
    c3.metric("Bifurcaciones medias", f"{resumen['mean_branches']:.1f}")
    c4.metric("Terminales medios", f"{resumen['mean_terminals']:.1f}")

tab_bio, tab_comp, tab_modelo = st.tabs(["Biomarcadores", "Comparativa", "Modelo"])

with tab_bio:
    if not datos["records"]:
        st.info("No hay biomarcadores guardados.")
    else:
        df = pd.DataFrame(datos["records"]).drop(columns=["id", "run_id"])
        biomarcador = st.selectbox("Biomarcador", BIOMARCADORES)
        izq, der = st.columns(2)

        base = alt.Chart(df).encode(
            x=alt.X("grupo:N", title=None, sort=["sana", "alzheimer"], axis=alt.Axis(labelAngle=0)),
            y=alt.Y(f"{biomarcador}:Q", title=biomarcador),
            color=alt.Color("grupo:N", scale=COLOR_GRUPO, legend=None),
        )
        puntos = base.mark_circle(size=64, opacity=0.8).encode(
            # Dispersión horizontal centrada en un tercio de la banda para que los puntos queden sobre su caja.
            xOffset=alt.XOffset("jitter:Q", scale=alt.Scale(domain=[-1.5, 1.5])),
            tooltip=["archivo:N", "grupo:N", alt.Tooltip(f"{biomarcador}:Q", format=",.2f")],
        ).transform_calculate(jitter="random() - 0.5")
        izq.altair_chart(base.mark_boxplot(size=40, opacity=0.35) + puntos, width="stretch")

        dispersion = alt.Chart(df).mark_circle(size=72, opacity=0.85).encode(
            x=alt.X("longitud_total_um:Q", title="Longitud total (µm)"),
            y=alt.Y("bifurcaciones:Q", title="Bifurcaciones"),
            color=alt.Color("grupo:N", scale=COLOR_GRUPO, title="Grupo"),
            tooltip=["archivo:N", "grupo:N", alt.Tooltip("longitud_total_um:Q", format=",.1f"), "bifurcaciones:Q"],
        )
        der.altair_chart(dispersion, width="stretch")

        st.dataframe(df, hide_index=True)

with tab_comp:
    informe = os.path.join(RESULTADOS_COMPARATIVA, "informe_comparativo.md")
    if os.path.exists(informe):
        with open(informe, encoding="utf-8") as f:
            st.markdown(f.read())
    else:
        st.info("No hay informe comparativo: ejecuta `uv run python main.py`.")

with tab_modelo:
    if not datos["training_runs"]:
        st.info("No hay entrenamientos registrados: ejecuta `uv run python train.py`.")
    else:
        aviso = aviso_azar()
        if aviso:
            st.warning(aviso)
        ultimo = datos["training_runs"][0]
        st.caption(
            f"{ultimo['model_name']} · {ultimo['created_at']} · "
            f"{ultimo['healthy_count']} sanas, {ultimo['alzheimer_count']} Alzheimer"
        )
        cv, linea_base = ultimo["metrics"]["cv"], ultimo["metrics"]["linea_base"]
        for col, (nombre, valor) in zip(st.columns(len(cv)), cv.items()):
            delta = valor["mean"] - linea_base[nombre]["mean"] if nombre in linea_base else None
            # La std va en la etiqueta: en el valor se trunca con cinco columnas.
            col.metric(
                f"{nombre} (± {valor['std']:.3f})",
                f"{valor['mean']:.3f}",
                delta=None if delta is None else f"{delta:+.3f} vs línea base",
            )

        importancia = os.path.join(RESULTADOS_EVALUACION, "importancia_caracteristicas.csv")
        if os.path.exists(importancia):
            # Una sola serie: gris neutro para no confundirla con el color de un grupo.
            barras = alt.Chart(pd.read_csv(importancia)).mark_bar(
                color="#8a8a86", cornerRadiusEnd=4
            ).encode(
                x=alt.X("importancia:Q", title="Importancia"),
                y=alt.Y("caracteristica:N", title=None, sort="-x"),
                tooltip=["caracteristica:N", alt.Tooltip("importancia:Q", format=".3f")],
            )
            st.altair_chart(barras, width="stretch")

        izq, der = st.columns(2)
        for col, nombre in ((izq, "matriz_confusion_RandomForest.png"), (der, "curva_roc_RandomForest.png")):
            ruta = os.path.join(RESULTADOS_EVALUACION, nombre)
            if os.path.exists(ruta):
                col.image(ruta)
