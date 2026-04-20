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




ruta_balance = Path("data/modelo_financiero_data/Balance.xlsx")

# ------------------------------------------------------------
# Funciones auxiliares
# ------------------------------------------------------------
def limpiar_monto(valor):
    """
    Limpia montos que pueden venir como número o como texto con
    formato colombiano/internacional.
    """
    if pd.isna(valor):
        return np.nan

    # Si ya es numérico
    if isinstance(valor, (int, float, np.integer, np.floating)):
        return float(valor)

    s = str(valor).strip()

    if s == "":
        return np.nan

    # Caso tipo colombiano: 20.673.470,00
    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")

    # Caso tipo internacional: 1,734,068,854,391.51
    elif "," in s and "." not in s:
        s = s.replace(",", "")

    # Caso entero con puntos de miles: 20.673.470
    elif "." in s and s.count(".") > 1:
        s = s.replace(".", "")

    try:
        return float(s)
    except:
        return np.nan


def formato_moneda(x):
    if pd.isna(x):
        return ""
    return f"${x:,.0f}".replace(",", ".")


def formato_billones(x):
    if pd.isna(x):
        return ""
    return f"{x:,.2f} B".replace(",", ".")


@st.cache_data
def cargar_balance(ruta):
    df = pd.read_excel(ruta, sheet_name="InfoFacial").copy()
    df.columns = [c.strip() for c in df.columns]

    # Fechas
    df["Fecha Inicio"] = pd.to_datetime(df["Fecha Inicio"], errors="coerce")
    df["Fecha Vencimiento"] = pd.to_datetime(df["Fecha Vencimiento"], errors="coerce")

    # Variables numéricas
    df["SaldoCapital"] = df["SaldoCapital"].apply(limpiar_monto)
    df["PuntosAdicionales"] = pd.to_numeric(df["PuntosAdicionales"], errors="coerce")
    df["FrecuenciaInteres"] = pd.to_numeric(df["FrecuenciaInteres"], errors="coerce")
    df["TasaBase"] = pd.to_numeric(df["TasaBase"], errors="coerce")

    # Strings
    for col in [
        "Código", "Signo", "PeriodoInteres", "Cartera",
        "PlanAmortizacion", "naturaleza", "Tasa"
    ]:
        df[col] = df[col].astype(str).str.strip()

    return df


balance_df = cargar_balance(ruta_balance)

# Etiquetas más claras
balance_df["TipoPosicion"] = (
    balance_df["naturaleza"]
    .map({"A": "Activo", "P": "Pasivo"})
    .fillna(balance_df["naturaleza"])
)

# ------------------------------------------------------------
# Resúmenes
# ------------------------------------------------------------
saldo_total = balance_df["SaldoCapital"].sum()
n_posiciones = len(balance_df)
n_columnas = balance_df.shape[1]
fecha_min = balance_df["Fecha Inicio"].min()
fecha_max = balance_df["Fecha Vencimiento"].max()

BILLON = 1e9  # miles de millones de COP

resumen_naturaleza = (
    balance_df.groupby("TipoPosicion", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
)
resumen_naturaleza["SaldoBillones"] = resumen_naturaleza["SaldoTotal"] / BILLON

resumen_cartera = (
    balance_df.groupby("Cartera", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)
resumen_cartera["SaldoBillones"] = resumen_cartera["SaldoTotal"] / BILLON

resumen_tasa = (
    balance_df.groupby("Tasa", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)
resumen_tasa["SaldoBillones"] = resumen_tasa["SaldoTotal"] / BILLON

resumen_plan = (
    balance_df.groupby("PlanAmortizacion", dropna=False)
    .agg(
        Posiciones=("Código", "count"),
        SaldoTotal=("SaldoCapital", "sum")
    )
    .reset_index()
    .sort_values("SaldoTotal", ascending=False)
)
resumen_plan["SaldoBillones"] = resumen_plan["SaldoTotal"] / BILLON

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
        "Tasa contractual cuando la posición está a tasa fija.",
        "Periodicidad contractual relevante para intereses o repricing (M, T, S, D, etc.).",
        "Frecuencia numérica asociada al esquema de interés o repricing.",
        "Fecha de inicio de la operación.",
        "Fecha de vencimiento de la operación.",
        "Cartera o segmento al que pertenece la posición.",
        "Esquema de amortización contractual.",
        "Saldo de capital sobre el cual se calculan los intereses.",
        "Naturaleza de la posición: A = activo, P = pasivo.",
        "Factor de riesgo o tipo de tasa asociado a la posición."
    ]
})

planes_amortizacion = pd.DataFrame({
    "Plan": ["CREG", "DSCTO", "INTPER"],
    "Descripción breve": [
        "Cuota regular: en cada periodo se paga una cuota constante compuesta por capital e intereses.",
        "Descuento: capital e intereses se pagan al vencimiento de la operación.",
        "Interés periódico: se pagan intereses periódicamente sobre el capital, y el capital se cancela al final."
    ]
})

# ------------------------------------------------------------
# Texto principal
# ------------------------------------------------------------
st.markdown(f"""
El archivo [**`Balance.xlsx`**](https://github.com/LuisMantilla28/portfolio_streamlit/blob/c1730a022dfcd4685d56944d64892ed1fa375c38/data/modelo_financiero_data/Balance.xlsx)
contiene el detalle de las posiciones del libro bancario en la hoja **`InfoFacial`**,
que constituye la base principal para proyectar el **Ingreso Neto por Intereses (NII)**.

Cada fila representa una posición individual e integra información de **saldo**, **naturaleza**
(activo o pasivo), **cartera**, **tasa de referencia**, **spread**, **fechas contractuales**
y **plan de amortización**. En conjunto, esta estructura permite modelar cómo evoluciona
el margen financiero ante cambios en tasas e indicadores.

En esta base se observan **{n_posiciones} posiciones** y **{n_columnas} variables**,
con un saldo agregado de **{formato_moneda(saldo_total)}**. El rango temporal de las operaciones
va desde **{fecha_min.date() if pd.notna(fecha_min) else "N/D"}**
hasta **{fecha_max.date() if pd.notna(fecha_max) else "N/D"}**.
""")

# ------------------------------------------------------------
# Expander principal
# ------------------------------------------------------------
with st.expander("Ver descripción detallada del archivo Balance.xlsx", expanded=False):

    tab1, tab2, tab3, tab4 = st.tabs([
        "Resumen general",
        "Diccionario de variables",
        "Composición del balance",
        "Balance completo"
    ])

    # --------------------------------------------------------
    # TAB 1: RESUMEN GENERAL
    # --------------------------------------------------------
    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.metric("Número de posiciones", f"{n_posiciones}")
        c2.metric("Número de variables", f"{n_columnas}")
        c3.metric("Horizonte observado", f"{fecha_min.date().year} a {fecha_max.date().year}")


        st.markdown("""
        **Lectura general del archivo**

        - La hoja **InfoFacial** contiene el detalle contractual de las posiciones que componen el balance.
        - Las posiciones se distribuyen entre **activos** y **pasivos**, lo que permite proyectar ingresos y gastos por intereses.
        - La base incluye posiciones indexadas a factores como **DTF, IBR, IPC, Auvr, Cuvr y TA_Jur**, así como posiciones a **tasa fija**.
        - También incorpora la lógica contractual necesaria para la valoración: fechas, periodicidad y plan de amortización.
        """)

        tabla_nat = resumen_naturaleza.copy()
        tabla_nat["SaldoTotal"] = tabla_nat["SaldoTotal"].map(formato_moneda)
        tabla_nat["SaldoBillones"] = tabla_nat["SaldoBillones"].map(formato_billones)

        st.dataframe(
            tabla_nat,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # TAB 2: DICCIONARIO + PLANES
    # --------------------------------------------------------
    with tab2:
        st.markdown("A continuación se presenta una descripción de las variables más relevantes del archivo:")
        st.dataframe(diccionario_columnas, use_container_width=True, hide_index=True)

        st.markdown("### Planes de amortización")
        st.markdown("""
        Los planes de amortización indican **cómo se distribuyen en el tiempo los pagos de capital e intereses**.
        Esta información es importante porque afecta directamente la trayectoria del saldo y, por tanto, el comportamiento del NII.
        """)

        st.dataframe(planes_amortizacion, use_container_width=True, hide_index=True)

    # --------------------------------------------------------
    # TAB 3: COMPOSICIÓN DEL BALANCE
    # --------------------------------------------------------
    with tab3:
        col1, col2 = st.columns(2)

        with col1:
            fig_cartera = px.bar(
                resumen_cartera,
                x="Cartera",
                y="SaldoBillones",
                text="Posiciones",
                title="Saldo total por cartera",
                hover_data={
                    "SaldoTotal": ":,.0f",
                    "SaldoBillones": ":.2f",
                    "Posiciones": True
                }
            )
            fig_cartera.update_traces(texttemplate="n=%{text}", textposition="outside")
            fig_cartera.update_layout(
                xaxis_title="",
                yaxis_title="Saldo total (billones de COP)",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_cartera, use_container_width=True)

        with col2:
            fig_tasa = px.bar(
                resumen_tasa,
                x="Tasa",
                y="SaldoBillones",
                text="Posiciones",
                title="Saldo total por factor o tipo de tasa",
                hover_data={
                    "SaldoTotal": ":,.0f",
                    "SaldoBillones": ":.2f",
                    "Posiciones": True
                }
            )
            fig_tasa.update_traces(texttemplate="n=%{text}", textposition="outside")
            fig_tasa.update_layout(
                xaxis_title="",
                yaxis_title="Saldo total (billones de COP)"
            )
            st.plotly_chart(fig_tasa, use_container_width=True)

        col3, col4 = st.columns(2)

       

        with col3:
            fig_plan = px.bar(
                resumen_plan,
                x="PlanAmortizacion",
                y="SaldoBillones",
                text="Posiciones",
                title="Saldo total por plan de amortización",
                hover_data={
                    "SaldoTotal": ":,.0f",
                    "SaldoBillones": ":.2f",
                    "Posiciones": True
                }
            )
            fig_plan.update_traces(texttemplate="n=%{text}", textposition="outside")
            fig_plan.update_layout(
                xaxis_title="",
                yaxis_title="Saldo total (billones de COP)"
            )
            st.plotly_chart(fig_plan, use_container_width=True)

        st.markdown("""
        **Interpretación**

        Esta sección permite identificar cómo se concentra el balance según la **cartera**,
        la **naturaleza de las posiciones**, el **factor de tasa** y el **plan de amortización**.
        Esta descomposición es clave porque el comportamiento del NII depende no solo del tamaño
        de los saldos, sino también de **cómo y cuándo reprician las tasas**, y de la forma en que
        se **amortiza cada operación**.

        **Nota:** la etiqueta `n=` sobre cada barra representa el **número de posiciones** dentro de cada categoría.
        """)

        # ----------------------------------------------------
        # Vista adicional sin la cartera/factor dominante
        # ----------------------------------------------------
        st.markdown("### Vista complementaria sin la exposición dominante")
        st.markdown("""
        Dado que algunas categorías concentran una porción muy alta del saldo total, la siguiente vista excluye
        la categoría dominante para facilitar la lectura del resto del balance.
        """)

        col5, col6 = st.columns(2)

        with col5:
            cartera_top = resumen_cartera.iloc[0]["Cartera"]
            resumen_cartera_sin_top = resumen_cartera[resumen_cartera["Cartera"] != cartera_top].copy()

            fig_cartera_2 = px.bar(
                resumen_cartera_sin_top,
                x="Cartera",
                y="SaldoBillones",
                text="Posiciones",
                title=f"Saldo por cartera (excluyendo {cartera_top})",
                hover_data={
                    "SaldoTotal": ":,.0f",
                    "SaldoBillones": ":.4f",
                    "Posiciones": True
                }
            )
            fig_cartera_2.update_traces(texttemplate="n=%{text}", textposition="outside")
            fig_cartera_2.update_layout(
                xaxis_title="",
                yaxis_title="Saldo total (billones de COP)",
                xaxis_tickangle=-30
            )
            st.plotly_chart(fig_cartera_2, use_container_width=True)

        with col6:
            tasa_top = resumen_tasa.iloc[0]["Tasa"]
            resumen_tasa_sin_top = resumen_tasa[resumen_tasa["Tasa"] != tasa_top].copy()

            fig_tasa_2 = px.bar(
                resumen_tasa_sin_top,
                x="Tasa",
                y="SaldoBillones",
                text="Posiciones",
                title=f"Saldo por factor (excluyendo {tasa_top})",
                hover_data={
                    "SaldoTotal": ":,.0f",
                    "SaldoBillones": ":.4f",
                    "Posiciones": True
                }
            )
            fig_tasa_2.update_traces(texttemplate="n=%{text}", textposition="outside")
            fig_tasa_2.update_layout(
                xaxis_title="",
                yaxis_title="Saldo total (billones de COP)"
            )
            st.plotly_chart(fig_tasa_2, use_container_width=True)
        st.markdown("""
        En términos estructurales, el balance presenta una **alta concentración en posiciones pasivas**, 
        explicada principalmente por la **Cuenta de Ahorro Jurídica**, que domina tanto la distribución por 
        cartera como por factor de tasa a través de **TA_Jur**. Esta concentración también se refleja en la 
        composición por naturaleza, donde los pasivos representan prácticamente la totalidad del saldo total. 
        Adicionalmente, el plan de amortización **INTPER** concentra la mayor parte del balance, lo que sugiere 
        que una fracción importante de las posiciones mantiene el capital hasta el vencimiento y solo genera 
        pagos periódicos de intereses. En conjunto, esta estructura anticipa una sensibilidad relevante del 
        margen financiero frente a movimientos en tasas asociadas al fondeo, y ayuda a explicar por qué el 
        riesgo del balance se encuentra fuertemente concentrado en el libro pasivo.
        """)

    # --------------------------------------------------------
    # TAB 4: BALANCE COMPLETO
    # --------------------------------------------------------
    with tab4:
        st.markdown("Vista completa de la hoja **InfoFacial** utilizada en el ejercicio:")

        vista_balance = balance_df.copy()
        vista_balance["SaldoCapital"] = vista_balance["SaldoCapital"].map(formato_moneda)

        st.dataframe(vista_balance, use_container_width=True, height=500)

st.subheader("Supuestos clave")

st.markdown("""
La construcción del ejercicio de **Earnings at Risk (EaR)** requiere establecer algunos supuestos
metodológicos para traducir la información contractual del balance en trayectorias mensuales de
**Ingreso Neto por Intereses (NII)**. En este proyecto se adoptan los siguientes:

- El horizonte de análisis es de **12 meses**, con fecha de corte **26 de abril de 2020**.

- El universo de trabajo corresponde a las posiciones de la hoja **`InfoFacial`**, incluyendo
exposiciones asociadas a **`TA_Jur`**. Por ello, la composición del balance utilizada aquí puede
diferir de otros resúmenes agregados del archivo original.

- El **NII** se calcula sobre **base devengada mensual**, es decir, los intereses se reconocen
mes a mes y no únicamente cuando ocurre el pago contractual.

- Para las posiciones a **tasa variable**, la tasa aplicable en cada escenario se construye a
partir de la trayectoria simulada del factor de riesgo correspondiente y del **spread** indicado
en el balance.

- En el caso de la **DTF**, el spread se suma o resta primero sobre la **tasa trimestral
anticipada**, y posteriormente se convierte a tasa efectiva anual para la valoración.

- La variable **`PeriodoInteres`** y, cuando aplica, **`FrecuenciaInteres`**, se interpretan
como guía para la frecuencia de **repricing o reset** de las tasas. Dentro de cada bloque de
repricing, la tasa se mantiene constante.

- Las posiciones se valorizan respetando su **fecha de inicio**, **fecha de vencimiento** y
**plan de amortización**, de modo que solo generan intereses durante el periodo en que se
encuentran activas.

- Para posiciones con plan **CREG**, el saldo se reduce gradualmente mediante una aproximación
de amortización mensual; para **INTPER** y **DSCTO**, el capital se mantiene hasta el vencimiento,
de acuerdo con la lógica contractual de cada producto.

- El signo del NII depende de la **naturaleza** de la posición: los **activos** generan ingresos
por intereses y los **pasivos** generan gastos por intereses.

- El análisis se desarrolla como un **caso de estudio cuantitativo**, por lo que los resultados
deben interpretarse como una aproximación metodológicamente consistente al riesgo de tasa, y no
como un motor regulatorio o productivo de ALM.
""")




