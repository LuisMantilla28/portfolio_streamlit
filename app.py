import streamlit as st
import navigation
from pathlib import Path

# -------------------------------------------------------
# Configuración general
# -------------------------------------------------------
st.set_page_config(
    page_title="Luis Mantilla | Quant & Data Science Portfolio",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

navigation.show()

# -------------------------------------------------------
# Estilos
# -------------------------------------------------------
st.markdown("""
<style>
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        line-height: 1.0;
        margin-bottom: 0.2rem;
    }

    .hero-subtitle {
        font-size: 1.15rem;
        color: #4b5563;
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
        padding: 1.2rem 1.1rem;
        background: rgba(255,255,255,0.02);
        height: 100%;
    }

    .metric-card {
        border: 1px solid rgba(120,120,120,0.18);
        border-radius: 16px;
        padding: 1rem 1rem 0.9rem 1rem;
        background: rgba(255,255,255,0.02);
        text-align: center;
    }

    .metric-value {
        font-size: 1.5rem;
        font-weight: 800;
        margin-bottom: 0.2rem;
    }

    .metric-label {
        font-size: 0.95rem;
        color: #6b7280;
    }

    .badge {
        display: inline-block;
        padding: 0.35rem 0.7rem;
        margin: 0.2rem 0.35rem 0.15rem 0;
        border-radius: 999px;
        border: 1px solid rgba(120,120,120,0.2);
        background: rgba(120,120,120,0.08);
        font-size: 0.84rem;
    }

    .eyebrow {
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: #6b7280;
        margin-bottom: 0.35rem;
    }

    .card h3 {
        margin-top: 0.2rem;
        margin-bottom: 0.45rem;
        font-size: 1.15rem;
    }

    .card p {
        margin-bottom: 0.7rem;
    }

    .cta-link {
        text-decoration: none;
        font-weight: 700;
    }

    .small-note {
        font-size: 0.9rem;
        color: #6b7280;
    }

    .footer-note {
        text-align: center;
        color: #6b7280;
        font-size: 0.9rem;
        margin-top: 1rem;
    }

    .achievement-highlight {
        border-left: 4px solid #0ea5e9;
        padding-left: 1rem;
        margin-top: 0.3rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# Helpers
# -------------------------------------------------------
def render_badges(items):
    return "".join([f"<span class='badge'>{item}</span>" for item in items])

def project_card(title, category, description, techs, url):
    st.markdown(
        f"""
        <div class="card">
            <div class="eyebrow">{category}</div>
            <h3>{title}</h3>
            <p>{description}</p>
            <div>{render_badges(techs)}</div>
            <p style="margin-top:0.9rem;">
                <a class="cta-link" href="{url}" target="_blank">Ver proyecto ↗</a>
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

def achievement_card():
    st.markdown(
        f"""
        <div class="card">
            <div class="eyebrow">Logro destacado</div>
            <h3>1.er lugar — Competencia de Casos CAS + ACTEX 2025</h3>
            <div class="achievement-highlight">
                <p>
                    Integrante del equipo <b>Riskbusters</b>, ganador de la edición Spanish LatAm de la competencia,
                    representando a la <b>Universidad Nacional de Colombia</b>.
                </p>
            </div>
            <p class="small-note">
                Evidencia pública disponible en LinkedIn, artículo oficial de CAS y video de la presentación final.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------------
# Hero
# -------------------------------------------------------
left, right = st.columns([1.8, 1], gap="large")

with left:
    st.markdown('<div class="hero-title">Luis Mantilla</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="hero-subtitle">Data Science · Riesgo financiero · Estadística aplicada · Quant Finance</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Soy matemático y estudiante de maestría en estadística. 
        Construyo proyectos enfocados en **analítica bancaria**, **series de tiempo**,
        **modelado financiero** y **estadística aplicada**, con una orientación clara hacia
        **riesgo** y **finanzas cuantitativas**.
        """
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.link_button("Ver proyecto SQL", "https://portfolioluismantilla.streamlit.app/SQL", use_container_width=True)
    with c2:
        st.link_button("Ver series de tiempo", "https://portfolioluismantilla.streamlit.app/series_tiempo", use_container_width=True)
    with c3:
        st.link_button("Ver modelado financiero", "https://portfolioluismantilla.streamlit.app/modelado_financiero", use_container_width=True)

with right:
    st.markdown("### Perfil")
    profile_path = Path("assets/profile.png")
    if profile_path.exists():
        st.image(str(profile_path), use_container_width=True)
    else:
        st.info("Puedes agregar una foto en `assets/profile.png`.")

    st.markdown("### Contacto")
    st.write("📧 **Correo:** luisenriquemantillasanabria@gmail.com")
    st.write("📍 **Ubicación:** Bogotá, Colombia")
    st.write("🎯 **Interés:** riesgo, banca, pricing, analytics y data science")

st.markdown("")

# -------------------------------------------------------
# Métricas rápidas
# -------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">3</div>
        <div class="metric-label">proyectos en vivo</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">1.er</div>
        <div class="metric-label">lugar CAS + ACTEX 2025</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">R · Python · SQL</div>
        <div class="metric-label">stack principal</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-value">Finanzas + Datos</div>
        <div class="metric-label">enfoque profesional</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------
# Logro destacado
# -------------------------------------------------------
st.markdown('<div class="section-title">🏆 Validación externa</div>', unsafe_allow_html=True)

a1, a2 = st.columns([1.25, 1], gap="large")

with a1:
    achievement_card()

with a2:
    st.markdown(
        """
        **¿Por qué lo pongo tan arriba?**  
        Porque esta sección te da credibilidad inmediata.

        No solo dice que te interesan los modelos cuantitativos: muestra que ya competiste y ganaste
        en un contexto internacional con evaluación externa.

        **Enlaces de respaldo**
        """
    )
    st.link_button(
        "Publicación de la Asociación Colombiana de Actuarios",
        "https://www.linkedin.com/feed/update/urn:li:activity:7397403780390227969/",
        use_container_width=True
    )
    st.link_button(
        "Artículo oficial de CAS",
        "https://ar.casact.org/predictive-modeling-takes-center-stage-in-cas-latin-america-case-competitions/",
        use_container_width=True
    )
    st.link_button(
        "Video de la presentación final",
        "https://www.youtube.com/watch?v=is-sw5alnpw&t=1038s",
        use_container_width=True
    )

st.markdown("---")

# -------------------------------------------------------
# Proyectos
# -------------------------------------------------------
st.markdown('<div class="section-title">🚀 Proyectos destacados</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="muted">Selecciona un proyecto para ver el desarrollo completo, las visualizaciones y la lógica analítica.</div>',
    unsafe_allow_html=True
)

p1, p2, p3 = st.columns(3, gap="large")

with p1:
    project_card(
        title="Credit Risk Analytics con SQL",
        category="SQL · Banking Analytics",
        description="""
        Proyecto enfocado en indicadores bancarios, mora, pagos, segmentación y análisis de riesgo.
        Combina consulta analítica, lógica de negocio y visualización clara para toma de decisiones.
        """,
        techs=["SQL", "DuckDB", "KPIs", "Riesgo crediticio", "Segmentación"],
        url="https://portfolioluismantilla.streamlit.app/SQL"
    )

with p2:
    project_card(
        title="Series de tiempo financieras",
        category="Forecasting · Time Series",
        description="""
        Modelado de factores de riesgo y análisis temporal con énfasis en validación,
        estructura dinámica y lectura financiera de los resultados.
        """,
        techs=["Series de tiempo", "VAR", "Pronóstico", "Validación", "Visualización"],
        url="https://portfolioluismantilla.streamlit.app/series_tiempo"
    )

with p3:
    project_card(
        title="Modelado financiero y pricing",
        category="Quant Finance · Statistical Modeling",
        description="""
        Trabajo orientado a valoración y análisis cuantitativo, incluyendo comparación de modelos,
        simulación y enfoque estadístico para problemas financieros.
        """,
        techs=["Option pricing", "Simulación", "Riesgo", "R", "Finanzas cuant"],
        url="https://portfolioluismantilla.streamlit.app/modelado_financiero"
    )

st.markdown("---")

# -------------------------------------------------------
# Sobre mí
# -------------------------------------------------------
st.markdown('<div class="section-title">👤 Sobre mí</div>', unsafe_allow_html=True)

s1, s2 = st.columns([1.2, 1], gap="large")

with s1:
    st.write(
        """
        Mi perfil combina **formación matemática**, **estadística aplicada** y una orientación
        creciente hacia **finanzas cuantitativas** y **riesgo**.

        Me interesa desarrollar soluciones que no se queden solo en el modelo:
        busco que cada proyecto tenga una narrativa clara de negocio, una metodología sólida
        y una presentación profesional.
        """
    )

with s2:
    st.markdown("**Lo que encontrarás en este portafolio**")
    st.write("• Proyectos aplicados y navegables")
    st.write("• Estadística y modelado con enfoque real")
    st.write("• Análisis reproducible y visualmente claro")
    st.write("• Intersección entre datos, riesgo y finanzas")

st.markdown("---")

# -------------------------------------------------------
# Stack técnico
# -------------------------------------------------------
st.markdown('<div class="section-title">🧰 Stack técnico</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4, gap="medium")

with c1:
    st.markdown("**Datos / SQL**")
    st.markdown(render_badges([
        "SQL", "DuckDB", "Parquet", "Modelado de datos", "KPIs"
    ]), unsafe_allow_html=True)

with c2:
    st.markdown("**Estadística**")
    st.markdown(render_badges([
        "Inferencia", "Multivariada", "Bootstrap", "Modelos robustos", "Validación"
    ]), unsafe_allow_html=True)

with c3:
    st.markdown("**Finanzas cuantitativas**")
    st.markdown(render_badges([
        "Option pricing", "VaR / ES", "Riesgo", "Series financieras", "Simulación"
    ]), unsafe_allow_html=True)

with c4:
    st.markdown("**Programación**")
    st.markdown(render_badges([
        "Python", "R", "Streamlit", "Visualización", "Machine Learning"
    ]), unsafe_allow_html=True)

st.markdown("---")

# -------------------------------------------------------
# Cierre
# -------------------------------------------------------
st.markdown('<div class="section-title">📬 Cierre</div>', unsafe_allow_html=True)
st.write(
    """
    Este portafolio reúne proyectos construidos alrededor de una misma idea:
    usar herramientas estadísticas y computacionales para resolver problemas
    relevantes en datos, riesgo y finanzas.
    """
)

st.caption("© 2026 — Luis Mantilla · Portfolio built with Streamlit")
