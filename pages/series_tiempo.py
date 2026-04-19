import streamlit as st
import navigation
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

navigation.show()
layout="wide"

# ============================================================
# CONFIGURACIÓN GENERAL DE LA PÁGINA
# ============================================================

st.set_page_config(
    page_title="Series multivariadas",
    page_icon="📈",
    layout="wide"
)

st.title("Factores de riesgo y simulación de EaR")

st.write(
    """
    Caso de estudio de modelación de factores de riesgo mensuales para la generación
    de escenarios y su posterior uso en la estimación del Net Interest Income (NII)
    y del Earnings at Risk (EaR).

    En este proyecto se comparan distintas metodologías de series de tiempo bajo
    validación temporal fuera de muestra, con el fin de seleccionar un modelo capaz
    de representar adecuadamente la dinámica conjunta de los factores de riesgo y
    generar trayectorias futuras consistentes para análisis financiero.
    """
)

st.subheader("Objetivos del proyecto")

st.write(
    """
    Este proyecto tiene como objetivo modelar la dinámica conjunta de varios factores
    de riesgo mensuales con el fin de generar escenarios futuros consistentes para
    análisis de riesgo financiero.

    Desde la perspectiva de negocio, el problema consiste en evitar que la proyección
    de variables relevantes para el balance se haga de forma arbitraria o con supuestos
    poco defendibles. En su lugar, se busca construir una metodología cuantitativa que
    permita representar la evolución probable de los factores de riesgo y trasladar esa
    incertidumbre al comportamiento futuro del Net Interest Income (NII) y del
    Earnings at Risk (EaR).

    En particular, los objetivos específicos fueron:

    - Comparar distintas metodologías de predicción y simulación de series de tiempo;
    - Evaluar su desempeño mediante validación temporal fuera de muestra;
    - Seleccionar el modelo más adecuado para representar la dependencia conjunta de los factores;
    - Generar trayectorias futuras a 12 meses que puedan utilizarse como insumo
      en ejercicios de simulación financiera y medición de riesgo.
    """
)

st.subheader("Descripción de los datos")

st.write(
    """
    El análisis se realizó con una base de **148 observaciones mensuales** de seis factores
    de riesgo relevantes para la dinámica de tasas y su posterior uso en ejercicios de
    simulación financiera.

    Los factores considerados fueron:

    - **DTF**
    - **IBR**
    - **IPC**
    - **Cuvr**
    - **Auvr**
    - **TA_Jur**

    Estas series se utilizaron como variables de entrada para comparar distintas metodologías
    de modelación de series de tiempo. Dado que algunos factores en niveles presentaban señales
    de no estacionariedad o resultados mixtos en las pruebas estadísticas, la modelación se
    realizó sobre **primeras diferencias**, con el fin de capturar la dinámica mensual de los
    cambios en cada factor y trabajar en un marco más adecuado para modelos multivariados como VAR.

    A partir de esta base histórica se construyó un esquema de validación temporal rolling
    expansiva, y posteriormente se estimó el modelo final con toda la muestra disponible para
    generar escenarios futuros a 12 meses.
    """
)

RUTA_FACTORES = Path("data/Factores de Riesgo.xlsx")
FACTOR_COLS = ["DTF", "IBR", "IPC", "Cuvr", "Auvr", "TA_Jur"]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def convertir_fecha_excel(serie):
    """
    Convierte una serie de fechas que puede venir como:
    - datetime
    - string
    - serial de Excel
    """
    s = serie.copy()

    if pd.api.types.is_datetime64_any_dtype(s):
        return pd.to_datetime(s, errors="coerce")

    s_num = pd.to_numeric(s, errors="coerce")

    if s_num.notna().sum() > 0:
        return pd.to_datetime(s_num, unit="D", origin="1899-12-30", errors="coerce")

    return pd.to_datetime(s, errors="coerce")


@st.cache_data
def cargar_factores_riesgo(ruta_archivo):
    if not os.path.exists(ruta_archivo):
        raise FileNotFoundError(f"No se encontró el archivo: {ruta_archivo}")

    df = pd.read_excel(ruta_archivo)

    # eliminar columnas tipo Unnamed
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")]

    # detectar columna fecha
    fecha_col = None
    for c in df.columns:
        if str(c).strip().lower() == "fecha":
            fecha_col = c
            break

    if fecha_col is not None:
        df[fecha_col] = convertir_fecha_excel(df[fecha_col])
        df = df.sort_values(fecha_col).reset_index(drop=True)
    else:
        df.insert(0, "Fecha", pd.RangeIndex(start=1, stop=len(df) + 1))
        fecha_col = "Fecha"

    # forzar factores a numérico
    for col in FACTOR_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[[fecha_col] + FACTOR_COLS].dropna().reset_index(drop=True)
    df = df.rename(columns={fecha_col: "Fecha"})

    return df


# =========================================================
# CARGA DE DATOS
# =========================================================
try:
    factores_df = cargar_factores_riesgo(str(RUTA_FACTORES))
except Exception as e:
    st.error(f"Error cargando los datos: {e}")
    st.stop()


# =========================================================
# SECCIÓN STREAMLIT
# =========================================================
st.subheader("Visualización de los factores de riesgo")

st.write(
    """
    A continuación se presentan las seis series históricas utilizadas en el análisis:
    DTF, IBR, IPC, Cuvr, Auvr y TA_Jur.
    """
)

col1, col2, col3 = st.columns(3)
col1.metric("Número de observaciones", len(factores_df))
col2.metric("Número de factores", len(FACTOR_COLS))
col3.metric("Frecuencia", "Mensual")

tab1, tab2, tab3 = st.tabs(["Vista individual", "Vista completa", "Datos"])

# =========================================================
# TAB 1: VISTA INDIVIDUAL
# =========================================================
with tab1:
    factor_seleccionado = st.selectbox(
        "Seleccione un factor",
        FACTOR_COLS,
        index=0
    )

    fig_individual = px.line(
        factores_df,
        x="Fecha",
        y=factor_seleccionado,
        title=f"Serie histórica de {factor_seleccionado}",
        markers=False
    )

    fig_individual.update_layout(
        xaxis_title="Fecha",
        yaxis_title=factor_seleccionado,
        height=500
    )

    st.plotly_chart(fig_individual, use_container_width=True)


# =========================================================
# TAB 2: VISTA COMPLETA (6 GRÁFICAS)
# =========================================================
with tab2:
    fig_subplots = make_subplots(
        rows=2,
        cols=3,
        subplot_titles=FACTOR_COLS,
        shared_xaxes=False
    )

    posiciones = {
        "DTF": (1, 1),
        "IBR": (1, 2),
        "IPC": (1, 3),
        "Cuvr": (2, 1),
        "Auvr": (2, 2),
        "TA_Jur": (2, 3),
    }

    for factor in FACTOR_COLS:
        fila, col = posiciones[factor]

        fig_subplots.add_trace(
            go.Scatter(
                x=factores_df["Fecha"],
                y=factores_df[factor],
                mode="lines",
                name=factor,
                showlegend=False
            ),
            row=fila,
            col=col
        )

    fig_subplots.update_layout(
        title="Factores de riesgo - vista completa",
        height=700
    )

    st.plotly_chart(fig_subplots, use_container_width=True)


# =========================================================
# TAB 3: DATOS
# =========================================================
with tab3:
    st.dataframe(factores_df, use_container_width=True)

