import streamlit as st
import navigation
# -----------------------------
# Configuración general
# -----------------------------


st.set_page_config(
    page_title="Luis Mantilla | Quant & Data Science Portfolio",
    page_icon="📈",
    layout="wide",
)



navigation.show()


# -----------------------------
# Helpers
# -----------------------------
def badge(text: str):
    st.markdown(
        f"""
        <span style="
            display:inline-block;
            padding:6px 10px;
            margin:4px 6px 0 0;
            border-radius:999px;
            border:1px solid rgba(49,51,63,0.2);
            background: rgba(49,51,63,0.06);
            font-size:0.9rem;">
            {text}
        </span>
        """,
        unsafe_allow_html=True,
    )

# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    st.title("📌 Navegación")

    st.markdown("---")
    st.markdown("### Secciones")
    

    if st.button("🏠 Inicio"):
        st.switch_page("app.py")
    
    if st.button("🟦 SQL"):
        st.switch_page("pages/SQL.py")
    
    if st.button("📈 Series de tiempo"):
        st.write("Próximamente")
    
    if st.button("💰 Modelado financiero"):
        st.write("Próximamente")
    
    if st.button("🤖 Machine Learning"):
        st.write("Próximamente")
    
    if st.button("🧾 CV"):
        st.write("Próximamente")

    st.markdown("---")
    st.markdown("### Enlaces")
    # TODO: cambia estos links por los tuyos
    st.link_button("GitHub", "https://github.com/tu_usuario")
    st.link_button("LinkedIn", "https://www.linkedin.com/in/tu_usuario/")
    st.link_button("CV (PDF)", "https://drive.google.com/")

# -----------------------------
# Header / Hero
# -----------------------------
col1, col2 = st.columns([2, 1], gap="large")

with col1:
    st.title("Luis Mantilla")
    st.subheader("Data Science — Riesgo financiero")
    st.write(
        """
        Portafolio orientado a **banca y riesgo**, **data science** y **cuant/finanzas**.
        Aquí encontrarás proyectos con enfoque en **SQL analytics**, **series de tiempo**, **modelado financiero** y **ML aplicado**.
        """
    )



with col2:
    st.markdown("### Perfil")
    # Si subes una imagen a assets/profile.png, se mostrará. Si no, ignora.
    try:
        st.image("assets/profile.png", use_container_width=True)
    except Exception:
        st.info("Tip: agrega una foto en `assets/profile.png` (opcional).")

    st.markdown("### Contacto")
    st.write("- 📧 correo: luisenriquemantillasanabria@gmail.com")
    st.write("- 🌎 Bogotá, Colombia")

st.markdown("---")

# -----------------------------
# Skills / Stack
# -----------------------------
st.markdown("## 🧰 Stack técnico")
st.write("Herramientas y temas que verás reflejados en los proyectos:")

skills_cols = st.columns(4)
with skills_cols[0]:
    st.markdown("**Datos / SQL**")
    badge("SQL (MySQL / PostgreSQL)")
    badge("Data modeling")
    badge("ETL / ELT")
    badge("DuckDB / Parquet")

with skills_cols[1]:
    st.markdown("**Estadística**")
    badge("Inferencia")
    badge("Multivariada")
    badge("Robusto")
    badge("Bootstrap")

with skills_cols[2]:
    st.markdown("**Finanzas cuant**")
    badge("Option pricing")
    badge("Riesgo (PD/LGD/EAD)")
    badge("VaR / ES")
    badge("Densidades no normales")

with skills_cols[3]:
    st.markdown("**ML / Programación**")
    badge("Python / R")
    badge("Time series")
    badge("XGBoost / RF")
    badge("NLP / Embeddings")

st.markdown("---")

# -----------------------------
# Proyectos (cards simples)
# -----------------------------
st.markdown("## 🚀 Proyectos destacados (próximamente)")

p1, p2, p3 = st.columns(3, gap="large")

with p1:
    st.markdown("### 🟦 Credit Risk Analytics (SQL)")
    st.write(
        """
        KPIs bancarios, mora, pagos, segmentación y análisis de riesgo con SQL.
        **Enfoque:** negocio + consultas avanzadas + dashboard.
        """
    )
    st.caption("Estado: por construir ✅")
    st.link_button("Repositorio (próximamente)", "https://github.com/tu_usuario")

with p2:
    st.markdown("### 📈 Financial Time Series")
    st.write(
        """
        Retornos, volatilidad, ARIMA/GARCH y pronósticos.
        **Enfoque:** finanzas + validación + visualización clara.
        """
    )
    st.caption("Estado: por construir ✅")
    st.link_button("Repositorio (próximamente)", "https://github.com/tu_usuario")

with p3:
    st.markdown("### 💰 Option Pricing & Risk Modeling")
    st.write(
        """
        Black-Scholes vs modelos alternativos, Monte Carlo y análisis de densidades.
        **Enfoque:** cuant + matemática + aplicación.
        """
    )
    st.caption("Estado: por construir ✅")
    st.link_button("Repositorio (próximamente)", "https://github.com/tu_usuario")

st.markdown("---")

# -----------------------------
# Sección About
# -----------------------------
st.markdown("## 👤 Sobre mí")
st.write(
    """
Soy matemático y estudiante de maestría en estadística, con interés en **finanzas cuantitativas** y **riesgo**.
Me enfoco en construir proyectos reproducibles: desde **SQL** y **modelos estadísticos** hasta **visualización** y **deploy**.
"""
)

st.markdown("## 📌 Qué encontrarás aquí")
bul1, bul2, bul3 = st.columns(3)
with bul1:
    st.markdown("**Banca y riesgo**")
    st.write("- KPIs\n- riesgo crediticio\n- segmentación\n- alertas/monitoring")
with bul2:
    st.markdown("**Data science**")
    st.write("- pipelines\n- modelos ML\n- evaluación\n- interpretabilidad")
with bul3:
    st.markdown("**Cuant/finanzas**")
    st.write("- opciones\n- volatilidad\n- simulación\n- modelos no normales")

st.markdown("---")
st.caption("© 2026 — Portafolio en Streamlit + GitHub")
