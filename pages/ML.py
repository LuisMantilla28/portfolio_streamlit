import streamlit as st
import navigation
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

navigation.show()

st.set_page_config(page_title="ML - Default Crediticio", page_icon="🤖", layout="wide")

# ---------------------------------------------------------------
# RUTAS
# ---------------------------------------------------------------
BASE = Path("data/modelo_ml")

@st.cache_data
def cargar_datos():
    resumen_prep    = pd.read_csv(BASE / "resumen_preprocesamiento.csv")
    resumen_modelos = pd.read_csv(BASE / "resumen_modelos.csv")
    df_umbrales     = pd.read_csv(BASE / "df_umbrales.csv")
    importancia     = pd.read_csv(BASE / "importancia_shap.csv")
    val_pred        = pd.read_parquet(BASE / "val_predictions.parquet")
    roc_lr          = pd.read_csv(BASE / "roc_lr.csv")
    roc_xgb         = pd.read_csv(BASE / "roc_xgb.csv")
    pr_lr           = pd.read_csv(BASE / "pr_lr.csv")
    pr_xgb          = pd.read_csv(BASE / "pr_xgb.csv")
    shap_alto       = pd.read_csv(BASE / "shap_alto_riesgo.csv")
    shap_bajo       = pd.read_csv(BASE / "shap_bajo_riesgo.csv")
    shap_ambiguo    = pd.read_csv(BASE / "shap_caso_ambiguo.csv")
    return (resumen_prep, resumen_modelos, df_umbrales, importancia,
            val_pred, roc_lr, roc_xgb, pr_lr, pr_xgb,
            shap_alto, shap_bajo, shap_ambiguo)

(resumen_prep, resumen_modelos, df_umbrales, importancia,
 val_pred, roc_lr, roc_xgb, pr_lr, pr_xgb,
 shap_alto, shap_bajo, shap_ambiguo) = cargar_datos()

auc_lr  = resumen_modelos.loc[resumen_modelos["Modelo"] == "Regresión Logística", "AUC-ROC"].values[0]
auc_xgb = resumen_modelos.loc[resumen_modelos["Modelo"] == "XGBoost", "AUC-ROC"].values[0]

# ===============================================================
# 1. INTRODUCCIÓN
# ===============================================================
st.title("Predicción de Default Crediticio con Machine Learning")

st.markdown("""
Este proyecto desarrolla un modelo de **scoring crediticio** para predecir la probabilidad
de que un cliente entre en mora grave (90+ días de retraso) en los próximos dos años.

A partir del dataset público [Give Me Some Credit](https://www.kaggle.com/competitions/GiveMeSomeCredit/overview)
de Kaggle, con **150,000 clientes** y **11 variables financieras**, se construye un pipeline
completo que va desde la limpieza de datos hasta la interpretabilidad del modelo con **SHAP values**.

El proyecto está orientado a mostrar cómo el machine learning puede integrarse al lenguaje
de riesgo crediticio: no solo predecir quién va a defaultear, sino **explicar por qué**,
variable por variable, cliente por cliente.
""")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Clientes", "150,000")
col2.metric("Tasa de default", "6.7%")
col3.metric("AUC Logística", f"{auc_lr:.3f}")
col4.metric("AUC XGBoost", f"{auc_xgb:.3f}")

st.markdown("---")

# ===============================================================
# 2. DATOS Y PREPROCESAMIENTO
# ===============================================================
st.header("1. Datos y preprocesamiento")

st.markdown("""
El dataset presenta varios problemas comunes en datos financieros reales:
valores centinela, outliers extremos, nulos en variables críticas y fuerte
desbalance de clases. La siguiente tabla resume las decisiones tomadas y
su justificación.
""")

st.dataframe(resumen_prep, use_container_width=True, hide_index=True)

st.markdown("""
Adicionalmente se construyeron tres variables nuevas a partir de la información disponible:
**mora_acumulada** (suma de todos los eventos de mora), **tiene_mora_previa** (flag binario)
e **ingreso_por_dependiente** (ingreso ajustado por carga familiar). Las variables con
distribución muy sesgada — `debt_ratio`, `monthly_income` e `ingreso_por_dependiente` —
se transformaron con **log1p** para mejorar el comportamiento de la Regresión Logística.
""")

st.markdown("---")

# ===============================================================
# 3. MODELACIÓN
# ===============================================================
st.header("2. Modelación")

st.markdown("""
Se compararon dos modelos con una lógica de complejidad creciente. Ambos incorporan
una estrategia explícita para el desbalance de clases, dado que los defaults ( dejó de pagar su deuda por 90 días o más) representan
solo el 6.7% de la muestra.
""")

st.dataframe(resumen_modelos, use_container_width=True, hide_index=True)

st.markdown("---")

# ---------------------------------------------------------------
# CURVAS ROC Y PRECISION-RECALL
# ---------------------------------------------------------------
st.subheader("Evaluación del poder discriminante")

st.markdown("""
Para evaluar los modelos se usan dos curvas complementarias. La **Curva ROC** mide
la capacidad general de discriminación: qué tan bien separa el modelo a los clientes
que van a defaultear de los que no. El área bajo esta curva (**AUC-ROC**) resume ese
poder en un solo número — 1.0 sería perfecto, 0.5 sería equivalente a lanzar una moneda.

La **Curva Precision-Recall** es más informativa en contextos de desbalance como este.
Responde una pregunta más exigente: de los clientes que el modelo marca como riesgo,
¿cuántos realmente van a defaultear? Esta curva cae más rápido porque detectar defaults
con alta precisión es difícil cuando son minoría.
""")

col1, col2 = st.columns(2)

with col1:
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(
        x=roc_lr["fpr"], y=roc_lr["tpr"],
        name=f"Logística (AUC={auc_lr:.3f})",
        mode="lines", line=dict(width=2)
    ))
    fig_roc.add_trace(go.Scatter(
        x=roc_xgb["fpr"], y=roc_xgb["tpr"],
        name=f"XGBoost (AUC={auc_xgb:.3f})",
        mode="lines", line=dict(width=2)
    ))
    fig_roc.add_trace(go.Scatter(
        x=[0, 1], y=[0, 1], mode="lines",
        line=dict(dash="dash", color="gray", width=1),
        showlegend=False
    ))
    fig_roc.update_layout(
        title="Curva ROC",
        xaxis_title="Falsos Positivos (clientes solventes mal clasificados)",
        yaxis_title="Verdaderos Positivos (defaults detectados)",
        height=420, legend=dict(x=0.5, y=0.1)
    )
    st.plotly_chart(fig_roc, use_container_width=True)

with col2:
    fig_pr = go.Figure()
    fig_pr.add_trace(go.Scatter(
        x=pr_lr["recall"], y=pr_lr["precision"],
        name="Logística", mode="lines", line=dict(width=2)
    ))
    fig_pr.add_trace(go.Scatter(
        x=pr_xgb["recall"], y=pr_xgb["precision"],
        name="XGBoost", mode="lines", line=dict(width=2)
    ))
    fig_pr.update_layout(
        title="Curva Precision-Recall",
        xaxis_title="Recall (% de defaults reales detectados)",
        yaxis_title="Precision (% de aciertos entre los alertados)",
        height=420, legend=dict(x=0.5, y=0.9)
    )
    st.plotly_chart(fig_pr, use_container_width=True)

st.markdown("""
XGBoost alcanza un **AUC-ROC de 0.869** frente al **0.860** de la Regresión Logística.
La diferencia es moderada — lo que indica que las variables están bien construidas y que
incluso un modelo simple captura el patrón principal. Sin embargo, XGBoost tiene ventaja
en variables con efectos no lineales como `age` y `mora_acumulada`, donde la Logística
asume relaciones que los datos no respetan.

La Regresión Logística se mantiene como **baseline obligatorio** en crédito: sus
coeficientes son directamente interpretables como odds ratios, lo que facilita la
validación regulatoria y la explicación a comités de riesgo.
""")

st.markdown("---")

# ---------------------------------------------------------------
# UMBRAL DE DECISIÓN
# ---------------------------------------------------------------
st.subheader("¿A partir de qué probabilidad se rechaza un cliente?")

st.markdown("""
Todo modelo de clasificación produce una probabilidad entre 0 y 1. Para convertirla
en una decisión — aprobar o rechazar — se necesita un **umbral**: si la probabilidad
supera ese valor, el cliente se clasifica como riesgo de default.

Por defecto se usa 0.5, pero en crédito ese umbral raramente es el óptimo. El problema
es asimétrico: prestarle a alguien que no va a pagar genera una pérdida real, mientras
que rechazar a un cliente solvente es solo una oportunidad perdida. Dependiendo del
apetito de riesgo del negocio, conviene ajustar ese punto de corte.

La siguiente gráfica muestra cómo cambian tres métricas al mover el umbral:
- **Recall:** qué porcentaje de los defaults reales estamos capturando
- **Precision:** de los que marcamos como default, cuántos realmente lo son
- **F1:** balance entre ambas — útil cuando ninguna puede sacrificarse completamente
""")

fig_umbral = go.Figure()
fig_umbral.add_trace(go.Scatter(
    x=df_umbrales["Umbral"], y=df_umbrales["Precision"],
    name="Precision", mode="lines+markers"
))
fig_umbral.add_trace(go.Scatter(
    x=df_umbrales["Umbral"], y=df_umbrales["Recall"],
    name="Recall", mode="lines+markers"
))
fig_umbral.add_trace(go.Scatter(
    x=df_umbrales["Umbral"], y=df_umbrales["F1"],
    name="F1", mode="lines+markers"
))
fig_umbral.update_layout(
    title="Precision vs Recall según umbral — XGBoost",
    xaxis_title="Umbral de decisión",
    yaxis_title="Score",
    height=420
)
st.plotly_chart(fig_umbral, use_container_width=True)

st.markdown("""
La gráfica confirma el trade-off esperado: a medida que bajamos el umbral, capturamos
más defaults (Recall sube) pero a costa de más falsas alarmas (Precision baja).

**¿Qué umbral elegir?**

- **Umbral 0.20 — originación masiva:** captura el 94% de defaults con precisión del 12%.
  Adecuado cuando el costo de aprobar a alguien que no va a pagar supera ampliamente
  el costo de rechazar a un buen cliente. El banco prefiere ser conservador.

- **Umbral 0.50 — seguimiento focalizado:** precisión del 22% pero captura el 78%
  de defaults. Útil cuando los recursos de gestión de mora son limitados y se quiere
  concentrar esfuerzos solo en los casos más probables.

No existe un umbral universalmente correcto — la decisión depende del contexto
del negocio y del costo relativo de cada tipo de error.
""")
st.markdown("---")

# ===============================================================
# 4. INTERPRETABILIDAD — SHAP
# ===============================================================
st.header("3. Interpretabilidad — SHAP values")

st.markdown("""
Un modelo que solo dice *"este cliente tiene 98% de probabilidad de default"* no es
suficiente en banca. Un comité de riesgo, un auditor o un regulador va a preguntar
**¿por qué?** SHAP (SHapley Additive exPlanations) permite responder exactamente eso:
descompone la predicción de cada cliente en la contribución individual de cada variable.

La lógica es simple: el modelo parte de una probabilidad base (el promedio del portafolio,
~6.7%) y cada variable la empuja hacia arriba o hacia abajo. La suma de todas esas
contribuciones explica por qué un cliente específico terminó con la probabilidad que tiene.

- **SHAP positivo** → esa variable aumenta el riesgo de default
- **SHAP negativo** → esa variable protege contra el default
""")

st.markdown("---")

# ---------------------------------------------------------------
# IMPORTANCIA GLOBAL
# ---------------------------------------------------------------
st.subheader("¿Qué variables importan más para el modelo?")

st.markdown("""
La siguiente gráfica muestra el comportamiento de los SHAP values para todos los
clientes del conjunto de validación simultáneamente. Cada punto representa un cliente.

**Cómo leerla:**
- **Eje Y:** variables ordenadas de mayor a menor importancia
- **Eje X:** valor SHAP — qué tanto empuja esa variable hacia default (derecha)
  o hacia solvencia (izquierda)
- **Color rojo:** el cliente tiene un valor **alto** en esa variable
- **Color azul:** el cliente tiene un valor **bajo** en esa variable

Por ejemplo, en `revolving_util`: los puntos rojos están a la derecha — utilización
alta aumenta el riesgo. Los azules están a la izquierda — utilización baja lo reduce.
En `age` ocurre lo contrario: los puntos rojos (clientes mayores) están a la izquierda,
lo que confirma que la edad avanzada **protege** contra el default.
""")

from PIL import Image
st.image(
    Image.open(BASE / "shap_summary_plot.png"),
    caption="Cada punto es un cliente del conjunto de validación. Rojo = valor alto de la variable, Azul = valor bajo. La posición horizontal indica el impacto sobre el riesgo.",
    width=600
)

st.markdown("""
La gráfica revela tres patrones claros:

- **`revolving_util`** tiene la distribución más amplia — clientes con utilización
  alta (rojo) se concentran a la derecha con impactos de hasta +2, mientras los de
  utilización baja (azul) se ubican a la izquierda. Es la variable más determinante.

- **`mora_acumulada`** muestra un patrón asimétrico: la mayoría de puntos están
  cerca de cero (clientes sin mora previa), pero los pocos con mora acumulada alta
  (rojo) generan impactos muy grandes hacia la derecha — son los casos de mayor riesgo.

- **`age`** es la única variable donde el rojo está a la izquierda — mayor edad
  reduce el riesgo. Su efecto es consistente y lineal a lo largo de toda la distribución.
""")

st.markdown("#### Ranking de importancia por variable")

st.markdown("""
La siguiente gráfica resume la importancia global de cada variable como el promedio
del valor absoluto de sus SHAP values — es decir, cuánto impacta en promedio sobre
todos los clientes, sin importar la dirección.
""")

fig_imp = px.bar(
    importancia.sort_values("SHAP_medio_absoluto"),
    x="SHAP_medio_absoluto",
    y="Variable",
    orientation="h",
    title="Contribución media absoluta por variable — SHAP",
    labels={"SHAP_medio_absoluto": "SHAP medio absoluto", "Variable": ""}
)
fig_imp.update_layout(height=450)
st.plotly_chart(fig_imp, use_container_width=True)

st.markdown("""
`revolving_util` y `mora_acumulada` dominan el modelo con amplia ventaja.
La edad (`age`) ocupa el tercer lugar con un efecto protector claro.

El hallazgo más relevante desde el punto de vista del negocio es que `monthly_income_log`
aparece en la mitad inferior del ranking — **el comportamiento crediticio previo importa
más que la capacidad declarada de pago**. Un cliente de altos ingresos con historial
de mora sigue siendo un cliente de alto riesgo.
""")

st.markdown("---")

# ---------------------------------------------------------------
# ANÁLISIS INDIVIDUAL
# ---------------------------------------------------------------
st.subheader("¿Cómo decide el modelo para un cliente específico?")

st.markdown("""
Para ilustrar cómo opera el modelo en la práctica, se analizan tres perfiles del
conjunto de validación: un cliente de alto riesgo, uno de bajo riesgo y un caso
ambiguo donde las señales se contradicen.

En cada caso, la gráfica de barras muestra la contribución SHAP de cada variable:
**rojo** significa que esa variable empuja hacia default, **verde** que lo reduce.
La magnitud de la barra indica qué tan fuerte es ese efecto.
""")

clientes_data = {
    "Alto riesgo 🔴":  (shap_alto,    0.9865, "Sí"),
    "Bajo riesgo 🟢":  (shap_bajo,    0.0076, "No"),
    "Caso ambiguo 🟡": (shap_ambiguo, 0.5000, "No"),
}

tab1, tab2, tab3 = st.tabs(list(clientes_data.keys()))

for tab, (nombre, (df_shap, prob, default_real)) in zip(
    [tab1, tab2, tab3], clientes_data.items()
):
    with tab:
        col1, col2 = st.columns([1, 2])

        with col1:
            st.metric("P(default)", f"{prob:.2%}")
            st.metric("Default real", default_real)
            st.markdown("**Características del cliente**")
            st.dataframe(
                df_shap[["Variable", "Valor"]].set_index("Variable"),
                use_container_width=True
            )

        with col2:
            df_plot = df_shap.copy()
            df_plot["color"] = df_plot["SHAP"].apply(
                lambda x: "#e74c3c" if x > 0 else "#2ecc71"
            )
            df_plot = df_plot.sort_values("SHAP")

            fig_wf = go.Figure(go.Bar(
                x=df_plot["SHAP"],
                y=df_plot["Variable"],
                orientation="h",
                marker_color=df_plot["color"],
            ))
            fig_wf.update_layout(
                title="Contribución de cada variable a la predicción",
                xaxis_title="SHAP value (rojo = aumenta riesgo, verde = reduce riesgo)",
                height=420,
                xaxis=dict(zeroline=True, zerolinewidth=2)
            )
            st.plotly_chart(fig_wf, use_container_width=True)

descripciones = {
    "Alto riesgo 🔴": """
        Cliente de 33 años con utilización de crédito al límite (`revolving_util=1.07`)
        y 9 eventos de mora acumulados. Estas dos variables generan contribuciones SHAP
        altamente positivas (+1.51 y +1.14 respectivamente) que dominan completamente
        la predicción. El modelo asigna una probabilidad de default del **98.65%** —
        un rechazo automático en cualquier política de originación estándar. El resto
        de variables tienen un impacto marginal: nada puede compensar ese historial.
    """,
    "Bajo riesgo 🟢": """
        Cliente de 95 años, sin ningún evento de mora previo y utilización de crédito
        prácticamente en cero. Todas las barras son verdes — cada variable contribuye
        a reducir el riesgo. La edad (-1.14) y la utilización (-1.38) son los factores
        más protectores. Probabilidad de default: **0.76%**. Perfil ideal para ofrecer
        productos de crédito con condiciones preferenciales o tasas diferenciadas.
    """,
    "Caso ambiguo 🟡": """
        El caso más interesante del análisis. `revolving_util=1.0` empuja fuertemente
        hacia default (+0.88), pero la ausencia total de mora previa lo compensa
        parcialmente (-0.52). Con solo 30 años y deuda alta pero sin historial de
        incumplimiento, las señales se cancelan entre sí y el modelo no puede decidir
        — probabilidad exactamente del **50%**. Este es precisamente el perfil que
        requiere revisión manual o información adicional antes de tomar una decisión
        de crédito: ni aprobación automática ni rechazo automático.
    """
}

tab1, tab2, tab3 = st.tabs(list(clientes_data.keys()))
for tab, nombre in zip([tab1, tab2, tab3], clientes_data.keys()):
    with tab:
        st.markdown(descripciones[nombre])

st.markdown("---")


st.markdown("---")
st.header("4. Simulador de riesgo crediticio")

st.markdown("""
Con base en el modelo entrenado, este simulador estima la probabilidad de default
de un cliente a 2 años. Ingresa las características del cliente y el modelo explicará
no solo el resultado, sino **qué variables lo determinan y en qué dirección**.
""")

import joblib
import shap

@st.cache_resource
def cargar_modelo():
    modelo = joblib.load(BASE / "xgb_model.pkl")
    return modelo

xgb_sim = cargar_modelo()
explainer_sim = shap.TreeExplainer(xgb_sim)

# ---------------------------------------------------------------
# FORMULARIO DE ENTRADA
# ---------------------------------------------------------------
st.subheader("Características del cliente")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Perfil básico**")
    age = st.slider(
        "Edad",
        min_value=18, max_value=100, value=45,
        help="Edad del cliente en años"
    )
    monthly_income = st.number_input(
        "Ingreso mensual (USD)",
        min_value=0, max_value=50000, value=5000, step=500,
        help="Ingreso mensual declarado del cliente"
    )
    dependents = st.slider(
        "Número de dependientes",
        min_value=0, max_value=10, value=0,
        help="Personas que dependen económicamente del cliente"
    )

with col2:
    st.markdown("**Comportamiento crediticio**")
    revolving_util = st.slider(
        "Utilización de líneas rotativas (0 a 1)",
        min_value=0.0, max_value=1.0, value=0.3, step=0.01,
        help="Proporción del cupo disponible que está siendo usado. 1.0 = al límite"
    )
    late_30_59 = st.slider(
        "Veces con mora 30-59 días",
        min_value=0, max_value=10, value=0,
        help="Número de veces que el cliente tuvo entre 30 y 59 días de retraso"
    )
    late_60_89 = st.slider(
        "Veces con mora 60-89 días",
        min_value=0, max_value=10, value=0,
        help="Número de veces que el cliente tuvo entre 60 y 89 días de retraso"
    )
    late_90 = st.slider(
        "Veces con mora 90+ días",
        min_value=0, max_value=10, value=0,
        help="Número de veces que el cliente tuvo 90 o más días de retraso"
    )

with col3:
    st.markdown("**Estructura de deuda**")
    debt_ratio = st.number_input(
        "Debt Ratio",
        min_value=0.0, max_value=2500.0, value=0.35, step=0.01,
        help="Relación entre deudas totales e ingresos. Mayor a 1 indica que las deudas superan el ingreso"
    )
    open_credit_lines = st.slider(
        "Líneas de crédito abiertas",
        min_value=0, max_value=40, value=8,
        help="Número total de tarjetas de crédito y préstamos activos"
    )
    real_estate_loans = st.slider(
        "Préstamos hipotecarios",
        min_value=0, max_value=10, value=1,
        help="Número de préstamos de vivienda o bienes raíces activos"
    )

# ---------------------------------------------------------------
# CÁLCULO INTERNO DE VARIABLES ENGINEERED
# ---------------------------------------------------------------
mora_acumulada = late_30_59 + late_60_89 + late_90
tiene_mora_previa = 1 if mora_acumulada > 0 else 0
ingreso_por_dependiente = monthly_income / (dependents + 1)

# Aplicar los mismos cappings del entrenamiento
debt_ratio_capped  = min(debt_ratio, 2449.0)
income_capped      = min(monthly_income, 23000.0)
ingreso_dep_capped = min(ingreso_por_dependiente, 23000.0)

# Transformación log1p igual que en entrenamiento
debt_ratio_log           = np.log1p(debt_ratio_capped)
monthly_income_log       = np.log1p(income_capped)
ingreso_por_dependiente_log = np.log1p(ingreso_dep_capped)

# Vector de features en el mismo orden que FEATURES
input_dict = {
    "revolving_util":            revolving_util,
    "age":                       age,
    "late_30_59":                late_30_59,
    "late_90":                   late_90,
    "late_60_89":                late_60_89,
    "open_credit_lines":         open_credit_lines,
    "real_estate_loans":         real_estate_loans,
    "dependents":                dependents,
    "mora_acumulada":            mora_acumulada,
    "tiene_mora_previa":         tiene_mora_previa,
    "debt_ratio_log":            debt_ratio_log,
    "monthly_income_log":        monthly_income_log,
    "ingreso_por_dependiente_log": ingreso_por_dependiente_log
}

FEATURES = [
    "revolving_util", "age", "late_30_59", "late_90", "late_60_89",
    "open_credit_lines", "real_estate_loans", "dependents",
    "mora_acumulada", "tiene_mora_previa",
    "debt_ratio_log", "monthly_income_log", "ingreso_por_dependiente_log"
]

input_df = pd.DataFrame([input_dict])[FEATURES]

# ---------------------------------------------------------------
# PREDICCIÓN Y SHAP
# ---------------------------------------------------------------
if st.button("Calcular riesgo", type="primary", use_container_width=True):

    prob = xgb_sim.predict_proba(input_df)[0][1]
    shap_vals = explainer_sim(input_df)

    # Nivel de riesgo
    if prob < 0.10:
        nivel    = "🟢 Riesgo Bajo"
        color    = "#2ecc71"
        mensaje  = "El perfil del cliente es consistente con un comportamiento de pago sólido. Candidato para aprobación automática."
    elif prob < 0.30:
        nivel    = "🟡 Riesgo Moderado"
        color    = "#f39c12"
        mensaje  = "El cliente presenta algunas señales de alerta. Se recomienda revisión adicional antes de aprobar."
    elif prob < 0.60:
        nivel    = "🟠 Riesgo Alto"
        color    = "#e67e22"
        mensaje  = "El perfil muestra señales claras de riesgo. Se recomienda solicitar garantías adicionales o ajustar condiciones."
    else:
        nivel    = "🔴 Riesgo Muy Alto"
        color    = "#e74c3c"
        mensaje  = "El modelo identifica una probabilidad de default muy alta. Perfil de rechazo bajo políticas estándar de originación."

    # Resultado principal
    st.markdown("---")
    st.subheader("Resultado")

    col_res1, col_res2 = st.columns([1, 2])

    with col_res1:
        st.markdown(
            f"""
            <div style="
                border: 2px solid {color};
                border-radius: 16px;
                padding: 1.5rem;
                text-align: center;
                background: rgba(255,255,255,0.02)
            ">
                <div style="font-size: 2.5rem; font-weight: 800; color: {color}">
                    {prob:.1%}
                </div>
                <div style="font-size: 1rem; color: #6b7280; margin-top: 0.3rem">
                    Probabilidad de default
                </div>
                <div style="font-size: 1.1rem; font-weight: 600; margin-top: 0.8rem">
                    {nivel}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")
        st.info(mensaje)

    with col_res2:
        # Gráfica SHAP del cliente
        nombres_legibles = {
            "revolving_util":               "Utilización de crédito rotativo",
            "age":                          "Edad",
            "late_30_59":                   "Mora 30-59 días",
            "late_90":                      "Mora 90+ días",
            "late_60_89":                   "Mora 60-89 días",
            "open_credit_lines":            "Líneas de crédito abiertas",
            "real_estate_loans":            "Préstamos hipotecarios",
            "dependents":                   "Dependientes",
            "mora_acumulada":               "Mora acumulada histórica",
            "tiene_mora_previa":            "Tiene mora previa",
            "debt_ratio_log":               "Ratio de deuda",
            "monthly_income_log":           "Ingreso mensual",
            "ingreso_por_dependiente_log":  "Ingreso por dependiente"
        }

        shap_df = pd.DataFrame({
            "Variable": [nombres_legibles[f] for f in FEATURES],
            "SHAP":     shap_vals.values[0]
        }).sort_values("SHAP")

        shap_df["color"] = shap_df["SHAP"].apply(
            lambda x: "#e74c3c" if x > 0 else "#2ecc71"
        )

        fig_sim = go.Figure(go.Bar(
            x=shap_df["SHAP"],
            y=shap_df["Variable"],
            orientation="h",
            marker_color=shap_df["color"]
        ))
        fig_sim.update_layout(
            title="¿Por qué este resultado? — Contribución de cada variable",
            xaxis_title="Impacto (rojo = aumenta riesgo, verde = reduce riesgo)",
            height=450,
            xaxis=dict(zeroline=True, zerolinewidth=2)
        )
        st.plotly_chart(fig_sim, use_container_width=True)

    # Explicación en lenguaje natural
    st.subheader("Explicación del resultado")

    top_riesgo   = shap_df[shap_df["SHAP"] > 0].sort_values("SHAP", ascending=False).head(3)
    top_protecc  = shap_df[shap_df["SHAP"] < 0].sort_values("SHAP").head(3)

    col_r, col_p = st.columns(2)

    with col_r:
        st.markdown("**🔴 Principales factores de riesgo**")
        if len(top_riesgo) == 0:
            st.write("Ninguna variable aumenta significativamente el riesgo.")
        else:
            for _, row in top_riesgo.iterrows():
                st.markdown(f"- **{row['Variable']}** — impacto: `+{row['SHAP']:.3f}`")

    with col_p:
        st.markdown("**🟢 Principales factores protectores**")
        if len(top_protecc) == 0:
            st.write("Ninguna variable reduce significativamente el riesgo.")
        else:
            for _, row in top_protecc.iterrows():
                st.markdown(f"- **{row['Variable']}** — impacto: `{row['SHAP']:.3f}`")


# ===============================================================
# 5. CONCLUSIONES
# ===============================================================
st.header("5. Conclusiones")

st.markdown("""
**Problema:** predecir la probabilidad de default crediticio a 2 años sobre
150,000 clientes con fuerte desbalance de clases (6.7% de defaults).

**Resultado:** XGBoost alcanza un **AUC-ROC de 0.869**, superando al baseline
de Regresión Logística (0.860). La diferencia moderada entre modelos indica
que las variables están bien construidas y que incluso un modelo simple
captura el patrón principal.

**Hallazgos clave:**

- `revolving_util` y `mora_acumulada` son los predictores dominantes —
  juntos explican la mayor parte del riesgo de default.
- La **edad tiene un efecto protector no lineal**: clientes mayores son
  sistemáticamente menos riesgosos, lo que favorece modelos como XGBoost
  sobre la regresión logística.
- El **ingreso importa menos que el comportamiento crediticio previo** —
  un cliente de altos ingresos con historial de mora sigue siendo un
  cliente de alto riesgo.
- El umbral óptimo depende del apetito de riesgo: un umbral de **0.20**
  captura el 94% de defaults y es recomendable para originación masiva;
  uno de **0.50** es más conservador y adecuado cuando los recursos
  de seguimiento son limitados.

**Limitación principal:** el dataset es de 2011 y el comportamiento
crediticio puede haber cambiado. En producción, el modelo requeriría
reentrenamiento periódico con datos recientes.
""")


