import streamlit as st
import navigation
import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

st.title("Series de tiempo multivariadas")
st.subheader("Modelación conjunta de factores de riesgo mediante aproximación normal multivariada y VAR")

st.markdown(
    """
En esta sección se presenta un caso de **series de tiempo multivariadas** aplicado a seis factores de riesgo observados mensualmente.
El objetivo no es únicamente construir proyecciones, sino **comparar enfoques estadísticos alternativos** y justificar, con evidencia
econométrica, cuál resulta más adecuado para modelar la dinámica conjunta de las series.

La lógica del análisis sigue una secuencia natural de modelación:

1. **Exploración de los datos históricos**.
2. **Modelo base**: cambios mensuales con distribución normal multivariada.
3. **Diagnóstico estadístico** del modelo base.
4. **Modelo dinámico**: proceso VAR para capturar dependencia temporal.
5. **Conclusiones** sobre la idoneidad de cada enfoque.

Desde una perspectiva de estadística aplicada y econometría, esta comparación es importante porque distingue entre:
- **dependencia contemporánea**, capturada por una matriz de covarianza;
- **dependencia temporal**, que requiere una estructura dinámica explícita.

En términos sencillos: dos variables pueden moverse juntas en el mismo mes, pero además pueden exhibir **memoria en el tiempo**.
Un modelo útil debe reconocer ambas dimensiones cuando los datos así lo exigen.
"""
)


# ============================================================
# RUTAS DE ARCHIVOS
# ============================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = ROOT_DIR / "page" /"Series_tiempo" / "Multivariado"
DATA_DIR = PROJECT_DIR / "data"
FIG_DIR = PROJECT_DIR / "figures"

# Verificación rápida
if not DATA_DIR.exists():
    st.error(f"No existe la carpeta de datos: {DATA_DIR}")
    st.stop()

if not FIG_DIR.exists():
    st.error(f"No existe la carpeta de figuras: {FIG_DIR}")
    st.stop()


# ============================================================
# FUNCIONES AUXILIARES DE CARGA
# ============================================================

@st.cache_data
def cargar_csv(nombre_archivo: str) -> pd.DataFrame:
    ruta = DATA_DIR / nombre_archivo
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    return pd.read_csv(ruta)

@st.cache_data
def cargar_json(nombre_archivo: str) -> dict:
    ruta = DATA_DIR / nombre_archivo
    if not ruta.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def archivo_existe(nombre_archivo: str, carpeta: Path) -> bool:
    return (carpeta / nombre_archivo).exists()


# ============================================================
# CARGA DE DATOS
# ============================================================

try:
    historico = cargar_csv("historico_limpio.csv")
    delta = cargar_csv("delta_factores.csv")
    mu_normal = cargar_csv("mu_normal.csv")
    sigma_normal = cargar_csv("sigma_normal.csv")
    diagnostico_normal = cargar_csv("diagnostico_normal.csv")
    resumen_var = cargar_csv("resumen_simulacion_var.csv")
    info_var = cargar_json("resumen_modelo_var.json")
except Exception as e:
    st.error(f"Error cargando archivos del proyecto: {e}")
    st.stop()


# ============================================================
# LIMPIEZA Y AJUSTES DE FORMATO
# ============================================================

if "Fecha" in historico.columns:
    historico["Fecha"] = pd.to_datetime(historico["Fecha"], errors="coerce")

factores = [c for c in historico.columns if c != "Fecha"]

if "Factor" in mu_normal.columns and "Media_delta_mensual" in mu_normal.columns:
    pass
else:
    st.warning("El archivo mu_normal.csv no tiene el formato esperado.")

if "Factor" not in resumen_var.columns:
    st.error("El archivo resumen_simulacion_var.csv debe contener la columna 'Factor'.")
    st.stop()

if "Mes" not in resumen_var.columns:
    st.error("El archivo resumen_simulacion_var.csv debe contener la columna 'Mes'.")
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("Opciones de visualización")

factor_seleccionado = st.sidebar.selectbox(
    "Selecciona un factor para análisis detallado",
    options=factores,
    index=0
)

mostrar_tablas = st.sidebar.checkbox("Mostrar tablas técnicas", value=True)
mostrar_conclusion_larga = st.sidebar.checkbox("Mostrar conclusión extendida", value=True)

mes_min = int(resumen_var["Mes"].min())
mes_max = int(resumen_var["Mes"].max())

horizonte_usuario = st.sidebar.slider(
    "Horizonte de proyección a visualizar",
    min_value=mes_min,
    max_value=mes_max,
    value=mes_max
)


# ============================================================
# TABS PRINCIPALES
# ============================================================

tab0, tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Resumen ejecutivo",
    "Datos históricos",
    "Modelo normal multivariado",
    "Diagnóstico econométrico",
    "Modelo VAR",
    "Conclusiones"
])


# ============================================================
# TAB 0: RESUMEN EJECUTIVO
# ============================================================

with tab0:
    st.markdown("## Resumen ejecutivo")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Número de factores", len(factores))
    col2.metric("Observaciones históricas", historico.shape[0])
    col3.metric("Observaciones en diferencias", delta.shape[0])
    col4.metric("Rezagos VAR seleccionados", info_var.get("lags", "N/D"))

    st.markdown(
        """
Este caso de estudio compara dos enfoques de modelación para una colección de series temporales mensuales:

- **Aproximación estática**: suponer que las diferencias mensuales siguen una distribución normal multivariada.
- **Aproximación dinámica**: ajustar un modelo **VAR** para capturar interacción y persistencia temporal.

La evidencia estadística sugiere que el enfoque normal multivariado es útil como línea base, pero **no resulta suficiente cuando
las series exhiben dependencia serial**. En ese contexto, el VAR constituye una alternativa más coherente, ya que permite incorporar
la estructura dinámica observada en los datos.
"""
    )

    st.info(
        """
**Lectura técnica breve**  
- La normal multivariada modela bien la **covariación contemporánea**.  
- El VAR modela tanto la **covariación contemporánea** como la **dependencia temporal**.  
- Cuando hay autocorrelación significativa, un modelo puramente estático tiende a ser insuficiente.
"""
    )


# ============================================================
# TAB 1: DATOS HISTÓRICOS
# ============================================================

with tab1:
    st.markdown("## Datos históricos")
    st.markdown(
        """
Se parte de un conjunto de seis factores de riesgo observados mensualmente. Para el análisis dinámico, además del nivel de las series,
se trabaja con sus **diferencias mensuales**, ya que en muchos contextos de econometría financiera y análisis temporal es más razonable
modelar los cambios que los niveles absolutos.
"""
    )

    st.markdown("### Vista previa del histórico")
    st.dataframe(historico.head(12), use_container_width=True)

    st.markdown("### Series históricas en nivel")

    historico_largo = historico.melt(
        id_vars="Fecha",
        value_vars=factores,
        var_name="Factor",
        value_name="Valor"
    )

    fig_hist = px.line(
        historico_largo,
        x="Fecha",
        y="Valor",
        color="Factor",
        title="Evolución histórica de los factores de riesgo"
    )
    fig_hist.update_layout(
        xaxis_title="Fecha",
        yaxis_title="Nivel observado",
        legend_title="Factor",
        height=520
    )
    st.plotly_chart(fig_hist, use_container_width=True)

    st.markdown("### Diferencias mensuales")
    delta_largo = delta.copy()
    delta_largo["indice"] = np.arange(1, len(delta_largo) + 1)

    delta_largo = delta_largo.melt(
        id_vars="indice",
        value_vars=delta.columns,
        var_name="Factor",
        value_name="Delta"
    )

    fig_delta = px.line(
        delta_largo[delta_largo["Factor"] == factor_seleccionado],
        x="indice",
        y="Delta",
        title=f"Diferencias mensuales de {factor_seleccionado}"
    )
    fig_delta.update_layout(
        xaxis_title="Tiempo",
        yaxis_title="Cambio mensual",
        height=420
    )
    st.plotly_chart(fig_delta, use_container_width=True)

    st.markdown(
        """
**Comentario estadístico.**  
En modelación de series de tiempo multivariadas, trabajar con diferencias cumple dos propósitos:
1. atenúa problemas de tendencia y no estacionariedad en nivel;
2. permite enfocar el análisis en la dinámica de corto plazo.

Esto no reemplaza pruebas formales de estacionariedad, pero sí constituye una transformación estándar y razonable en este contexto.
"""
    )


# ============================================================
# TAB 2: MODELO NORMAL MULTIVARIADO
# ============================================================

with tab2:
    st.markdown("## Modelo base: normal multivariada")
    st.markdown(
        r"""
Como primera aproximación, se asume que el vector de cambios mensuales satisface:

\[
\Delta X_t \sim N(\mu, \Sigma)
\]

donde:

- \(\mu\) representa el vector de medias de los cambios mensuales;
- \(\Sigma\) representa la matriz de varianzas y covarianzas contemporáneas.

Este enfoque es útil como **benchmark estadístico** porque:
- es interpretable;
- es fácil de estimar;
- captura la estructura de correlación entre variables en un mismo periodo.

Sin embargo, su limitación principal es que **no incorpora dinámica temporal explícita**.
En otras palabras, permite modelar cómo se mueven juntas las variables dentro de un mismo mes,
pero no cómo el pasado afecta el futuro.
"""
    )

    col_a, col_b = st.columns([1, 1])

    with col_a:
        st.markdown("### Vector de medias")
        st.dataframe(mu_normal, use_container_width=True)

    with col_b:
        st.markdown("### Matriz de covarianza")
        sigma_df = sigma_normal.copy()

        # Si el índice quedó guardado como primera columna sin nombre, se limpia
        if sigma_df.columns[0].startswith("Unnamed"):
            sigma_df = sigma_df.rename(columns={sigma_df.columns[0]: "Factor"})
            sigma_df = sigma_df.set_index("Factor")

        st.dataframe(sigma_df, use_container_width=True)

    st.markdown("### Visualización de la matriz de covarianza")

    ruta_heatmap_cov = FIG_DIR / "heatmap_cov_normal.png"
    if ruta_heatmap_cov.exists():
        st.image(str(ruta_heatmap_cov), use_container_width=True)
    else:
        st.warning("No se encontró la figura heatmap_cov_normal.png")

    st.markdown(
        """
**Interpretación econométrica.**  
La matriz de covarianza resume la magnitud de la variabilidad conjunta y de la asociación contemporánea entre factores.
No obstante, una matriz de covarianza por sí sola no constituye un modelo dinámico: si existe persistencia en el tiempo,
este enfoque puede subestimar patrones temporales relevantes y, por tanto, generar simulaciones menos realistas.
"""
    )


# ============================================================
# TAB 3: DIAGNÓSTICO ECONOMÉTRICO
# ============================================================

with tab3:
    st.markdown("## Diagnóstico econométrico del modelo base")
    st.markdown(
        """
Para evaluar la idoneidad del enfoque normal multivariado, se revisan dos aspectos esenciales:

1. **Normalidad marginal** de los cambios mensuales.
2. **Ausencia de autocorrelación** en cada serie de diferencias.

La lógica de esta evaluación es muy importante:

- Si los cambios no son aproximadamente normales, el modelo puede representar mal la dispersión y las colas.
- Si las series presentan autocorrelación, entonces un modelo estático ignora información temporal relevante.

Desde un punto de vista econométrico, un modelo puede ser conveniente como primera aproximación,
pero debe ser **validado a la luz de los datos**.
"""
    )

    diagnostico_vista = diagnostico_normal.copy()

    # Normalización de nombres por si el CSV quedó con mayúsculas/minúsculas distintas
    cols_diag = {c.lower(): c for c in diagnostico_vista.columns}

    col_factor = cols_diag.get("factor", None)
    col_pnorm = cols_diag.get("p_normalidad", None)
    col_pauto = cols_diag.get("p_autocorrelacion", None)

    if col_factor and col_pnorm and col_pauto:
        diagnostico_vista["Conclusión normalidad"] = np.where(
            diagnostico_vista[col_pnorm] > 0.05,
            "Compatible con normalidad",
            "Evidencia contra normalidad"
        )
        diagnostico_vista["Conclusión autocorrelación"] = np.where(
            diagnostico_vista[col_pauto] > 0.05,
            "Sin evidencia de autocorrelación",
            "Hay dependencia temporal"
        )

        st.dataframe(diagnostico_vista, use_container_width=True)

        fig_norm = px.bar(
            diagnostico_vista,
            x=col_factor,
            y=col_pnorm,
            title="p-values de normalidad por factor"
        )
        fig_norm.add_hline(y=0.05, line_dash="dash")
        fig_norm.update_layout(yaxis_title="p-value")
        st.plotly_chart(fig_norm, use_container_width=True)

        fig_auto = px.bar(
            diagnostico_vista,
            x=col_factor,
            y=col_pauto,
            title="p-values de autocorrelación por factor"
        )
        fig_auto.add_hline(y=0.05, line_dash="dash")
        fig_auto.update_layout(yaxis_title="p-value")
        st.plotly_chart(fig_auto, use_container_width=True)

        n_no_normales = int((diagnostico_vista[col_pnorm] <= 0.05).sum())
        n_con_auto = int((diagnostico_vista[col_pauto] <= 0.05).sum())

        st.markdown("### Lectura de resultados")
        st.write(
            f"- Factores con evidencia contra normalidad al 5%: **{n_no_normales}** de **{len(diagnostico_vista)}**."
        )
        st.write(
            f"- Factores con evidencia de dependencia temporal al 5%: **{n_con_auto}** de **{len(diagnostico_vista)}**."
        )

        st.warning(
            """
**Decisión estadística.**  
Si existe evidencia de autocorrelación en una o varias series, la hipótesis de independencia temporal implícita
en la aproximación normal multivariada resulta cuestionable. En ese caso, conviene pasar a un modelo dinámico.
"""
        )
    else:
        st.warning("No se pudieron identificar correctamente las columnas del archivo diagnostico_normal.csv")

    st.markdown(
        """
**Conclusión técnica de esta etapa.**  
La normal multivariada puede ser razonable como modelo descriptivo de corto alcance o como benchmark comparativo.
Sin embargo, cuando el objetivo es proyectar trayectorias realistas en presencia de memoria temporal,
es preferible un modelo que incorpore explícitamente esa dinámica. Esa es precisamente la motivación del modelo VAR.
"""
    )


# ============================================================
# TAB 4: MODELO VAR
# ============================================================

with tab4:
    st.markdown("## Modelo dinámico: VAR")
    st.markdown(
        r"""
El modelo **VAR (Vector Autoregressive Model)** introduce una estructura dinámica entre los factores. De manera general:

\[
X_t = c + A_1 X_{t-1} + \cdots + A_p X_{t-p} + \varepsilon_t
\]

En este marco:
- el vector actual depende de sus propios rezagos;
- cada variable puede depender del pasado de las demás;
- el término \(\varepsilon_t\) captura innovaciones no anticipadas.

La principal ventaja econométrica del VAR es que permite modelar simultáneamente:
1. **interdependencia entre variables**;
2. **persistencia temporal**;
3. **propagación dinámica de shocks**.

En aplicaciones reales, esto suele producir trayectorias simuladas más coherentes que las obtenidas bajo independencia temporal.
"""
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Rezagos seleccionados", info_var.get("lags", "N/D"))
    col2.metric("Variables modeladas", len(info_var.get("variables", factores)))
    col3.metric("Observaciones usadas", info_var.get("observaciones", "N/D"))

    st.markdown("### Proyecciones resumidas por percentiles")

    resumen_var_filtrado = resumen_var[resumen_var["Mes"] <= horizonte_usuario].copy()

    factor_var = resumen_var_filtrado[resumen_var_filtrado["Factor"] == factor_seleccionado].copy()

    fig_var = go.Figure()

    fig_var.add_trace(go.Scatter(
        x=factor_var["Mes"],
        y=factor_var["P95"],
        mode="lines",
        line=dict(width=0),
        showlegend=False,
        hoverinfo="skip"
    ))

    fig_var.add_trace(go.Scatter(
        x=factor_var["Mes"],
        y=factor_var["P05"],
        mode="lines",
        fill="tonexty",
        line=dict(width=0),
        name="Banda 5%-95%",
        hoverinfo="skip"
    ))

    fig_var.add_trace(go.Scatter(
        x=factor_var["Mes"],
        y=factor_var["P50"],
        mode="lines+markers",
        name="Mediana"
    ))

    fig_var.add_trace(go.Scatter(
        x=factor_var["Mes"],
        y=factor_var["Media"],
        mode="lines",
        name="Media"
    ))

    fig_var.update_layout(
        title=f"Proyección VAR resumida para {factor_seleccionado}",
        xaxis_title="Mes proyectado",
        yaxis_title="Nivel proyectado",
        height=500
    )

    st.plotly_chart(fig_var, use_container_width=True)

    st.markdown("### Comparación histórica reciente vs proyección esperada")

    ultimos_hist = historico[["Fecha", factor_seleccionado]].dropna().tail(24).copy()
    ultimos_hist = ultimos_hist.rename(columns={factor_seleccionado: "Valor"})
    ultimos_hist["Tipo"] = "Histórico"

    ultima_fecha = ultimos_hist["Fecha"].max()
    fechas_futuras = pd.date_range(
        start=ultima_fecha + pd.offsets.MonthBegin(1),
        periods=factor_var.shape[0],
        freq="MS"
    )

    proy_media = pd.DataFrame({
        "Fecha": fechas_futuras,
        "Valor": factor_var["Media"].values,
        "Tipo": "Proyección VAR (media)"
    })

    comparacion = pd.concat([ultimos_hist, proy_media], ignore_index=True)

    fig_comp = px.line(
        comparacion,
        x="Fecha",
        y="Valor",
        color="Tipo",
        title=f"Histórico reciente y proyección media VAR: {factor_seleccionado}"
    )
    fig_comp.update_layout(height=450)
    st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("### Correlación contemporánea de residuos del VAR")

    ruta_heatmap_res = FIG_DIR / "heatmap_corr_residuos_var.png"
    if ruta_heatmap_res.exists():
        st.image(str(ruta_heatmap_res), use_container_width=True)
    else:
        st.warning("No se encontró la figura heatmap_corr_residuos_var.png")

    st.markdown(
        """
**Interpretación estadística del VAR.**  
El interés del modelo no reside únicamente en proyectar medias, sino en proporcionar un esquema coherente
para la simulación conjunta de trayectorias. Al incorporar rezagos, el VAR reconoce que los movimientos de hoy
pueden depender del comportamiento reciente del sistema.

En contextos de análisis cuantitativo, esto es especialmente valioso porque:
- evita tratar los cambios mensuales como realizaciones temporalmente independientes;
- permite construir escenarios más plausibles;
- mejora la consistencia interna de las simulaciones multivariadas.
"""
    )

    if mostrar_tablas:
        st.markdown("### Resumen tabular de proyecciones")
        st.dataframe(
            resumen_var_filtrado[resumen_var_filtrado["Factor"] == factor_seleccionado],
            use_container_width=True
        )


# ============================================================
# TAB 5: CONCLUSIONES
# ============================================================

with tab5:
    st.markdown("## Conclusiones y decisiones de modelación")

    st.success(
        """
**Decisión principal.**  
La aproximación normal multivariada se conserva como modelo base o benchmark, pero el modelo recomendado para la
proyección y simulación conjunta de los factores es el **VAR**, dado que incorpora explícitamente la estructura dinámica del sistema.
"""
    )

    st.markdown(
        """
### Conclusiones técnicas

**1. Sobre el modelo normal multivariado**  
La aproximación normal multivariada constituye un punto de partida razonable cuando se desea resumir la media y la covarianza
de los cambios mensuales. Su principal fortaleza es la simplicidad. No obstante, su principal debilidad es igualmente clara:
**supone independencia temporal condicional al vector de medias y a la matriz de covarianza**.

**2. Sobre el diagnóstico estadístico**  
El análisis de normalidad y autocorrelación permite evaluar si esa simplificación es defendible. Cuando se detecta dependencia serial,
el supuesto de independencia temporal deja de ser apropiado, incluso si la correlación contemporánea está bien representada.

**3. Sobre el modelo VAR**  
El modelo VAR supera esa limitación porque añade estructura autorregresiva. En consecuencia, no solo modela cómo se relacionan
las variables en un mismo periodo, sino también cómo las realizaciones pasadas del sistema contribuyen a explicar la evolución futura.

**4. Sobre la calidad de la modelación**  
Desde una perspectiva econométrica, el valor del ejercicio no radica en “forzar” un modelo a funcionar, sino en
**comparar alternativas y justificar la elección con evidencia empírica**. Esa práctica refleja una lógica de modelación más sólida y profesional.

**5. Sobre el uso práctico**  
Una vez validado el carácter dinámico de la información, el VAR se convierte en una base más adecuada para:
- simulación de escenarios,
- análisis prospectivo,
- ejercicios de sensibilidad,
- y posteriores aplicaciones cuantitativas sobre portafolios o medidas de riesgo.
"""
    )

    if mostrar_conclusion_larga:
        st.markdown(
            """
### Lectura final como estadístico/econometrista

En términos metodológicos, este ejercicio deja una enseñanza importante:  
**no toda estructura multivariada puede modelarse adecuadamente con una sola matriz de covarianza**.

La covarianza contemporánea resume asociación instantánea, pero la dinámica temporal exige herramientas adicionales.
Cuando los datos muestran memoria, persistencia o interacción rezagada, un enfoque estático corre el riesgo de producir
simulaciones demasiado simplificadas.

Por ello, la secuencia correcta de trabajo fue:

- comenzar con un modelo base interpretable;
- contrastarlo con pruebas diagnósticas;
- identificar sus limitaciones;
- y reemplazarlo por un modelo más adecuado.

Esta forma de trabajar es estadísticamente rigurosa y, además, muy valiosa en entornos aplicados, porque demuestra
capacidad de diagnóstico, criterio de selección de modelos y comprensión de la estructura real de los datos.
"""
        )

    st.markdown("---")
    st.caption(
        "Proyecto de series de tiempo multivariadas: comparación entre aproximación normal multivariada y modelación VAR."
    )
