import streamlit as st


def show():
    # Estado de la barra
    if "nav_open" not in st.session_state:
        st.session_state.nav_open = True

    # Botón para contraer / expandir
    col_btn, _ = st.columns([1, 20])
    with col_btn:
        if st.button("☰" if not st.session_state.nav_open else "✕", key="toggle_nav"):
            st.session_state.nav_open = not st.session_state.nav_open
            st.rerun()

    # CSS dinámico según estado
    if st.session_state.nav_open:
        sidebar_width = "18rem"
        margin_left = "0rem"
    else:
        sidebar_width = "4.5rem"
        margin_left = "-13.5rem"

    custom_style = f"""
    <style>
    [data-testid="stSidebarNav"] {{
        display: none;
    }}

    header {{
        visibility: hidden;
    }}

    [data-testid="stSidebar"] {{
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
        transition: all 0.3s ease-in-out;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        transition: margin-left 0.3s ease-in-out;
        margin-left: {margin_left} !important;
    }}
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

    with st.sidebar:
        if st.session_state.nav_open:
            st.title("📌 Navegación")

            st.markdown("---")
            st.markdown("### Secciones")

            if st.button("🏠 Inicio"):
                st.switch_page("app.py")

            if st.button("🟦 SQL"):
                st.switch_page("pages/SQL.py")

            if st.button("📈 Series de tiempo"):
                st.switch_page("pages/series_tiempo.py")

            if st.button("💰 Modelado financiero"):
                st.switch_page("pages/modelado_financiero.py")

            if st.button("🤖 Machine Learning"):
                st.write("Próximamente")

            st.markdown("---")
            st.markdown("### Enlaces")
            st.link_button("GitHub", "https://github.com/LuisMantilla28/portfolio_streamlit")
            st.link_button("LinkedIn", "https://www.linkedin.com/in/luis-enrique-mantilla-sanabria-905a01271/")
        else:
            st.markdown("## 📌")
