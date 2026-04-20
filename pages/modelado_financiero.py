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
    page_title="Modelado financiero",
    page_icon="💰",
    layout="wide"
)

# Título actualizado
st.title("Riesgo de Tasa de Interés en el Libro Bancario: proyección del NII y cálculo de EaR")

st.write("""
Este proyecto presenta un ejercicio de **riesgo de tasa de interés en el libro bancario**, 
centrado en la proyección del **Ingreso Neto por Intereses (NII)** y en la estimación de la 
métrica **Earnings at Risk (EaR)** a un horizonte de un año.

A partir de un balance con posiciones activas y pasivas, junto con información histórica de 
factores de riesgo como **DTF, IBR, IPC** y tasas asociadas a productos de vivienda y cuentas 
jurídicas, se construye un esquema de simulación para evaluar cómo los cambios en las tasas e 
indicadores afectan el margen financiero de la entidad.

El análisis incorpora la estructura contractual de las posiciones, incluyendo su naturaleza, 
vencimiento, plan de amortización y periodicidad de repricing, con el fin de obtener una visión 
más realista de la sensibilidad del balance ante distintos escenarios.

Finalmente, los resultados se presentan de forma agregada y desagregada por **factor de riesgo** 
y **cartera**, permitiendo identificar las principales fuentes de exposición y el comportamiento 
del NII bajo escenarios adversos.
""")

st.subheader("Objetivos")

st.markdown("""
**Objetivo general**

Desarrollar un ejercicio de medición del **riesgo de tasa de interés en el libro bancario** 
mediante la proyección del **Ingreso Neto por Intereses (NII)** y el cálculo de la métrica 
**Earnings at Risk (EaR)** a un horizonte de 12 meses, considerando la sensibilidad del balance 
ante cambios en los principales factores de riesgo.

**Objetivos específicos**

- Integrar la información del balance con la serie histórica de factores de riesgo para construir 
un marco consistente de análisis del margen financiero.

- Proyectar el NII bajo un escenario base y bajo múltiples trayectorias simuladas de tasas e indicadores, 
incorporando las características contractuales de cada posición.

- Cuantificar el **EaR total** del portafolio y desagregarlo por **factor de riesgo** y por **cartera**, 
con el fin de identificar las principales fuentes de exposición.

- Analizar el comportamiento mensual del NII y evaluar cómo los cambios en las tasas afectan 
la estabilidad del margen financiero de la entidad.
""")

st.subheader("Datos")

st.markdown("""
El análisis se apoya en dos fuentes principales de información:

- **Balance bancario:** contiene las posiciones activas y pasivas del libro bancario, junto con 
atributos relevantes para la valoración financiera, como el saldo de capital, la naturaleza de 
la posición, la tasa de referencia, el spread, la fecha de inicio, la fecha de vencimiento, el 
plan de amortización y la periodicidad de repricing.

- **Factores de riesgo:** incluye la serie histórica mensual de indicadores y tasas relevantes para 
el ejercicio, entre ellos **DTF, IBR, IPC**, así como tasas asociadas a productos de vivienda y 
cuentas jurídicas.

A partir de estas fuentes se construye un escenario base y un conjunto de trayectorias simuladas 
para proyectar el comportamiento del **Ingreso Neto por Intereses (NII)** durante un horizonte de 
12 meses.

En particular, el balance permite modelar la estructura contractual de cada posición, mientras que 
los factores de riesgo capturan la dinámica de las variables que determinan la evolución de las 
tasas indexadas. La combinación de ambas fuentes permite evaluar la sensibilidad del margen 
financiero ante distintos escenarios de mercado.
""")

# ============================================================
# SECCIÓN: DATOS - BALANCE.XLSX
# ============================================================
st.subheader("Datos")

ruta_balance = Path("data/modelo_financiero_data/Balance.xlsx")

@st.cache_data
def cargar_balance(ruta):
    df = pd.read_excel(ruta, sheet_name="InfoFacial").copy()
    df.columns = [c.strip() for c in df.columns]

    # Limpieza básica
    df["Fecha Inicio"] = pd.to_datetime(df["Fecha Inicio"], errors="coerce")
    df["Fecha Vencimiento"] = pd.to_datetime(df["Fecha Vencimiento"], errors="coerce")
    df["SaldoCapital"] = pd.to_numeric(df["SaldoCapital"], errors="coerce")
    df["PuntosAdicionales"] = pd.to_numeric(df["PuntosAdicionales"], errors="coerce")
    df["FrecuenciaInteres"] = pd.to_numeric(df["FrecuenciaInteres"], errors="coerce")

    for col in ["Código", "Signo", "PeriodoInteres", "Cartera", "PlanAmortizacion", "naturaleza", "Tasa"]:
        df[col] = df[col].astype(str).str.strip()

    return df

balance_df = cargar_balance(ruta_balance)

def formato_moneda(x):
    if pd.isna(x):
        return ""
    return f"${x:,.0f}".replace(",", ".")

# Etiquetas más claras
balance_df["TipoPosicion"] = balance_df["naturaleza"].map({"A": "Activo", "P": "Pasivo"}).fillna(balance_df["naturaleza"])

# Resúmenes
saldo_total = balance_df["SaldoCapital"].sum()
n_posiciones = len(balance_df)
n_columnas = balance_df.shape[1]
fecha_min = balance_df["Fecha Inicio"].min()
fecha_max = balance_df["Fecha Vencimiento"].max()

resumen_naturaleza = (
    balance_df.groupby("TipoPosicion", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
)

resumen_cartera = (
    balance_df.groupby("Cartera", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)

resumen_tasa = (
    balance_df.groupby("Tasa", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)

resumen_plan = (
    balance_df.groupby("PlanAmortizacion", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)

diccionario_columnas = pd.DataFrame({
    "Variable": [
        "Código", "PuntosAdicionales", "Signo", "TasaBase", "PeriodoInteres",
        "FrecuenciaInteres", "Fecha Inicio", "Fecha Vencimiento", "Cartera",
        "PlanAmortizacion", "SaldoCapital", "naturaleza", "Tasa"
    ],
    "Descripción": [
        "Identificador de la posición financiera.",
        "Spread o puntos adicionales sobre la tasa de referencia.",
        "Indica si el spread se suma o se resta a la tasa base.",
        "Tasa fija contractual cuando la posición no depende de un índice.",
        "Periodicidad contractual relevante para intereses o repricing (M, T, S, etc.).",
        "Frecuencia numérica asociada al esquema de interés o repricing.",
        "Fecha de inicio de la operación.",
        "Fecha de vencimiento de la operación.",
        "Segmento o cartera a la que pertenece la posición.",
        "Esquema de amortización contractual (por ejemplo, CREG, DSCTO, INTPER).",
        "Saldo de capital sobre el cual se calculan los intereses.",
        "Naturaleza de la posición: A = activo, P = pasivo.",
        "Factor de riesgo o tipo de tasa asociado a la posición (DTF, IBR, IPC, Auvr, etc.)."
    ]
})

st.markdown(f"""
El archivo **`Balance.xlsx`** contiene el detalle de las posiciones del libro bancario en la hoja
**`InfoFacial`**, que es la base principal para proyectar el **Ingreso Neto por Intereses (NII)**.

Cada fila representa una posición individual y combina información de **saldo**, **naturaleza**
(activo o pasivo), **cartera**, **tasa de referencia**, **spread**, **fechas contractuales** y
**plan de amortización**. En conjunto, esta estructura permite modelar cómo evoluciona el margen
financiero ante cambios en tasas e indicadores.

En esta base se observan **{n_posiciones} posiciones** y **{n_columnas} variables**, con un saldo
agregado de **{formato_moneda(saldo_total)}**. El rango temporal de las operaciones va desde
**{fecha_min.date() if pd.notna(fecha_min) else "N/D"}** hasta
**{fecha_max.date() if pd.notna(fecha_max) else "N/D"}**.
""")

with st.expander("Ver descripción detallada del archivo Balance.xlsx", expanded=False):

    tab1, tab2, tab3, tab4 = st.tabs([
        "Resumen general", "Diccionario de variables", "Composición del balance", "Balance completo"
    ])

    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Número de posiciones", f"{n_posiciones}")
        c2.metric("Número de variables", f"{n_columnas}")
        c3.metric("Saldo total", formato_moneda(saldo_total))
        c4.metric("Horizonte observado", f"{fecha_min.date()} a {fecha_max.date()}")

        st.markdown("""
        **Lectura general del archivo**

        - La hoja **InfoFacial** contiene el detalle contractual de las posiciones que componen el balance.
        - Las posiciones se distribuyen entre **activos** y **pasivos**, lo que permite proyectar
          ingresos y gastos por intereses.
        - La base incluye posiciones indexadas a factores como **DTF, IBR, IPC, Auvr y Cuvr**,
          así como posiciones a **tasa fija**.
        - También incorpora la lógica contractual necesaria para la valoración: fechas,
          periodicidad y plan de amortización.
        """)

        st.dataframe(
            resumen_naturaleza.assign(
                SaldoTotal=resumen_naturaleza["SaldoTotal"].map(formato_moneda)
            ),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.markdown("A continuación se presenta una descripción de las variables más relevantes del archivo:")
        st.dataframe(diccionario_columnas, use_container_width=True, hide_index=True)

    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            fig_cartera = px.bar(
                resumen_cartera,
                x="Cartera",
                y="SaldoTotal",
                text="Posiciones",
                title="Saldo total por cartera"
            )
            fig_cartera.update_layout(xaxis_title="", yaxis_title="Saldo total")
            st.plotly_chart(fig_cartera, use_container_width=True)

        with col2:
            fig_tasa = px.bar(
                resumen_tasa,
                x="Tasa",
                y="SaldoTotal",
                text="Posiciones",
                title="Saldo total por factor o tipo de tasa"
            )
            fig_tasa.update_layout(xaxis_title="", yaxis_title="Saldo total")
            st.plotly_chart(fig_tasa, use_container_width=True)

        col3, col4 = st.columns(2)

        with col3:
            fig_nat = px.pie(
                resumen_naturaleza,
                names="TipoPosicion",
                values="SaldoTotal",
                title="Distribución del saldo por naturaleza"
            )
            st.plotly_chart(fig_nat, use_container_width=True)

        with col4:
            fig_plan = px.bar(
                resumen_plan,
                x="PlanAmortizacion",
                y="SaldoTotal",
                text="Posiciones",
                title="Saldo total por plan de amortización"
            )
            fig_plan.update_layout(xaxis_title="", yaxis_title="Saldo total")
            st.plotly_chart(fig_plan, use_container_width=True)

        st.markdown("""
        **Interpretación**

        Esta sección permite identificar cómo se concentra el balance según la **cartera**, la
        **naturaleza de las posiciones**, el **factor de tasa** y el **plan de amortización**.
        Esta descomposición es clave porque el comportamiento del NII depende no solo del tamaño
        de los saldos, sino también de cómo y cuándo reprician las tasas, y de la forma en que
        se amortiza cada operación.
        """)

    with tab4:
        st.markdown("Vista completa de la hoja **InfoFacial** utilizada en el ejercicio:")
        st.dataframe(balance_df, use_container_width=True, height=500)


