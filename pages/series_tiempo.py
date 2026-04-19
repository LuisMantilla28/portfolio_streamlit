import streamlit as st
import navigation
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import os
from plotly.subplots import make_subplots
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


st.subheader("Metodología")

st.write(
    """
    El objetivo metodológico de este proyecto fue modelar la dinámica conjunta de
    varios factores de riesgo mensuales para generar trayectorias futuras consistentes
    y utilizarlas posteriormente en ejercicios de simulación financiera orientados
    al **Net Interest Income (NII)** y al **Earnings at Risk (EaR)**.
    """
)

with st.expander("1. Variables consideradas", expanded=True):
    st.write(
        """
        Se trabajó con seis factores de riesgo observados mensualmente:
        **DTF, IBR, IPC, Cuvr, Auvr y TA_Jur**.
        """
    )

    st.latex(r"""
    X_t=
    \begin{pmatrix}
    \text{DTF}_t\\
    \text{IBR}_t\\
    \text{IPC}_t\\
    \text{Cuvr}_t\\
    \text{Auvr}_t\\
    \text{TA\_Jur}_t
    \end{pmatrix},
    \qquad t=1,\dots,T
    """)

with st.expander("2. Transformación de las series"):
    st.write(
        """
        La modelación se realizó sobre **primeras diferencias**, con el fin de
        trabajar con una representación más adecuada para modelos dinámicos multivariados.
        """
    )

    st.latex(r"""
    \Delta X_t = X_t - X_{t-1}
    """)

    st.write(
        """
        Esta transformación permite estudiar los cambios mensuales de cada factor
        en lugar de trabajar directamente sobre sus niveles.
        """
    )

with st.expander("3. Modelos considerados"):
    st.write("Se plantearon tres enfoques de modelación:")

    st.markdown(
        """
        - **Benchmark ingenuo**
        - **Modelo normal multivariado**
        - **Modelo VAR**
        """
    )

    st.write("**Benchmark ingenuo**")
    st.latex(r"""
    \hat X_{t+1}=X_t
    """)

    st.write("En diferencias:")
    st.latex(r"""
    \widehat{\Delta X}_{t+1}=0
    """)

    st.write("**Modelo normal multivariado**")
    st.latex(r"""
    \Delta X_t \sim \mathcal{N}_k(\mu,\Sigma)
    """)

    st.write("Pronóstico puntual a un paso:")
    st.latex(r"""
    \widehat{\Delta X}_{t+1}=\hat\mu
    """)

    st.write("Reconstrucción en niveles:")
    st.latex(r"""
    \hat X_{t+1}=X_t+\hat\mu
    """)

    st.write("**Modelo VAR**")
    st.latex(r"""
    \Delta X_t = c + A_1 \Delta X_{t-1} + \cdots + A_p \Delta X_{t-p} + u_t
    """)

    st.write(
        """
        Este enfoque permite capturar tanto dependencia temporal como interacción
        dinámica entre los factores.
        """
    )

with st.expander("4. Validación temporal"):
    st.write(
        """
        Para comparar los modelos se utilizó una estrategia de **validación rolling expansiva**,
        respetando el orden temporal de la muestra.
        """
    )

    st.latex(r"""
    \text{Train}_s = \{1,2,\dots,m+s-1\}
    """)

    st.latex(r"""
    \text{Test}_s = \{m+s\}
    """)

    st.write(
        """
        En cada iteración se estimó el modelo con la información disponible hasta ese momento,
        se generó una predicción **one-step-ahead** y se comparó con la observación siguiente.
        """
    )

with st.expander("5. Métricas de evaluación"):
    st.write(
        """
        El desempeño predictivo fuera de muestra se evaluó mediante dos métricas:
        """
    )

    st.write("**RMSE**")
    st.latex(r"""
    RMSE=\sqrt{\frac{1}{n}\sum_{t=1}^{n}(X_t-\hat X_t)^2}
    """)

    st.write("**MAE**")
    st.latex(r"""
    MAE=\frac{1}{n}\sum_{t=1}^{n}|X_t-\hat X_t|
    """)

with st.expander("6. Estimación final del modelo dinámico"):
    st.write(
        """
        Una vez completada la fase de comparación, el modelo dinámico final se
        reestimó con toda la muestra disponible.
        """
    )

    st.write(
        """
        El orden autorregresivo se seleccionó mediante criterios de información,
        buscando un balance entre ajuste y parsimonia.
        """
    )

with st.expander("7. Validación de supuestos del modelo"):
    st.write(
        """
        Sobre el modelo final se revisaron los siguientes aspectos metodológicos:
        """
    )

    st.markdown(
        """
        - **Estacionariedad** de las series transformadas  
        - **Estabilidad** del sistema dinámico  
        - **Autocorrelación residual**  
        - **Normalidad residual**  
        - **Heterocedasticidad condicional**
        """
    )

    st.write(
        """
        Estas verificaciones permiten evaluar si la estructura dinámica estimada
        es consistente y si la incertidumbre residual puede utilizarse de manera
        adecuada en la simulación de escenarios.
        """
    )

with st.expander("8. Esquema de simulación"):
    st.write(
        """
        La simulación de escenarios se construyó a partir del modelo dinámico estimado
        y de sus residuos.
        """
    )

    st.latex(r"""
    \Delta X_t = c + A_1 \Delta X_{t-1} + \cdots + A_p \Delta X_{t-p} + u_t
    """)

    st.write("Residuos estimados:")
    st.latex(r"""
    \hat u_t = \Delta X_t - \widehat{\Delta X}_t
    """)

    st.write(
        """
        La actualización en niveles se obtiene a partir de los cambios simulados:
        """
    )

    st.latex(r"""
    X_{t+1}=X_t+\Delta X_{t+1}
    """)

with st.expander("9. Bootstrap de residuos vectoriales"):
    st.write(
        """
        Para representar la incertidumbre del sistema se utilizó un esquema de
        **bootstrap de residuos vectoriales**, remuestreando residuos históricos
        completos del modelo dinámico.
        """
    )

    st.write(
        """
        Este enfoque preserva la dependencia contemporánea entre factores dentro
        del término residual.
        """
    )

    st.latex(r"""
    \Delta X_{T+1}^{(s)}=
    \hat c+\hat A_1 \Delta X_T+\cdots+\hat A_p \Delta X_{T-p+1}+\hat u_{T+1}^{(s)}
    """)

    st.latex(r"""
    X_{T+1}^{(s)}=X_T+\Delta X_{T+1}^{(s)}
    """)

with st.expander("10. Construcción de escenarios"):
    st.write(
        """
        El horizonte de simulación se definió en **12 meses**, y el procedimiento
        se repitió múltiples veces para generar una colección de trayectorias futuras.
        """
    )

    st.latex(r"""
    s=1,\dots,S
    """)

    st.write(
        """
        Cada escenario contiene la evolución mensual simulada de los seis factores
        de riesgo y constituye la base para el análisis posterior del balance.
        """
    )

with st.expander("11. Aplicación en riesgo financiero"):
    st.write(
        """
        Las trayectorias simuladas de los factores no se interpretan como un único
        pronóstico puntual, sino como una representación probabilística de posibles
        estados futuros del sistema.
        """
    )

    st.write(
        """
        Estas trayectorias se utilizan posteriormente como entrada del modelo financiero
        del balance para trasladar la incertidumbre de los factores al cálculo del
        **NII** y del **EaR**.
        """
    )
