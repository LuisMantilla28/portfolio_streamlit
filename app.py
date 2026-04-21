import streamlit as st
import navigation
from pathlib import Path

st.set_page_config(
    page_title="Luis Mantilla | Portfolio",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

navigation.show()

# ---------------------------------------------------
# ESTILOS
# ---------------------------------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.0;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #6b7280;
        margin-bottom: 1rem;
    }

    .section-title {
        font-size: 1.55rem;
        font-weight: 750;
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
    }

    .muted {
        color: #6b7280;
    }

    .card {
        border: 1px solid rgba(120,120,120,0.18);
        border-radius: 18px;
        padding: 1.15rem 1.1rem;
        background: rgba(255,255,255,0.02);
        height: 100%;
    }

    .eyebrow {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }

    .card h3 {
        margin-top: 0.15rem;
        margin-bottom: 0.45rem;
        font-size: 1.12rem;
    }

    .badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.18rem 0.35rem 0.15rem 0;
        border-radius: 999px;
        border: 1px solid rgba(120,120,120,0.2);
        background: rgba(120,120,120,0.08);
        font-size: 0.84rem;
    }

    .metric-card {
        border: 1px solid rgba(120,120,120,0.18);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
        background: rgba(255,255,255,0.02);
    }

    .metric-value {
        font-size: 1.45rem;
        font-weight: 800;
        margin-bottom: 0.15rem;
    }

    .metric-label {
        font-size: 0.92rem;
        color: #6b7280;
    }

    .footer-note {
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------
# HELPERS
# ---------------------------------------------------
def badges(items):
    return "".join([f"<span class='badge'>{x}</span>" for x in items])

def project_card(category, title, desc, techs, url):
    st.markdown(
        f"""
        <div class="card">
            <div class="eyebrow">{category}</div>
            <h3>{title}</h3>
            <p>{desc}</p>
            <div>{badges(techs)}</div>
            <p style="margin-top:0.9rem;">
                <a href="{url}" target="_blank"><b>Ver proyecto ↗</b></a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# ---------------------------------------------------
# HERO
# ---------------------------------------------------
col1, col2 = st.columns([1.8, 1], gap="large")

with col1:
    st.markdown("<div class='hero-title'>Luis Mantilla</div>", unsafe_allow_html=True)
    st.markdown(
        "<div class='hero-subtitle'>Data Science · Riesgo financiero · Estadística aplicada · Quant Finance</div>",
        unsafe_allow_html=True
    )

    st.write("""
    Matemático y estudiante de maestría en estadística. 
    Desarrollo proyectos aplicados en **analítica bancaria**, **series de tiempo**, 
    **modelado financiero** y **aprendizaje estadístico**, con énfasis en 
    **riesgo**, **toma de decisiones** y **finanzas cuantitativas**.
    """)

    cta1, cta2, cta3 = st.columns(3)
    with cta1:
        st.link_button("Proyecto SQL", "https://portfolioluismantilla.streamlit.app/SQL", use_container_width=True)
    with cta2:
        st.link_button("Series de tiempo", "https://portfolioluismantilla.streamlit.app/series_tiempo", use_container_width=True)
    with cta3:
        st.link_button("Modelado financiero", "https://portfolioluismantilla.streamlit.app/modelado_financiero", use_container_width=True)

with col2:
    st.markdown("### Perfil")
    profile_path = Path("assets/profile.png")
    if profile_path.exists():
        st.image(str(profile_path), width=220)
    else:
        st.info("Puedes agregar una foto en `assets/profile.png`.")

    st.markdown("### Contacto")
    st.write("📧 **Correo:** luisenriquemantillasanabria@gmail.com")
    st.write("📍 **Ubicación:** Bogotá, Colombia")
    st.write("🎯 **Interés:** riesgo, banca, pricing y estadística aplicada")

st.markdown("")

# ---------------------------------------------------
# MÉTRICAS RÁPIDAS
# ---------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">4</div>
        <div class="metric-label">proyectos eje</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">SQL · R · Python</div>
        <div class="metric-label">stack principal</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">Riesgo + Datos</div>
        <div class="metric-label">enfoque aplicado</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">Estadística + Negocio</div>
        <div class="metric-label">perfil híbrido</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ---------------------------------------------------
# PROYECTOS
# ---------------------------------------------------
st.markdown("<div class='section-title'>🚀 Proyectos destacados</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='muted'>Cada proyecto muestra una faceta distinta de mi perfil: negocio, modelación, simulación y análisis estadístico.</div>",
    unsafe_allow_html=True
)

p1, p2 = st.columns(2, gap="large")
p3, p4 = st.columns(2, gap="large")

with p1:
    project_card(
        "Banking Analytics · SQL",
        "SQL para Riesgo Bancario",
        "Análisis de cartera, mora, perfil de clientes, señales tempranas y oportunidad comercial a partir de una base relacional sintética orientada a negocio.",
        ["SQL", "DuckDB", "Riesgo crediticio", "KPIs", "Segmentación"],
        "https://portfolioluismantilla.streamlit.app/SQL"
    )

with p2:
    project_card(
        "Time Series · Forecasting",
        "Escenarios Multivariados de Riesgo",
        "Comparación de metodologías de series de tiempo y construcción de un motor de simulación para factores de riesgo, con validación rolling y selección de VAR(1).",
        ["VAR", "Rolling validation", "Bootstrap", "Factores de riesgo", "Series multivariadas"],
        "https://portfolioluismantilla.streamlit.app/series_tiempo"
    )

with p3:
    project_card(
        "ALM · Quant Finance",
        "Proyección de NII y cálculo de EaR",
        "Ejercicio de riesgo de tasa de interés en el libro bancario mediante simulación de escenarios, proyección del margen financiero y descomposición de exposición.",
        ["NII", "EaR", "IRRBB", "Simulación", "Balance bancario"],
        "https://portfolioluismantilla.streamlit.app/modelado_financiero"
    )

with p4:
    project_card(
        "Statistics · Unsupervised Learning",
        "Aprendizaje no Supervisado y Análisis Multivariado",
        "Proyecto en Quarto orientado a exploración estructural de datos, reducción de dimensionalidad y lectura estadística de patrones multivariados.",
        ["Análisis multivariado", "Unsupervised learning", "Quarto", "EDA", "Visualización"],
        "https://luis-mantilla.quarto.pub/aa_cd/Analisis_Multivariado.html#an%C3%A1lisis-sobre-las-variables"
    )

st.markdown("---")

# ---------------------------------------------------
# LOGRO
# ---------------------------------------------------
st.markdown("<div class='section-title'>🏆 Logro destacado</div>", unsafe_allow_html=True)

l1, l2 = st.columns([1.2, 1], gap="large")

with l1:
    st.markdown("""
    <div class="card">
        <div class="eyebrow">Validación externa</div>
        <h3>1.er lugar — Competencia de Casos CAS + ACTEX 2025</h3>
        <p>
        Integrante del equipo ganador en la competencia de casos actuariales,
        representando a la Universidad Nacional de Colombia.
        </p>
        <p>
        Este logro refuerza mi interés por la intersección entre
        <b>riesgo</b>, <b>modelación cuantitativa</b> y <b>aplicación real</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

with l2:
    st.link_button(
        "Ver publicación de reconocimiento",
        "https://www.linkedin.com/feed/update/urn:li:activity:7397403780390227969/",
        use_container_width=True
    )
    st.link_button(
        "Ver presentación final",
        "https://www.youtube.com/watch?v=is-sw5alnpw&t",
        use_container_width=True
    )

st.markdown("---")

# ---------------------------------------------------
# SOBRE MÍ
# ---------------------------------------------------
st.markdown("<div class='section-title'>👤 Sobre mí</div>", unsafe_allow_html=True)

s1, s2 = st.columns([1.2, 1], gap="large")

with s1:
    st.write("""
    Mi perfil combina formación matemática, entrenamiento estadístico y una orientación
    cada vez más fuerte hacia **finanzas cuantitativas** y **riesgo**.

    Me interesa construir proyectos que no solo tengan una metodología sólida,
    sino también una lectura clara para negocio y una presentación profesional.
    """)

with s2:
    st.markdown("**Qué encontrarás aquí**")
    st.write("• proyectos navegables")
    st.write("• análisis reproducible")
    st.write("• modelación estadística")
    st.write("• aplicaciones en banca, riesgo y finanzas")

st.markdown("---")

# ---------------------------------------------------
# ÁREAS DE TRABAJO
# ---------------------------------------------------
st.markdown("<div class='section-title'>📌 Áreas de trabajo</div>", unsafe_allow_html=True)

a1, a2, a3 = st.columns(3)

with a1:
    st.markdown("**Banca y riesgo**")
    st.write("- cartera\n- mora\n- NII / EaR\n- factores de riesgo")

with a2:
    st.markdown("**Estadística y modelación**")
    st.write("- inferencia\n- multivariado\n- validación\n- simulación")

with a3:
    st.markdown("**Data science**")
    st.write("- SQL analytics\n- series de tiempo\n- visualización\n- aprendizaje no supervisado")

st.markdown("---")

# ---------------------------------------------------
# STACK
# ---------------------------------------------------
st.markdown("<div class='section-title'>🧰 Stack técnico</div>", unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("**Lenguajes**")
    st.markdown(badges(["Python", "R", "SQL"]), unsafe_allow_html=True)

with c2:
    st.markdown("**Datos**")
    st.markdown(badges(["DuckDB", "Pandas", "Parquet", "EDA"]), unsafe_allow_html=True)

with c3:
    st.markdown("**Modelación**")
    st.markdown(badges(["VAR", "Bootstrap", "Inferencia", "Multivariado"]), unsafe_allow_html=True)

with c4:
    st.markdown("**Visualización / Deploy**")
    st.markdown(badges(["Streamlit", "Plotly", "Matplotlib", "Quarto"]), unsafe_allow_html=True)

st.markdown("<div class='footer-note'>© 2026 — Luis Mantilla · Portfolio built with Streamlit</div>", unsafe_allow_html=True)
