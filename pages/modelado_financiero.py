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
