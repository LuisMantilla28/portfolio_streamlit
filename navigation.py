import streamlit as st

def show():
    # Ocultar menú nativo de Streamlit
    hide_streamlit_style = """
    <style>
    [data-testid="stSidebarNav"] {display: none;}
    header {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

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
        st.link_button("GitHub", "https://github.com/tu_usuario")
        st.link_button("LinkedIn", "https://www.linkedin.com/in/tu_usuario/")
