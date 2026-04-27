import streamlit as st


def show():
    custom_style = """
     <style>
    [data-testid="stSidebarNav"] {
        display: none;
    }

    [data-testid="stSidebar"] {
        min-width: 18rem !important;
        max-width: 18rem !important;
    }
    </style>
    """
    st.markdown(custom_style, unsafe_allow_html=True)

    with st.sidebar:
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
            st.switch_page("pages/ML.pyy")

        st.markdown("---")
        st.markdown("### Enlaces")
        st.link_button("GitHub", "https://github.com/LuisMantilla28/portfolio_streamlit")
        st.link_button("LinkedIn", "https://www.linkedin.com/in/luis-enrique-mantilla-sanabria-905a01271/")
