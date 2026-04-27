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
una estrategia explícita para el desbalance de clases, dado que los defaults representan
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
SHAP (SHapley Additive exPlanations) permite responder la pregunta que cualquier
comité de riesgo haría: **¿por qué el modelo asignó esta probabilidad a este cliente?**

Cada variable recibe un valor SHAP que representa su contribución individual a la
predicción — positivo si empuja hacia default, negativo si protege contra él.
""")

# Importancia global
st.subheader("Importancia global de variables")

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
La edad (`age`) es el tercer factor más importante, con un efecto protector
claro: a mayor edad, menor riesgo. El ingreso (`monthly_income_log`) tiene
un impacto relativamente menor — el **comportamiento crediticio previo
importa más que la capacidad declarada de pago**.
""")

# Análisis de 3 clientes
st.subheader("Análisis individual: tres perfiles de cliente")

st.markdown("""
Para ilustrar cómo el modelo toma decisiones, se analizan tres clientes
representativos del conjunto de validación.
""")

clientes_data = {
    "Alto riesgo 🔴":  (shap_alto,   0.9865, "Sí"),
    "Bajo riesgo 🟢":  (shap_bajo,   0.0076, "No"),
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
            st.markdown("**Valores del cliente**")
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
                title=f"Contribución SHAP por variable",
                xaxis_title="SHAP value",
                height=420,
                xaxis=dict(zeroline=True, zerolinewidth=2)
            )
            st.plotly_chart(fig_wf, use_container_width=True)

# Descripciones por cliente
descripciones = {
    "Alto riesgo 🔴": """
        Cliente de 33 años con utilización de crédito al límite (`revolving_util=1.07`)
        y 9 eventos de mora acumulados. Estas dos variables explican casi toda la
        predicción. El modelo asigna una probabilidad de default del **98.65%** —
        un rechazo automático en cualquier política de originación estándar.
    """,
    "Bajo riesgo 🟢": """
        Cliente de 95 años, sin ningún evento de mora previo y utilización de crédito
        prácticamente en cero. Todas las variables SHAP son negativas — cada una
        contribuye a reducir el riesgo. Probabilidad de default: **0.76%**.
        Perfil ideal para ofrecer productos de crédito con condiciones preferenciales.
    """,
    "Caso ambiguo 🟡": """
        El caso más interesante: `revolving_util=1.0` empuja fuertemente hacia default
        (+0.88), pero la ausencia total de mora previa lo compensa (-0.52). Con solo
        30 años y deuda alta pero sin historial de incumplimiento, el modelo no puede
        decidir — probabilidad exactamente del **50%**. Este es el perfil que requiere
        revisión manual o información adicional antes de aprobar.
    """
}

tab1, tab2, tab3 = st.tabs(list(clientes_data.keys()))
for tab, nombre in zip([tab1, tab2, tab3], clientes_data.keys()):
    with tab:
        st.markdown(descripciones[nombre])

st.markdown("---")

# ===============================================================
# 5. CONCLUSIONES
# ===============================================================
st.header("4. Conclusiones")

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
