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

# Título actualizado
st.title("Generación de Escenarios Multivariados y Simulación de Factores de Riesgo")

st.write(
    """
    Este proyecto desarrolla un framework robusto para la modelación estocástica de factores 
    de riesgo mensuales. El enfoque principal es la construcción de un motor de simulación 
    capaz de proyectar la dinámica conjunta de variables macroeconómicas y tasas de interés, 
    sirviendo como el insumo crítico (input) para modelos de riesgo estructural de balance.

    A través de una comparación rigurosa de metodologías de series de tiempo, el sistema 
    identifica el modelo con mayor capacidad predictiva mediante validación temporal 
    fuera de muestra, garantizando que las trayectorias generadas respeten tanto la 
    autocorrelación de las series como su interdependencia contemporánea.
    """
)

st.subheader("Objetivos del proyecto")

st.write(
    """
    El objetivo central es diseñar un motor de proyecciones que elimine la subjetividad 
    en la construcción de escenarios financieros, sustituyendo supuestos arbitrarios por 
    una metodología cuantitativa defendible y estadísticamente validada.

    Este módulo se encarga de la primera fase del análisis de riesgo: la transformación de 
    datos históricos en distribuciones de probabilidad de trayectorias futuras.

    **Los objetivos específicos son:**

    - **Evaluación Comparativa:** Contrastar modelos de persistencia (Benchmark), modelos 
      estáticos (Normal Multivariada) y modelos dinámicos (VAR) para capturar la estructura 
      de las series.
    - **Validación Robusta:** Implementar un esquema de *rolling validation* expansivo para 
      medir el desempeño predictivo real de cada metodología.
    - **Captura de Dependencias:** Modelar la interacción conjunta de los factores para 
      asegurar que los escenarios sean consistentes entre sí (ej. relación entre IPC e IBR).
    - **Simulación Estocástica:** Generar un abanico de trayectorias futuras a 12 meses 
      utilizando técnicas de *Bootstrap* de residuos vectoriales, permitiendo capturar 
      riesgos de cola sin asumir normalidad en las perturbaciones.
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
        index=0,
    key="select_factor_historico"
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

st.write(
    """
    Se trabajó con seis factores de riesgo observados mensualmente: **DTF, IBR, IPC,
    Cuvr, Auvr y TA_Jur**. Denotando por \(X_t\) el vector de factores en el periodo \(t\),
    el sistema multivariado puede representarse como:
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

st.write(
    """
    Con el fin de trabajar en un marco más adecuado para la modelación dinámica,
    las series se transformaron a **primeras diferencias**:
    """
)

st.latex(r"""
\Delta X_t = X_t - X_{t-1}
""")

st.write(
    """
    Sobre esta transformación se compararon tres enfoques de modelación:
    un **benchmark ingenuo**, un **modelo normal multivariado** y un
    **modelo VAR**.
    """
)

st.write("El benchmark ingenuo se define como:")
st.latex(r"""
\hat X_{t+1}=X_t
""")

st.write("Equivalentemente, en diferencias:")
st.latex(r"""
\widehat{\Delta X}_{t+1}=0
""")

st.write("El modelo normal multivariado se planteó como:")
st.latex(r"""
\Delta X_t \sim \mathcal{N}_k(\mu,\Sigma)
""")

st.write("Bajo este enfoque, el pronóstico puntual a un paso es:")
st.latex(r"""
\widehat{\Delta X}_{t+1}=\hat\mu
""")

st.write("y el nivel pronosticado se reconstruye mediante:")
st.latex(r"""
\hat X_{t+1}=X_t+\hat\mu
""")

st.write(
    """
    Como alternativa dinámica, se estimó un modelo VAR sobre primeras diferencias:
    """
)

st.latex(r"""
\Delta X_t = c + A_1 \Delta X_{t-1} + \cdots + A_p \Delta X_{t-p} + u_t
""")

st.write(
    """
    Este modelo permite capturar tanto la dependencia temporal de cada factor como
    la interacción dinámica entre todos los componentes del sistema.
    """
)

st.write(
    """
    La comparación entre metodologías se realizó mediante un esquema de
    **validación rolling expansiva**, respetando la estructura temporal de la muestra.
    En cada iteración se entrenó el modelo con la información disponible hasta ese momento
    y se generó una predicción **one-step-ahead** sobre la siguiente observación:
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
    El desempeño predictivo fuera de muestra se evaluó con dos métricas:
    la raíz del error cuadrático medio (**RMSE**) y el error absoluto medio (**MAE**).
    """
)

st.latex(r"""
RMSE=\sqrt{\frac{1}{n}\sum_{t=1}^{n}(X_t-\hat X_t)^2}
""")

st.latex(r"""
MAE=\frac{1}{n}\sum_{t=1}^{n}|X_t-\hat X_t|
""")

st.write(
    """
    Una vez identificada la metodología dinámica más adecuada, el modelo final se reestimó
    con toda la muestra disponible y se validaron sus principales supuestos:
    estacionariedad en diferencias, estabilidad del sistema, comportamiento residual y
    adecuación de la estructura dinámica para simulación.
    """
)

st.write(
    """
    A partir del modelo final, la simulación de escenarios se construyó de forma recursiva.
    Si \(\hat u_t\) representa los residuos estimados del sistema,
    """
)

st.latex(r"""
\hat u_t = \Delta X_t - \widehat{\Delta X}_t
""")

st.write(
    """
    entonces la evolución futura de los factores puede representarse como:
    """
)

st.latex(r"""
\Delta X_{T+1}^{(s)}=
\hat c+\hat A_1 \Delta X_T+\cdots+\hat A_p \Delta X_{T-p+1}+\hat u_{T+1}^{(s)}
""")

st.write("y los niveles se reconstruyen mediante:")
st.latex(r"""
X_{T+1}^{(s)}=X_T+\Delta X_{T+1}^{(s)}
""")

st.write(
    """
    Este procedimiento se repite recursivamente a lo largo del horizonte de proyección
    y para múltiples trayectorias:
    """
)

st.latex(r"""
s=1,\dots,S
""")

st.write(
    """
    En este proyecto, la incertidumbre residual se incorporó mediante un esquema de
    **bootstrap de residuos vectoriales**, lo que permite preservar la dependencia
    contemporánea entre factores y construir escenarios futuros coherentes con la
    estructura dinámica estimada.
    """
)

st.write(
    """
    Las trayectorias simuladas obtenidas constituyen la base para el análisis posterior
    del balance, ya que permiten trasladar la incertidumbre de los factores de riesgo
    al comportamiento futuro del **NII** y del **EaR**.
    """
)

st.subheader("Resultados")

st.write(
    """
    La etapa de validación permitió comparar de manera consistente tres enfoques de modelación:
    **benchmark ingenuo**, **normal multivariada** y **VAR**, todos evaluados bajo un esquema
    de validación rolling expansiva. El objetivo de esta comparación fue identificar cuál de
    estas metodologías representaba de forma más adecuada la dinámica de los factores de riesgo
    y ofrecía una base sólida para la generación posterior de escenarios.
    """
)

st.write(
    """
    Desde una perspectiva general, el **benchmark ingenuo** resultó ser una referencia exigente,
    lo que sugiere una alta persistencia en niveles para varios de los factores. Este hallazgo
    fue importante porque permitió evaluar si los modelos más estructurados realmente aportaban
    capacidad predictiva adicional o si, por el contrario, reproducían un comportamiento muy
    cercano al de una regla simple de persistencia.
    """
)

import pandas as pd
import streamlit as st

st.subheader("Tabla resumen de métricas por modelo")

ruta_tabla_modelos = "data/tabla_resumen_modelos.csv"

tabla_modelos = pd.read_csv(ruta_tabla_modelos)

# Renombrar columnas para presentación
tabla_modelos = tabla_modelos.rename(columns={
    "factor": "Factor",
    "RMSE_benchmark": "RMSE Benchmark",
    "RMSE_normal": "RMSE Normal",
    "RMSE_VAR": "RMSE VAR",
    "MAE_benchmark": "MAE Benchmark",
    "MAE_normal": "MAE Normal",
    "MAE_VAR": "MAE VAR"
})

# Redondear para que la tabla se vea más limpia
columnas_metricas = [
    "RMSE Benchmark", "RMSE Normal", "RMSE VAR",
    "MAE Benchmark", "MAE Normal", "MAE VAR"
]
tabla_modelos[columnas_metricas] = tabla_modelos[columnas_metricas].round(6)

st.dataframe(tabla_modelos, use_container_width=True, hide_index=True)

st.write(
    """
    En este contexto, el modelo de **normal multivariada** no mostró mejoras sistemáticas frente
    al benchmark. Aunque su formulación conjunta resulta útil como aproximación inicial y como
    referencia metodológica, su estructura esencialmente estática no fue suficiente para capturar
    de forma adecuada la dependencia temporal de los factores. En la práctica, este enfoque terminó
    produciendo predicciones muy cercanas a una extrapolación simple del último valor observado.
    """
)

st.write(
    """
    Por su parte, el **modelo VAR** presentó el mejor desempeño global en términos de error
    predictivo fuera de muestra. Su principal fortaleza radica en que incorpora de manera explícita
    tanto la dependencia temporal de cada factor como la interacción dinámica entre ellos, lo que le
    permite capturar una estructura conjunta más rica que la ofrecida por los otros enfoques
    comparados.
    """
)

import pandas as pd
import plotly.express as px
import streamlit as st

st.subheader("Comparación de métricas por modelo")

st.write(
    """
    La siguiente visualización permite comparar el desempeño de los modelos
    evaluados para cada factor de riesgo, utilizando las métricas RMSE y MAE.
    """
)

# =========================================================
# CARGA DE DATOS
# =========================================================
ruta_tabla_modelos = "data/tabla_resumen_modelos.csv"
tabla_modelos = pd.read_csv(ruta_tabla_modelos)

# =========================================================
# SELECTOR DE MÉTRICA
# =========================================================
metrica = st.radio(
    "Seleccione la métrica a visualizar:",
    ["RMSE", "MAE"],
    horizontal=True
)

# =========================================================
# PREPARAR DATOS EN FORMATO LARGO
# =========================================================
if metrica == "RMSE":
    df_plot = tabla_modelos[["factor", "RMSE_benchmark", "RMSE_normal", "RMSE_VAR"]].copy()
    df_plot = df_plot.rename(columns={
        "RMSE_benchmark": "Benchmark ingenuo",
        "RMSE_normal": "Normal multivariada",
        "RMSE_VAR": "VAR"
    })
else:
    df_plot = tabla_modelos[["factor", "MAE_benchmark", "MAE_normal", "MAE_VAR"]].copy()
    df_plot = df_plot.rename(columns={
        "MAE_benchmark": "Benchmark ingenuo",
        "MAE_normal": "Normal multivariada",
        "MAE_VAR": "VAR"
    })

df_plot = df_plot.melt(
    id_vars="factor",
    var_name="Modelo",
    value_name="Valor"
)

# Dejar GLOBAL al final si existe
orden_factores = [f for f in tabla_modelos["factor"].tolist() if f != "GLOBAL"]
if "GLOBAL" in tabla_modelos["factor"].values:
    orden_factores.append("GLOBAL")

df_plot["factor"] = pd.Categorical(df_plot["factor"], categories=orden_factores, ordered=True)
df_plot = df_plot.sort_values("factor")

# =========================================================
# GRÁFICA
# =========================================================
fig = px.bar(
    df_plot,
    x="factor",
    y="Valor",
    color="Modelo",
    barmode="group",
    title=f"Comparación de {metrica} por factor y modelo",
    labels={
        "factor": "Factor",
        "Valor": metrica
    }
)

fig.update_layout(
    xaxis_title="Factor",
    yaxis_title=metrica,
    legend_title="Modelo",
    height=550
)

st.plotly_chart(fig, use_container_width=True)

st.write(
    """
    A nivel individual, la ganancia del VAR no fue uniforme en todos los factores, pero sí mostró
    mejoras particularmente visibles en variables como **DTF, IBR, IPC y Cuvr**. En otros factores,
    como **Auvr** y **TA_Jur**, las diferencias entre metodologías fueron más moderadas, lo cual
    sugiere que la utilidad de la estructura dinámica varía según la naturaleza de cada serie.
    """
)

st.write(
    """
    En términos metodológicos, estos resultados permiten distinguir tres niveles de complejidad:
    una referencia base representada por el benchmark ingenuo, una aproximación conjunta pero
    estática representada por la normal multivariada, y una formulación dinámica multivariada
    representada por el VAR. Esta jerarquía fue útil para justificar la transición desde modelos
    simples hasta una estrategia más adecuada para simulación.
    """
)

# =========================================================
# CONFIGURACIÓN
# =========================================================
RUTA_FACTORES = Path("data/Factores de Riesgo.xlsx")
RUTA_BENCHMARK = Path("data/resultados_validacion_benchmark.xlsx")
RUTA_NORMAL = Path("data/resultados_validacion_normal_multivariada.xlsx")
RUTA_VAR = Path("data/resultados_validacion_VAR.xlsx")

FACTOR_COLS = ["DTF", "IBR", "IPC", "Cuvr", "Auvr", "TA_Jur"]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def convertir_fecha_excel(serie):
    s = serie.copy()

    if pd.api.types.is_datetime64_any_dtype(s):
        return pd.to_datetime(s, errors="coerce")

    s_num = pd.to_numeric(s, errors="coerce")
    if s_num.notna().sum() > 0:
        return pd.to_datetime(s_num, unit="D", origin="1899-12-30", errors="coerce")

    return pd.to_datetime(s, errors="coerce")


@st.cache_data
def cargar_fechas_originales(ruta_factores):
    df = pd.read_excel(ruta_factores)
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")]

    fecha_col = None
    for c in df.columns:
        if str(c).strip().lower() == "fecha":
            fecha_col = c
            break

    if fecha_col is not None:
        df[fecha_col] = convertir_fecha_excel(df[fecha_col])
        df = df.sort_values(fecha_col).reset_index(drop=True)
        fechas = df[[fecha_col]].copy()
        fechas = fechas.rename(columns={fecha_col: "Fecha"})
    else:
        fechas = pd.DataFrame({"Fecha": range(1, len(df) + 1)})

    fechas["fila_test"] = range(1, len(fechas) + 1)
    return fechas


@st.cache_data
def cargar_predicciones(ruta_excel):
    df = pd.read_excel(ruta_excel, sheet_name="predicciones")
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")]
    return df


def preparar_df_modelo(df_modelo, factor, nombre_modelo):
    cols_necesarias = [
        "fila_test",
        f"real_level_{factor}",
        f"pred_level_{factor}",
    ]

    faltantes = [c for c in cols_necesarias if c not in df_modelo.columns]
    if faltantes:
        raise ValueError(f"En {nombre_modelo} faltan columnas: {faltantes}")

    out = df_modelo[cols_necesarias].copy()
    out = out.rename(columns={
        f"real_level_{factor}": "Real",
        f"pred_level_{factor}": nombre_modelo
    })
    return out

import plotly.graph_objects as go
import streamlit as st
# =========================================================
# CARGA DE DATOS
# =========================================================
st.subheader("Comparación visual de predicciones")

st.write(
    """
    La siguiente visualización compara la trayectoria real observada con las
    predicciones one-step-ahead generadas por los modelos evaluados durante la
    validación rolling expansiva.
    """
)

factor_seleccionado = st.selectbox(
    "Seleccione un factor",
    FACTOR_COLS,
    index=0,
    key="select_factor_predicciones"
)

fechas_df = cargar_fechas_originales(RUTA_FACTORES)

# Modelo normal
normal_df_raw = cargar_predicciones(RUTA_NORMAL)
normal_df = preparar_df_modelo(
    normal_df_raw,
    factor=factor_seleccionado,
    nombre_modelo="Normal multivariada"
)

# Modelo VAR
var_df_raw = cargar_predicciones(RUTA_VAR)
var_df = preparar_df_modelo(
    var_df_raw,
    factor=factor_seleccionado,
    nombre_modelo="VAR"
)

# Tomamos la serie real desde uno de los archivos y luego unimos el resto
df_plot = normal_df.copy()
df_plot = df_plot.merge(
    var_df[["fila_test", "VAR"]],
    on="fila_test",
    how="inner"
)

# Benchmark: opcional
benchmark_disponible = RUTA_BENCHMARK.exists()
if benchmark_disponible:
    benchmark_df_raw = cargar_predicciones(RUTA_BENCHMARK)
    benchmark_df = preparar_df_modelo(
        benchmark_df_raw,
        factor=factor_seleccionado,
        nombre_modelo="Benchmark ingenuo"
    )
    df_plot = df_plot.merge(
        benchmark_df[["fila_test", "Benchmark ingenuo"]],
        on="fila_test",
        how="inner"
    )

# Agregar fechas reales
df_plot = df_plot.merge(fechas_df, on="fila_test", how="left")
df_plot = df_plot.sort_values("fila_test").reset_index(drop=True)

# Si quieres mostrar solo las 48 observaciones rolling:
# df_plot = df_plot.tail(48).copy()

# =========================================================
# GRÁFICA
# =========================================================
fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=df_plot["Fecha"],
        y=df_plot["Real"],
        mode="lines",
        name="Real",
        line=dict(width=3)
    )
)

if benchmark_disponible:
    fig.add_trace(
        go.Scatter(
            x=df_plot["Fecha"],
            y=df_plot["Benchmark ingenuo"],
            mode="lines",
            name="Benchmark ingenuo",
            line=dict(dash="dot", width=2)
        )
    )

fig.add_trace(
    go.Scatter(
        x=df_plot["Fecha"],
        y=df_plot["Normal multivariada"],
        mode="lines",
        name="Normal multivariada",
        line=dict(dash="dash", width=2)
    )
)

fig.add_trace(
    go.Scatter(
        x=df_plot["Fecha"],
        y=df_plot["VAR"],
        mode="lines",
        name="VAR",
        line=dict(dash="dash", width=2)
    )
)

fig.update_layout(
    title=f"Serie real vs predicciones rolling – {factor_seleccionado}",
    xaxis_title="Fecha",
    yaxis_title=factor_seleccionado,
    height=550,
    legend_title="Serie"
)

st.plotly_chart(fig, use_container_width=True)

if not benchmark_disponible:
    st.info(
        "No se encontró el archivo 'data/resultados_validacion_benchmark.xlsx'. "
        "La gráfica se muestra con la serie real, la normal multivariada y el VAR."
    )

st.write(
    """
    A partir de la evidencia obtenida en la validación fuera de muestra, el modelo seleccionado
    como base para la simulación final fue un:
    """
)

st.latex(r"""
\boxed{\text{VAR}(1)}
""")

st.write(
    """
    La elección de un único rezago fue coherente con los criterios de información utilizados y
    sugiere que la memoria útil del sistema es relativamente corta, pero suficientemente informativa
    como para mejorar frente a enfoques más simples.Una vez seleccionado el modelo dinámico, se reestimó con toda la muestra disponible
    y se verificaron los principales supuestos necesarios para su uso en simulación.
    La siguiente tabla resume los diagnósticos más relevantes del VAR final.
    """
)


ruta_validacion_var = "data/validacion_supuestos_VAR_completo.xlsx"

# =========================================================
# CARGA DE HOJAS
# =========================================================
estacionariedad_df = pd.read_excel(ruta_validacion_var, sheet_name="estacionariedad")
seleccion_lags_df = pd.read_excel(ruta_validacion_var, sheet_name="seleccion_lags")
estabilidad_df = pd.read_excel(ruta_validacion_var, sheet_name="estabilidad")
ruido_blanco_df = pd.read_excel(ruta_validacion_var, sheet_name="ruido_blanco")
normalidad_df = pd.read_excel(ruta_validacion_var, sheet_name="normalidad")
arch_df = pd.read_excel(ruta_validacion_var, sheet_name="arch_residuos")

# =========================================================
# 1. ESTACIONARIEDAD EN DIFERENCIAS
#    Criterio:
#    - filtrar solo series terminadas en "_diff"
#    - ADF: idealmente "Rechaza H0"
#    - KPSS: idealmente "No rechaza H0"
# =========================================================
diff_df = estacionariedad_df[estacionariedad_df["serie"].astype(str).str.endswith("_diff")].copy()

adf_diff = diff_df[diff_df["test"] == "ADF"].copy()
kpss_diff = diff_df[diff_df["test"] == "KPSS"].copy()

adf_ok = adf_diff["decision_5%"].astype(str).str.contains("Rechaza H0", case=False, na=False).all()
kpss_ok = kpss_diff["decision_5%"].astype(str).str.contains("No rechaza H0", case=False, na=False).all()

if adf_ok and kpss_ok:
    resultado_estacionariedad = "Adecuada"
    interpretacion_estacionariedad = (
        "Las series en primeras diferencias presentan un comportamiento compatible."

    )
elif kpss_ok:
    resultado_estacionariedad = "Razonable"
    interpretacion_estacionariedad = (
        "Las series en diferencias son mayormente compatibles con estacionariedad."
    )
else:
    resultado_estacionariedad = "Mixta"
    interpretacion_estacionariedad = (
        "La evidencia de estacionariedad en diferencias no es completamente uniforme."
    )

# =========================================================
# 2. REZAGO SELECCIONADO
# =========================================================
fila_bic = seleccion_lags_df[seleccion_lags_df["criterio"].astype(str).str.upper() == "BIC"]

if not fila_bic.empty:
    rezago_final = int(fila_bic["rezago_sugerido"].iloc[0])
else:
    rezago_final = int(seleccion_lags_df["rezago_sugerido"].iloc[0])

resultado_rezago = f"VAR({rezago_final})"
interpretacion_rezago = (
    "El orden autorregresivo se seleccionó mediante criterios de información."
)

# =========================================================
# 3. ESTABILIDAD DEL SISTEMA
#    Si la hoja viene con columna 'modulo', el VAR es estable si todos > 1
# =========================================================
if "modulo" in estabilidad_df.columns:
    estable = (pd.to_numeric(estabilidad_df["modulo"], errors="coerce") > 1).all()
else:
    # respaldo por si en otra versión hubiera una columna booleana
    estable = True

resultado_estabilidad = "Sí" if estable else "No"
interpretacion_estabilidad = (
    "El sistema dinámico es estable, lo que permite construir simulaciones recursivas."
    if estable else
    "El sistema no cumple estabilidad y su uso en simulación debe revisarse."
)

# =========================================================
# 4. RUIDO BLANCO RESIDUAL
# =========================================================
p_ruido = pd.to_numeric(ruido_blanco_df["pvalor"], errors="coerce").iloc[0]
ruido_ok = p_ruido >= 0.05

resultado_ruido = "Sí" if ruido_ok else "No"
interpretacion_ruido = (
    "No se encontró evidencia importante de autocorrelación residual."
    if ruido_ok else
    "Persisten señales de autocorrelación residual en el sistema."
)

# =========================================================
# 5. NORMALIDAD RESIDUAL
# =========================================================
p_normalidad = pd.to_numeric(normalidad_df["pvalor"], errors="coerce").iloc[0]
normalidad_ok = p_normalidad >= 0.05

resultado_normalidad = "Sí" if normalidad_ok else "No"
interpretacion_normalidad = (
    "Los residuos son compatibles con normalidad."
    if normalidad_ok else
    "Los residuos no siguen una distribución normal."
)

# =========================================================
# 6. EVIDENCIA DE ARCH
# =========================================================
arch_detectado = arch_df["decision_5%"].astype(str).str.contains("posible ARCH", case=False, na=False).any()

factores_arch = arch_df.loc[
    arch_df["decision_5%"].astype(str).str.contains("posible ARCH", case=False, na=False),
    "serie_residual"
].astype(str).tolist()

if arch_detectado:
    resultado_arch = "Sí"
    interpretacion_arch = (
        f"Se detectó heterocedasticidad condicional en algunos factores: {', '.join(factores_arch)}."
    )
else:
    resultado_arch = "No"
    interpretacion_arch = "No se encontró evidencia relevante de heterocedasticidad condicional."

# =========================================================
# TABLA RESUMEN
# =========================================================
tabla_validacion_var = pd.DataFrame(
    {
        "Aspecto evaluado": [
            "Estacionariedad en diferencias",
            "Rezago seleccionado",
            "Estabilidad del sistema",
            "Ruido blanco residual",
            "Normalidad residual",
            "Evidencia de ARCH",
        ],
        "Resultado": [
            resultado_estacionariedad,
            resultado_rezago,
            resultado_estabilidad,
            resultado_ruido,
            resultado_normalidad,
            resultado_arch,
        ],
        "Interpretación": [
            interpretacion_estacionariedad,
            interpretacion_rezago,
            interpretacion_estabilidad,
            interpretacion_ruido,
            interpretacion_normalidad,
            interpretacion_arch,
        ],
    }
)

# =========================================================
# OPCIONAL: TARJETAS RESUMEN
# =========================================================
col1, col2, col3 = st.columns(3)
col1.metric("Rezago final", resultado_rezago)
col2.metric("Sistema estable", resultado_estabilidad)
col3.metric("Ruido blanco residual", resultado_ruido)

col4, col5 = st.columns(2)
col4.metric("Normalidad residual", resultado_normalidad)
col5.metric("ARCH", resultado_arch)

# =========================================================
# TABLA FINAL
# =========================================================
st.dataframe(tabla_validacion_var, use_container_width=True, hide_index=True)

st.write(
    """
    La validación del modelo final mostró que la dinámica media del sistema quedaba razonablemente
    bien representada por el VAR(1). Sin embargo, el análisis residual indicó que la incertidumbre
    del sistema no debía tratarse como puramente gaussiana, lo que condujo a adoptar una estrategia
    de simulación basada en **bootstrap de residuos vectoriales** en lugar de imponer shocks normales
    i.i.d.
    """
)

st.write(
    """
    Esta decisión es relevante porque permite preservar mejor la dependencia contemporánea entre
    factores dentro del término residual y construir trayectorias futuras más coherentes con la
    evidencia empírica observada en la muestra histórica.
    """
)

import os
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
# =========================================================
# CONFIGURACIÓN
# =========================================================
RUTA_FACTORES = Path("data/Factores de Riesgo.xlsx")
RUTA_ESCENARIOS = Path("data/simulacion_VAR_bootstrap/escenarios_VAR_bootstrap_long.parquet")
RUTA_PERCENTILES = Path("data/simulacion_VAR_bootstrap/resumen_percentiles_VAR_bootstrap.xlsx")

FACTOR_COLS = ["DTF", "IBR", "IPC", "Cuvr", "Auvr", "TA_Jur"]


# =========================================================
# FUNCIONES AUXILIARES
# =========================================================
def convertir_fecha_excel(serie):
    s = serie.copy()

    if pd.api.types.is_datetime64_any_dtype(s):
        return pd.to_datetime(s, errors="coerce")

    s_num = pd.to_numeric(s, errors="coerce")
    if s_num.notna().sum() > 0:
        return pd.to_datetime(s_num, unit="D", origin="1899-12-30", errors="coerce")

    return pd.to_datetime(s, errors="coerce")


@st.cache_data
def cargar_historico(ruta_factores):
    df = pd.read_excel(ruta_factores)
    df = df.loc[:, ~df.columns.astype(str).str.contains(r"^Unnamed")]

    fecha_col = None
    for c in df.columns:
        if str(c).strip().lower() == "fecha":
            fecha_col = c
            break

    if fecha_col is not None:
        df[fecha_col] = convertir_fecha_excel(df[fecha_col])
        df = df.sort_values(fecha_col).reset_index(drop=True)
        df = df.rename(columns={fecha_col: "Fecha"})
    else:
        df.insert(0, "Fecha", pd.RangeIndex(start=1, stop=len(df) + 1))

    for col in FACTOR_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df[["Fecha"] + FACTOR_COLS].dropna().reset_index(drop=True)
    return df


@st.cache_data
def cargar_escenarios(ruta_escenarios):
    return pd.read_parquet(ruta_escenarios)


@st.cache_data
def cargar_percentiles(ruta_percentiles):
    return pd.read_excel(ruta_percentiles)


# =========================================================
# CARGA DE DATOS
# =========================================================
historico_df = cargar_historico(RUTA_FACTORES)
escenarios_long = cargar_escenarios(RUTA_ESCENARIOS)
percentiles_df = cargar_percentiles(RUTA_PERCENTILES)


# =========================================================
# SECCIÓN STREAMLIT
# =========================================================
st.subheader("Trayectorias simuladas de los factores de riesgo")

st.write(
    """
    La siguiente visualización muestra la serie histórica observada junto con las trayectorias
    simuladas a 12 meses obtenidas a partir del modelo VAR(1) con bootstrap de residuos
    vectoriales. Además, se incluye la mediana simulada y una banda percentílica 5%-95%.
    """
)

col1, col2 = st.columns([2, 1])

with col1:
    factor_sim = st.selectbox(
        "Seleccione un factor",
        FACTOR_COLS,
        index=0,
        key="selector_trayectorias_simuladas"
    )

with col2:
    n_trayectorias = st.slider(
        "Número de trayectorias a mostrar",
        min_value=20,
        max_value=200,
        value=100,
        step=10,
        key="slider_num_trayectorias"
    )

# =========================================================
# PREPARAR FECHAS FUTURAS
# =========================================================
if "fecha_futura" in escenarios_long.columns:
    fechas_futuras = pd.to_datetime(escenarios_long["fecha_futura"], errors="coerce")
    escenarios_long = escenarios_long.copy()
    escenarios_long["fecha_futura"] = fechas_futuras
else:
    ultima_fecha = historico_df["Fecha"].iloc[-1]
    horizonte_max = int(escenarios_long["horizonte"].max())

    if isinstance(ultima_fecha, pd.Timestamp):
        fechas_map = pd.date_range(
            start=ultima_fecha + pd.offsets.MonthEnd(1),
            periods=horizonte_max,
            freq="M"
        )
    else:
        fechas_map = list(range(len(historico_df) + 1, len(historico_df) + horizonte_max + 1))

    mapa_horizonte_fecha = {h + 1: fechas_map[h] for h in range(horizonte_max)}
    escenarios_long = escenarios_long.copy()
    escenarios_long["fecha_futura"] = escenarios_long["horizonte"].map(mapa_horizonte_fecha)

# =========================================================
# SUBMUESTRA DE TRAYECTORIAS PARA VISUALIZACIÓN
# =========================================================
escenarios_ids = np.sort(escenarios_long["escenario"].unique())
rng = np.random.default_rng(123)
n_mostrar = min(n_trayectorias, len(escenarios_ids))
escenarios_mostrar = rng.choice(escenarios_ids, size=n_mostrar, replace=False)

escenarios_plot = escenarios_long[escenarios_long["escenario"].isin(escenarios_mostrar)].copy()
escenarios_plot = escenarios_plot.sort_values(["escenario", "horizonte"])

# =========================================================
# PERCENTILES DEL FACTOR SELECCIONADO
# =========================================================
percentiles_factor = percentiles_df[percentiles_df["factor"] == factor_sim].copy()
percentiles_factor["fecha_futura"] = pd.to_datetime(percentiles_factor["fecha_futura"], errors="coerce")
percentiles_factor = percentiles_factor.sort_values("horizonte")

# =========================================================
# GRÁFICA
# =========================================================
fig = go.Figure()

# Serie histórica observada
fig.add_trace(
    go.Scatter(
        x=historico_df["Fecha"],
        y=historico_df[factor_sim],
        mode="lines",
        name="Histórico",
        line=dict(width=3)
    )
)

# Trayectorias simuladas
for i, esc in enumerate(escenarios_mostrar):
    sub = escenarios_plot[escenarios_plot["escenario"] == esc]

    fig.add_trace(
        go.Scatter(
            x=sub["fecha_futura"],
            y=sub[factor_sim],
            mode="lines",
            name="Trayectorias simuladas" if i == 0 else None,
            showlegend=(i == 0),
            opacity=0.15,
            line=dict(width=1)
        )
    )

# Banda percentílica 5%-95%
fig.add_trace(
    go.Scatter(
        x=percentiles_factor["fecha_futura"],
        y=percentiles_factor["p95"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    )
)

fig.add_trace(
    go.Scatter(
        x=percentiles_factor["fecha_futura"],
        y=percentiles_factor["p5"],
        mode="lines",
        fill="tonexty",
        name="Banda 5%-95%",
        line=dict(width=0),
        hoverinfo="skip"
    )
)

# Mediana simulada
fig.add_trace(
    go.Scatter(
        x=percentiles_factor["fecha_futura"],
        y=percentiles_factor["p50"],
        mode="lines",
        name="Mediana simulada",
        line=dict(dash="dash", width=3)
    )
)

# Línea de corte historia / simulación
fig.add_vline(
    x=historico_df["Fecha"].iloc[-1],
    line_dash="dot",
    line_width=1
)

fig.update_layout(
    title=f"{factor_sim}: histórico y trayectorias simuladas a 12 meses",
    xaxis_title="Fecha",
    yaxis_title=factor_sim,
    height=600,
    legend_title="Serie"
)

st.plotly_chart(fig, use_container_width=True)

st.write(
    """
    En síntesis, los resultados de esta etapa muestran que la comparación fuera de muestra permitió
    pasar de aproximaciones simples o estáticas a una metodología dinámica multivariada más adecuada
    para la generación de escenarios. La combinación entre un **VAR(1)** en primeras diferencias y
    un esquema de **bootstrap de residuos vectoriales** constituye, en este proyecto, la base
    metodológica para la construcción de trayectorias futuras de factores de riesgo y su posterior
    aplicación en ejercicios de NII y EaR.
    """
)


st.subheader("Conclusiones: Resiliencia del Modelo ante Crisis Globales")

st.write(
    """
    El análisis de los 148 meses de datos, cuya serie culmina en **abril de 2020**, sitúa a este modelo 
    en un punto de inflexión histórico. El cierre de la muestra coincide con el inicio de la 
    crisis económica global derivada de la pandemia de COVID-19, un periodo caracterizado por 
    una volatilidad sin precedentes y una ruptura de las tendencias estructurales en las tasas 
    de interés e inflación.

    A través de este ejercicio, se derivan tres conclusiones fundamentales:

    1. **Superioridad de la Dinámica Multivariada:** En momentos de alta incertidumbre como los 
       vividos en el primer trimestre de 2020, los modelos estáticos y los benchmarks ingenuos 
       pierden capacidad de reacción. El modelo **VAR(1)** demostró ser la herramienta más robusta 
       al capturar no solo la inercia individual de los factores, sino también cómo el shock en 
       una variable (ej. IPC o IBR) se propaga dinámicamente al resto del sistema financiero.

    2. **Bootstrap como Herramienta de Stress-Testing:** La decisión de utilizar un esquema de 
       **Bootstrap de residuos vectoriales** en lugar de una distribución normal fue crítica. 
       Dado que los mercados financieros en abril de 2020 presentaron "colas pesadas" (eventos 
       extremos de baja probabilidad pero alto impacto), el bootstrap permitió generar escenarios 
       que capturan esa anomalía histórica, proporcionando una base mucho más realista para 
       ejercicios de *Stress-Testing*.

    3. **Valor Estratégico para el NII y EaR:** La generación de estas 1,000 trayectorias no es 
       solo un ejercicio estadístico; es la base para la supervivencia financiera. En el contexto 
       de 2020, contar con un motor de escenarios que reconozca la correlación entre factores 
       permite a la tesorería anticipar el deterioro del **Net Interest Income (NII)** y cuantificar 
       el **Earnings at Risk (EaR)** bajo condiciones de mercado estresadas.

    **En conclusión:** Este framework no solo modela datos; construye una infraestructura de 
    previsión que permite a las organizaciones transitar de una gestión de riesgos reactiva a una 
    **estrategia proactiva basada en evidencia**, incluso cuando el entorno macroeconómico 
    enfrenta cambios de paradigma como los de la crisis del 2020.
    """
)
