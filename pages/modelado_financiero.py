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




