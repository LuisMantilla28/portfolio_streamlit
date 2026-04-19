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
    El objetivo fue modelar la dinámica conjunta de varios factores de riesgo mensuales
    para generar escenarios futuros consistentes y utilizarlos posteriormente en ejercicios
    de simulación financiera, especialmente en la estimación del **Net Interest Income (NII)**
    y del **Earnings at Risk (EaR)**.
    """
)

st.markdown("---")

st.subheader("1. Variables consideradas")

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
\qquad t=1,\dots,148
""")

st.write(
    """
    En total se utilizaron **148 observaciones mensuales**, lo que permitió construir
    un ejercicio de validación temporal y, posteriormente, estimar el modelo final
    con toda la muestra.
    """
)

st.markdown("---")

st.subheader("2. Transformación de las series")

st.write(
    """
    Dado que varios factores en niveles presentaban señales de no estacionariedad o resultados
    mixtos en las pruebas estadísticas, la modelación se realizó sobre **primeras diferencias**.
    """
)

st.latex(r"""
\Delta X_t = X_t - X_{t-1}
""")

st.write(
    """
    Esta transformación permite trabajar con series más cercanas a la estacionariedad y resulta
    más adecuada para modelos dinámicos multivariados como el VAR.
    """
)

st.markdown("---")

st.subheader("3. Modelos comparados")

st.write(
    """
    Se compararon tres enfoques predictivos para determinar cuál representaba mejor la dinámica
    de los factores de riesgo:
    """
)

st.markdown(
    """
    - **Benchmark ingenuo**: asume que el siguiente valor es igual al valor actual.
    - **Normal multivariada**: modela conjuntamente los cambios mensuales con una distribución
      normal multivariada.
    - **VAR**: incorpora dependencia temporal e interacción dinámica entre los factores mediante
      sus rezagos.
    """
)

st.write("**Benchmark ingenuo**")
st.latex(r"""
\hat X_{t+1} = X_t
""")

st.write("Equivalentemente, en diferencias:")
st.latex(r"""
\widehat{\Delta X}_{t+1}=0
""")

st.write("**Modelo normal multivariado**")
st.latex(r"""
\Delta X_t \sim \mathcal N_k(\mu,\Sigma)
""")

st.write("El pronóstico puntual a un paso está dado por:")
st.latex(r"""
\widehat{\Delta X}_{t+1} = \hat\mu
""")

st.write("y el nivel pronosticado se reconstruye como:")
st.latex(r"""
\hat X_{t+1}=X_t+\hat\mu
""")

st.write("**Modelo VAR**")
st.latex(r"""
\Delta X_t = c + A_1 \Delta X_{t-1} + \cdots + A_p \Delta X_{t-p} + u_t
""")

st.write(
    """
    A diferencia del modelo normal multivariado estático, el VAR permite capturar tanto la
    dependencia temporal de cada factor como la interacción dinámica entre ellos.
    """
)

st.markdown("---")

st.subheader("4. Esquema de validación")

st.write(
    """
    Para comparar los modelos se utilizó una estrategia de **validación rolling expansiva**
    (*expanding window*), respetando el orden temporal de la muestra y evitando el uso de
    información futura en el entrenamiento.
    """
)

st.write(
    """
    Se partió de una ventana inicial de 100 observaciones y luego se realizaron predicciones
    one-step-ahead expandiendo la muestra en cada iteración:
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
    En cada split se ajustó el modelo con la muestra de entrenamiento, se generó una predicción
    a un paso adelante y se comparó con el valor realmente observado.
    """
)

st.markdown("---")

st.subheader("5. Métricas de evaluación")

st.write(
    """
    El desempeño predictivo fuera de muestra se evaluó mediante dos métricas:
    """
)

st.write("**Raíz del error cuadrático medio (RMSE)**")
st.latex(r"""
RMSE = \sqrt{\frac{1}{n}\sum_{t=1}^{n}(X_t-\hat X_t)^2}
""")

st.write("**Error absoluto medio (MAE)**")
st.latex(r"""
MAE = \frac{1}{n}\sum_{t=1}^{n}|X_t-\hat X_t|
""")

st.write(
    """
    Ambas métricas se calcularon por factor y también de forma global para comparar de manera
    consistente los enfoques propuestos.
    """
)

st.markdown("---")

st.subheader("6. Selección del modelo final")

st.write(
    """
    Los resultados mostraron que el **benchmark ingenuo** era competitivo, que la
    **normal multivariada** no mejoraba de forma sistemática al benchmark y que el
    **modelo VAR** ofrecía el mejor desempeño global.
    """
)

st.write(
    """
    A partir de esta evidencia, el modelo seleccionado como base para la simulación final fue un:
    """
)

st.latex(r"""
\boxed{\text{VAR}(1)}
""")

st.write(
    """
    El orden del VAR se eligió utilizando criterios de información como AIC, BIC, HQIC y FPE,
    los cuales coincidieron en seleccionar un rezago igual a uno.
    """
)

st.markdown("---")

st.subheader("7. Estimación final y validación del VAR")

st.write(
    """
    Una vez escogido el modelo, el VAR(1) se reestimó utilizando toda la muestra disponible.
    Luego se validaron sus principales supuestos:
    """
)

st.markdown(
    """
    - estacionariedad de las series en diferencias;
    - estabilidad del sistema;
    - ausencia de autocorrelación residual importante;
    - comportamiento de los residuos en términos de normalidad;
    - evidencia de heterocedasticidad condicional.
    """
)

st.write(
    """
    La evidencia empírica mostró que el sistema era estable y que la dinámica media conjunta
    quedaba razonablemente representada. Sin embargo, los residuos no resultaron gaussianos
    y, en algunos factores, se encontró evidencia de heterocedasticidad condicional.
    """
)

st.markdown("---")

st.subheader("8. Simulación de escenarios")

st.write(
    """
    Debido a que los residuos del VAR no cumplían adecuadamente el supuesto de normalidad,
    la simulación final no se realizó mediante shocks gaussianos i.i.d. En su lugar, se
    utilizó un enfoque de **bootstrap de residuos vectoriales**.
    """
)

st.write("El modelo base para la simulación fue:")
st.latex(r"""
\Delta X_t = c + A_1 \Delta X_{t-1} + u_t
""")

st.write("con residuos estimados:")
st.latex(r"""
\hat u_t = \Delta X_t - \widehat{\Delta X}_t
""")

st.write(
    """
    En cada paso de simulación se seleccionó aleatoriamente con reemplazo un residuo vectorial
    histórico completo, preservando así la dependencia contemporánea entre factores.
    """
)

st.write("La simulación recursiva se construyó como:")
st.latex(r"""
\Delta X_{T+1}^{(s)} = \hat c + \hat A_1 \Delta X_T + \hat u_{T+1}^{(s)}
""")

st.latex(r"""
X_{T+1}^{(s)} = X_T + \Delta X_{T+1}^{(s)}
""")

st.write("y de forma recursiva para horizontes posteriores:")
st.latex(r"""
\Delta X_{T+h}^{(s)} =
\hat c + \hat A_1 \Delta X_{T+h-1}^{(s)} + \hat u_{T+h}^{(s)},
\qquad h=1,\dots,12
""")

st.write(
    """
    Este procedimiento se repitió para:
    """
)

st.latex(r"""
s=1,\dots,1000
""")

st.write(
    """
    obteniendo así **1000 trayectorias mensuales a 12 meses** para cada uno de los factores
    de riesgo.
    """
)

st.markdown("---")

st.subheader("9. Aplicación financiera")

st.write(
    """
    Las trayectorias simuladas de los factores de riesgo se utilizan posteriormente como
    insumo del modelo financiero del balance. A partir de ellas se generan trayectorias
    futuras del NII y, con ello, se cuantifica el **Earnings at Risk (EaR)** bajo múltiples
    escenarios.
    """
)

st.markdown("---")

st.subheader("10. Conclusión metodológica")

st.write(
    """
    En síntesis, la estrategia implementada consistió en:

    1. transformar las series a primeras diferencias;
    2. comparar benchmark ingenuo, normal multivariada y VAR mediante validación rolling expansiva;
    3. seleccionar el VAR(1) como mejor modelo predictivo;
    4. reestimarlo con toda la muestra disponible;
    5. validar su estabilidad y comportamiento residual;
    6. generar escenarios futuros mediante bootstrap de residuos vectoriales.

    Este enfoque permite combinar validación estadística, modelación dinámica multivariada
    y simulación empírica de innovaciones, construyendo una base coherente para ejercicios
    de riesgo financiero orientados a NII y EaR.
    """
)

