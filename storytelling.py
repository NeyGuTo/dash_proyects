import streamlit as st

from storytelling.theme import inject_styles
from storytelling.views import render_cuadro_dashboard, render_datos_dashboard


st.set_page_config(page_title="Storytelling ABC", page_icon=":bar_chart:", layout="wide")


def main() -> None:
    inject_styles()
    st.markdown(
        """
        <div class="hero">
            <h1>Compras 2024</h1>
            <p>Dashboard narrativo para análisis de compras, inventario y rotación por clases ABC.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    tab_datos, tab_cuadro = st.tabs(["DATOS", "CUADRO"])
    with tab_datos:
        render_datos_dashboard()
    with tab_cuadro:
        render_cuadro_dashboard()


if __name__ == "__main__":
    main()
