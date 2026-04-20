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
del NII bajo escenarios adversos. El codigo del proyecto se encuetra en el github,[Codigo del proyecto](https://github.com/LuisMantilla28/portfolio_streamlit/blob/9ffa8ae40860d2e76bd6cb9e6af6d6c23a72d6e6/Notebooks/Balance_proyectado.ipynb).
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

st.subheader("Metodología")

st.markdown("""
La metodología del proyecto se estructura en cinco etapas principales, con el objetivo de
traducir la información contractual del balance en una medición cuantitativa del
**Earnings at Risk (EaR)** sobre el **Ingreso Neto por Intereses (NII)**.

**1. Preparación y limpieza de datos**

En una primera etapa se realiza la lectura y depuración del archivo **`Balance.xlsx`**
y de la base histórica de factores de riesgo. Esto incluye la estandarización de nombres
de variables, la conversión de fechas, la limpieza de montos y la validación de campos
clave como la naturaleza de la posición, el plan de amortización, el tipo de tasa y la
periodicidad contractual.

**2. Construcción del escenario base**

A partir del último dato histórico disponible antes de la fecha de corte, se construye una
trayectoria base de tasas e indicadores para los siguientes 12 meses. Este escenario sirve
como punto de referencia para estimar el **NII base**, es decir, el margen financiero que
se obtendría si las condiciones de mercado permanecieran constantes en el horizonte de análisis.

**3. Generación de escenarios simulados**

La simulación de los factores de riesgo se realiza a partir de un **modelo estadístico VAR(1)**,
ajustado sobre las series históricas observadas. Este modelo permite capturar la dinámica conjunta
y la dependencia temporal entre variables como **DTF, IBR, IPC, Auvr, Cuvr y TA_Jur**, generando
trayectorias mensuales consistentes para el horizonte de proyección. El procedimiento detallado
de ajuste, validación y simulación del modelo puede consultarse en la sección correspondiente de
series de tiempo.
""")

st.page_link(
    "pages/series_tiempo.py",
    label="Ver procedimiento detallado del modelo VAR(1)",
    icon="📈"
)

st.markdown("""
**4. Valoración mensual del NII**

Con el balance y las trayectorias de tasas, se proyecta el **Ingreso Neto por Intereses**
mes a mes. Para cada posición se consideran su **naturaleza** (activo o pasivo), el
**saldo de capital**, la **tasa de referencia**, el **spread**, la **frecuencia de repricing**,
las **fechas contractuales** y el **plan de amortización**. De esta manera, el cálculo del NII
refleja la evolución del saldo y de la tasa aplicable a lo largo del tiempo.

**5. Cálculo del EaR y descomposición de resultados**

Finalmente, con la distribución de NII obtenida a partir de los escenarios simulados, se
calcula el **EaR** como la diferencia entre el **NII base** y un percentil adverso de la
distribución simulada. Además del resultado agregado, el análisis se descompone por
**factor de riesgo** y por **cartera**, con el fin de identificar las principales fuentes
de exposición y comprender cómo se distribuye el riesgo dentro del balance.
""")

# ============================================================
# SECCIÓN: RESULTADOS
# ============================================================
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.subheader("Resultados")

ruta_resultados = Path("data/modelo_financiero_data")

# ------------------------------------------------------------
# CARGA DE ARCHIVOS
# ------------------------------------------------------------
@st.cache_data
def cargar_resultados(base_path):
    resumen_total = pd.read_csv(base_path / "resumen_total.csv")
    ear_factor = pd.read_csv(base_path / "ear_por_factor.csv")
    ear_cartera = pd.read_csv(base_path / "ear_por_cartera.csv")
    nii_base_mensual = pd.read_csv(base_path / "nii_base_mensual.csv")
    nii_sim_total = pd.read_parquet(base_path / "nii_sim_total.parquet")
    nii_sim_factor = pd.read_parquet(base_path / "nii_sim_factor.parquet")
    nii_sim_cartera = pd.read_parquet(base_path / "nii_sim_cartera.parquet")
    nii_sim_mensual = pd.read_parquet(base_path / "nii_sim_mensual.parquet")
    detalle_base = pd.read_parquet(base_path / "detalle_base.parquet")
    return (
        resumen_total,
        ear_factor,
        ear_cartera,
        nii_base_mensual,
        nii_sim_total,
        nii_sim_factor,
        nii_sim_cartera,
        nii_sim_mensual,
        detalle_base,
    )

(
    resumen_total,
    ear_factor,
    ear_cartera,
    nii_base_mensual,
    nii_sim_total,
    nii_sim_factor,
    nii_sim_cartera,
    nii_sim_mensual,
    detalle_base,
) = cargar_resultados(ruta_resultados)

# ------------------------------------------------------------
# FUNCIONES AUXILIARES
# ------------------------------------------------------------
def valor_resumen(nombre):
    fila = resumen_total.loc[resumen_total["Métrica"] == nombre, "Valor"]
    if len(fila) == 0:
        return np.nan
    try:
        return float(fila.iloc[0])
    except:
        return fila.iloc[0]

def fmt_cop(x):
    if pd.isna(x):
        return "N/D"
    return f"${x:,.0f}".replace(",", ".")

def fmt_mm(x):
    if pd.isna(x):
        return "N/D"
    return f"{x/1e6:,.2f} MM".replace(",", ".")

def fmt_pct(x):
    if pd.isna(x):
        return "N/D"
    return f"{100*x:.2f}%"

# Valores principales
nii_base = valor_resumen("NII base")
media_nii = valor_resumen("Media NII simulado")
mediana_nii = valor_resumen("Mediana NII simulado")
p1_nii = valor_resumen("Percentil 1% NII")
p5_nii = valor_resumen("Percentil 5% NII")
ear_99 = valor_resumen("EaR 99%")
ear_95 = valor_resumen("EaR 95%")
n_sim = valor_resumen("Número de simulaciones")
fecha_corte = valor_resumen("Fecha de corte")
horizonte = valor_resumen("Horizonte (meses)")

# Tablas ordenadas
ear_factor = ear_factor.sort_values("EaR 99%", ascending=False).reset_index(drop=True)
ear_cartera = ear_cartera.sort_values("EaR 99%", ascending=False).reset_index(drop=True)

factor_top = ear_factor.iloc[0]["Factor"] if len(ear_factor) else "N/D"
cartera_top = ear_cartera.iloc[0]["Cartera"] if len(ear_cartera) else "N/D"

# ------------------------------------------------------------
# TEXTO DE APERTURA
# ------------------------------------------------------------
st.markdown(f"""
En esta sección se presentan los resultados de la proyección del **Ingreso Neto por Intereses (NII)**
y de la estimación del **Earnings at Risk (EaR)** a un horizonte de **{int(horizonte)} meses**,
utilizando **{int(n_sim)} escenarios simulados** y una fecha de corte de **{fecha_corte}**.

El objetivo es mostrar no solo el resultado agregado del portafolio, sino también su descomposición
por **factor de riesgo** y por **cartera**, con el fin de identificar las principales fuentes
de sensibilidad del balance.
""")

# ------------------------------------------------------------
# RESUMEN EJECUTIVO
# ------------------------------------------------------------
st.markdown("### Resumen ejecutivo")

c1, c2, c3, c4 = st.columns(4)
c1.metric("NII base", fmt_mm(nii_base))
c2.metric("EaR 99%", fmt_mm(ear_99))
c3.metric("Percentil 1% del NII", fmt_mm(p1_nii))
c4.metric("Media del NII simulado", fmt_mm(media_nii))

signo_base = "negativo" if nii_base < 0 else "positivo"
mejora_media = "supera" if media_nii > nii_base else "se ubica por debajo de"

st.markdown(f"""
- El **NII base** del portafolio es **{signo_base}**, lo que sugiere que bajo el escenario de referencia
  el margen financiero presenta presión por el lado del fondeo.
- El **EaR al 99%** asciende a **{fmt_mm(ear_99)}**, cuantificando el deterioro potencial del NII
  en escenarios extremos adversos.
- En promedio, el NII simulado **{mejora_media}** el valor base, lo que indica que la distribución
  de escenarios no se concentra exclusivamente en trayectorias adversas.
- La principal fuente de riesgo se concentra en **{cartera_top}** a nivel de cartera y en **{factor_top}**
  a nivel de factor.
""")

# ------------------------------------------------------------
# TABS DE RESULTADOS
# ------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resultado total",
    "EaR por factor",
    "EaR por cartera",
    "Trayectoria mensual del NII",
    "Detalle de posiciones"
])

# ============================================================
# TAB 1: RESULTADO TOTAL
# ============================================================
with tab1:
    st.markdown("#### Distribución del NII simulado")

    fig_hist = px.histogram(
        nii_sim_total,
        x="NII",
        nbins=40,
        opacity=0.8,
        labels={"NII": "NII (COP)"},
        title="Distribución del NII simulado"
    )

    fig_hist.add_vline(
        x=nii_base,
        line_width=2,
        line_dash="dash",
        annotation_text="NII base",
        annotation_position="top right"
    )
    fig_hist.add_vline(
        x=p1_nii,
        line_width=2,
        line_dash="dash",
        annotation_text="Percentil 1%",
        annotation_position="top left"
    )
    fig_hist.add_vline(
        x=p5_nii,
        line_width=2,
        line_dash="dot",
        annotation_text="Percentil 5%",
        annotation_position="top left"
    )

    fig_hist.update_layout(
        xaxis_title="NII (COP)",
        yaxis_title="Frecuencia",
        bargap=0.05
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("#### Tabla resumen")
    tabla_total = resumen_total.copy()
    tabla_total["Valor"] = tabla_total["Valor"].astype(str)
    st.dataframe(tabla_total, use_container_width=True, hide_index=True)

    st.markdown(f"""
    **Lectura del resultado total**

    El escenario base arroja un **NII de {fmt_cop(nii_base)}**, mientras que el percentil 1% de la
    distribución simulada se ubica en **{fmt_cop(p1_nii)}**. La diferencia entre ambos valores da
    lugar a un **EaR al 99% de {fmt_cop(ear_99)}**, que resume la pérdida potencial del margen
    financiero ante movimientos adversos de tasas e indicadores.
    """)

# ============================================================
# TAB 2: EAR POR FACTOR
# ============================================================
with tab2:
    st.markdown("#### Descomposición del riesgo por factor")

    fig_factor = px.bar(
        ear_factor,
        x="Factor",
        y="EaR 99%",
        text="EaR 99%",
        title="EaR al 99% por factor de riesgo",
        hover_data={
            "NII base": ":,.0f",
            "Media": ":,.0f",
            "Mediana": ":,.0f",
            "Percentil 1%": ":,.0f",
            "Percentil 5%": ":,.0f",
            "EaR 99%": ":,.0f",
            "EaR 95%": ":,.0f",
        }
    )
    fig_factor.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
    fig_factor.update_layout(
        xaxis_title="Factor",
        yaxis_title="EaR 99% (COP)"
    )
    st.plotly_chart(fig_factor, use_container_width=True)

    st.dataframe(ear_factor, use_container_width=True, hide_index=True)

    st.markdown(f"""
    El análisis por factor muestra que la mayor contribución al riesgo proviene de **{factor_top}**,
    seguido por los factores que presentan mayor sensibilidad sobre la estructura del balance. En cambio,
    las exposiciones a **tasa fija** tienden a mostrar una contribución marginal al EaR, lo que resulta
    consistente con su menor dependencia de los escenarios simulados.
    """)

# ============================================================
# TAB 3: EAR POR CARTERA
# ============================================================
with tab3:
    st.markdown("#### Descomposición del riesgo por cartera")

    fig_cartera = px.bar(
        ear_cartera,
        x="Cartera",
        y="EaR 99%",
        text="EaR 99%",
        title="EaR al 99% por cartera",
        hover_data={
            "NII base": ":,.0f",
            "Media": ":,.0f",
            "Mediana": ":,.0f",
            "Percentil 1%": ":,.0f",
            "Percentil 5%": ":,.0f",
            "EaR 99%": ":,.0f",
            "EaR 95%": ":,.0f",
        }
    )
    fig_cartera.update_traces(texttemplate="%{y:,.0f}", textposition="outside")
    fig_cartera.update_layout(
        xaxis_title="Cartera",
        yaxis_title="EaR 99% (COP)",
        xaxis_tickangle=-25
    )
    st.plotly_chart(fig_cartera, use_container_width=True)

    st.dataframe(ear_cartera, use_container_width=True, hide_index=True)

    st.markdown(f"""
  La descomposición por cartera evidencia una **fuerte concentración del riesgo en {cartera_top}**,
que explica la mayor parte del **EaR** del portafolio. Este resultado es consistente con la
estructura del balance, donde las posiciones pasivas de mayor tamaño concentran buena parte de la
sensibilidad al **repricing** y al **costo financiero**. En contraste, el resto de carteras muestra
una incidencia mucho menor sobre el riesgo agregado; incluso en el caso de **CDT**, el valor
ligeramente negativo del EaR refleja una exposición prácticamente nula, más que una fuente material
de deterioro del margen financiero. En conjunto, los resultados indican que el riesgo no está
distribuido de forma homogénea, sino claramente concentrado en el libro pasivo.
    """)

# ============================================================
# TAB 4: TRAYECTORIA MENSUAL DEL NII
# ============================================================
with tab4:
    st.markdown("#### Perfil mensual del NII")

    cols_meses = [c for c in nii_sim_mensual.columns if c.startswith("NII_mes_")]
    tray = nii_sim_mensual[cols_meses].copy()

    meses = np.arange(1, len(cols_meses) + 1)

    media_m = tray.mean(axis=0).values
    mediana_m = tray.median(axis=0).values
    p5_m = tray.quantile(0.05, axis=0).values
    p95_m = tray.quantile(0.95, axis=0).values
    p1_m = tray.quantile(0.01, axis=0).values
    p99_m = tray.quantile(0.99, axis=0).values
    nii_base_m = nii_base_mensual["NII_mensual_base"].values

    fig_tray = go.Figure()

    fig_tray.add_trace(go.Scatter(
        x=np.concatenate([meses, meses[::-1]]),
        y=np.concatenate([p95_m, p5_m[::-1]]),
        fill="toself",
        name="Banda 5%-95%",
        line=dict(width=0),
        opacity=0.25
    ))

    fig_tray.add_trace(go.Scatter(
        x=np.concatenate([meses, meses[::-1]]),
        y=np.concatenate([p99_m, p1_m[::-1]]),
        fill="toself",
        name="Banda 1%-99%",
        line=dict(width=0),
        opacity=0.12
    ))

    fig_tray.add_trace(go.Scatter(
        x=meses, y=media_m,
        mode="lines+markers",
        name="Media simulada"
    ))

    fig_tray.add_trace(go.Scatter(
        x=meses, y=mediana_m,
        mode="lines",
        line=dict(dash="dash"),
        name="Mediana simulada"
    ))

    fig_tray.add_trace(go.Scatter(
        x=meses, y=nii_base_m,
        mode="lines+markers",
        name="NII base mensual",
        line=dict(width=3)
    ))

    fig_tray.update_layout(
        title="Trayectoria mensual del NII",
        xaxis_title="Mes",
        yaxis_title="NII mensual (COP)",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1)
    )

    st.plotly_chart(fig_tray, use_container_width=True)



    st.markdown("""
    Se observa un **cambio marcado entre el mes 6 y el mes 7** en la trayectoria mensual del NII. 
Este comportamiento se explica principalmente por el **repricing semestral** de algunas posiciones 
de la **Cartera Pasiva** indexadas al **IPC**, en particular las posiciones **023CCFF** y **024ZZUU**. 
Ambas tienen **`PeriodoInteres = S`**, por lo que en el modelo la tasa aplicada se mantiene fija 
durante los primeros seis meses y se actualiza al inicio del séptimo mes con el nuevo valor del 
factor correspondiente. Dado que se trata de **pasivos** y además de posiciones con saldos elevados, 
cualquier cambio en la tasa utilizada a partir del mes 7 tiene un impacto visible sobre el gasto por 
intereses y, por consiguiente, sobre el **Ingreso Neto por Intereses (NII)**. En este caso, el salto 
observado no corresponde a un error numérico, sino a un **efecto estructural del esquema contractual 
de repricing** de estas obligaciones.
    """)

# ============================================================
# TAB 5: DETALLE DE POSICIONES
# ============================================================
with tab5:
    st.markdown("#### Posiciones con mayor contribución al NII base")

    detalle_base_orden = detalle_base.sort_values("NII", ascending=False).reset_index(drop=True)

    col_pos, col_neg = st.columns(2)

    with col_pos:
        st.markdown("**Top 10 posiciones con mayor aporte positivo al NII base**")
        st.dataframe(
            detalle_base_orden.head(10),
            use_container_width=True,
            hide_index=True
        )

    with col_neg:
        st.markdown("**Top 10 posiciones con mayor aporte negativo al NII base**")
        st.dataframe(
            detalle_base_orden.sort_values("NII", ascending=True).head(10),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("""
Estas tablas permiten identificar con mayor precisión **qué posiciones explican el nivel y el signo del NII base**. 
Por el lado positivo, los mayores aportes provienen principalmente de posiciones **activas** de 
**Adquisición de Vivienda** y **Cartera Ordinaria**, especialmente aquellas asociadas a **tasa fija** 
y a **DTF**, que generan una contribución importante al ingreso financiero del portafolio. En contraste, 
la presión negativa sobre el margen se concentra en posiciones **pasivas** de la **Cartera Pasiva**, 
en particular las indexadas a **IPC** e **IBR**. Destacan especialmente las posiciones **023CCFF** y 
**024ZZUU**, ambas clasificadas como pasivos IPC bajo plan **CREG**, cuyos saldos elevados hacen que 
su costo financiero tenga un efecto material sobre el NII. En conjunto, las tablas muestran que el 
resultado base del portafolio surge del contraste entre un grupo relativamente reducido de posiciones 
activas con alta capacidad de generación de ingresos y un bloque de posiciones pasivas que concentra 
la mayor parte de la presión sobre el margen financiero.
    """)

st.subheader("Conclusiones")

st.markdown("""
El ejercicio permitió construir una medición consistente del **riesgo de tasa de interés en el libro bancario**
a partir de la proyección del **Ingreso Neto por Intereses (NII)** y del cálculo del **Earnings at Risk (EaR)**.
En términos generales, los resultados muestran que el balance presenta una **alta sensibilidad a movimientos
en tasas e indicadores**, y que dicha sensibilidad no se distribuye de manera homogénea, sino que se concentra
en un conjunto relativamente reducido de exposiciones.

En particular, la descomposición por cartera evidencia que el riesgo se encuentra **fuertemente concentrado en
el libro pasivo**, especialmente en aquellas posiciones de mayor tamaño y mayor sensibilidad al **repricing**.
Esto es consistente con la composición observada en el balance, donde una parte importante del saldo se encuentra
asociada a obligaciones cuyo costo financiero depende de factores como **IPC, IBR** y **TA_Jur**. Como resultado,
el comportamiento del margen financiero está determinado en buena medida por la dinámica de estas tasas.

A nivel metodológico, el uso de un esquema que combina **simulación de factores de riesgo mediante un modelo VAR(1)**,
proyección mensual del NII y descomposición por **factor** y **cartera** permitió obtener una visión más rica
que la que ofrece una medida agregada aislada. No solo fue posible estimar el **EaR total**, sino también
identificar con claridad cuáles son las principales fuentes de deterioro potencial del margen financiero y
cómo se transmite ese riesgo a lo largo del horizonte de proyección.

Adicionalmente, el análisis mensual del NII permitió detectar comportamientos estructurales relevantes del balance,
como el salto observado entre el mes 6 y el mes 7, explicado por el **repricing semestral** de posiciones pasivas
indexadas al **IPC**. Este tipo de hallazgos muestra que la dinámica del riesgo no depende únicamente del nivel
de las tasas, sino también de la **estructura contractual** de las posiciones, incluyendo su periodicidad de ajuste
y su esquema de amortización.

En conjunto, el proyecto muestra que una aproximación cuantitativa bien estructurada permite transformar la
información contractual del balance en una herramienta útil para la gestión del riesgo financiero. Aunque se trata
de un **caso de estudio** y no de un motor regulatorio o productivo de ALM, el ejercicio ilustra de forma clara
cómo integrar **datos, modelación estadística y valoración financiera** para analizar la vulnerabilidad del margen
de interés ante escenarios adversos de mercado.
""")



