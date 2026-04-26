import pandas as pd
import plotly.express as px
import streamlit as st

from laboratorio.analytics import (
    apply_filters,
    exam_adjusted_monthly_stats,
    area_usage,
    exam_monthly_stats,
    exam_summary_table,
    format_int,
    monthly_consumption,
    monthly_summary_table,
    six_month_average,
)
from laboratorio.config import TARGET_EXAMS
from laboratorio.data_loader import load_lab_data
from laboratorio.sismed import sismed_static_data


st.set_page_config(
    page_title="Analisis de Laboratorio",
    page_icon="",
    layout="wide",
)


PLOTLY_AXIS_COLOR = "#243b53"
PLOTLY_GRID_COLOR = "rgba(36, 59, 83, 0.18)"
PLOTLY_PAPER_BG = "rgba(255,255,255,0.72)"


def inject_styles():
    st.markdown(
        """
        <style>
        :root {
            --ink-strong: #0f172a;
            --ink-soft: #475569;
            --accent: #0f766e;
            --accent-soft: #0ea5a4;
            --accent-warm: #d97706;
            --surface: #ffffff;
            --surface-soft: #f8fafc;
            --stroke-soft: rgba(15, 23, 42, 0.10);
        }
        .stApp {
            background:
                linear-gradient(180deg, #eef2f7 0%, #f4f7fb 42%, #eef3f8 100%);
            color: var(--ink-strong);
        }
        [data-testid="block-container"] {
            max-width: 1380px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        .stApp, .stApp p, .stApp label, .stApp div, .stApp span {
            color: var(--ink-strong);
        }
        [data-testid="stAppViewContainer"] {
            color: var(--ink-strong);
        }
        [data-testid="stHeader"] {
            background: rgba(244, 247, 251, 0.92);
            border-bottom: 1px solid rgba(15, 23, 42, 0.06);
        }
        h1, h2, h3, h4, h5, h6 {
            color: var(--ink-strong) !important;
        }
        .hero {
            padding: 0.35rem 0 0.55rem 0;
            margin-bottom: 0.55rem;
        }
        .hero h1 {
            margin: 0;
            font-size: 1.95rem;
            line-height: 1.02;
            max-width: 900px;
            color: var(--ink-strong) !important;
        }
        .section-head {
            margin: 0.25rem 0 0.9rem 0;
            padding: 0.8rem 1rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 10px 20px rgba(15, 23, 42, 0.05);
        }
        .section-title {
            font-size: 1.32rem;
            font-weight: 800;
            color: var(--ink-strong) !important;
            margin: 0;
        }
        .panel-card {
            background: rgba(255,255,255,0.98);
            border: 1px solid var(--stroke-soft);
            border-radius: 18px;
            padding: 0.95rem 0.95rem 0.3rem 0.95rem;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
            height: 100%;
        }
        [data-testid="stPlotlyChart"] {
            background: rgba(255,255,255,0.98);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 0.35rem 0.35rem 0 0.35rem;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
        }
        .empty-state {
            padding: 1rem 1.15rem;
            border-radius: 16px;
            background: linear-gradient(180deg, #fff7ed 0%, #fffbf5 100%);
            border: 1px solid rgba(244, 162, 89, 0.35);
            color: #7c2d12 !important;
            margin-top: 0.4rem;
        }
        .product-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 1rem;
            margin-bottom: 1rem;
        }
        .product-card {
            position: relative;
            overflow: hidden;
            background: rgba(255,255,255,0.98);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 18px;
            padding: 1rem 1.05rem;
            box-shadow: 0 14px 26px rgba(15, 23, 42, 0.08);
        }
        .product-card::before {
            content: "";
            position: absolute;
            inset: 0 0 auto 0;
            height: 4px;
            background: linear-gradient(90deg, #0f766e 0%, #0ea5a4 55%, #d97706 100%);
        }
        .product-card h3 {
            margin: 0.4rem 0 0.8rem 0;
            font-size: 1.02rem;
            color: #111827 !important;
        }
        .product-line {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            padding: 0.45rem 0;
            border-bottom: 1px solid rgba(17, 24, 39, 0.08);
        }
        .product-line:last-child {
            border-bottom: none;
        }
        .product-label {
            color: #486581 !important;
            font-size: 0.92rem;
        }
        .product-value {
            color: #102a43 !important;
            font-weight: 700;
        }
        .adjusted-note {
            margin-top: 0.45rem;
            margin-bottom: 1.5rem;
            padding: 0.55rem 0.7rem;
            border-radius: 12px;
            background: rgba(245, 158, 11, 0.12);
            border-left: 4px solid #d97706;
            color: #92400e !important;
            font-size: 0.88rem;
            font-weight: 700;
            line-height: 1.35;
        }
        [data-testid="stSidebar"] {
            display: none;
        }
        [data-testid="stMetricValue"],
        [data-testid="stMetricLabel"],
        [data-testid="stMetricDelta"] {
            color: var(--ink-strong) !important;
        }
        [data-testid="stMetric"] {
            background: rgba(255,255,255,0.98);
            border: 1px solid rgba(15, 23, 42, 0.08);
            padding: 1rem;
            border-radius: 18px;
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.08);
        }
        [data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            font-weight: 700 !important;
            color: #374151 !important;
        }
        [data-testid="stMetricValue"] {
            font-size: 2rem !important;
            font-weight: 800 !important;
            color: #111827 !important;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.45rem;
            margin-bottom: 0.55rem;
            padding: 0.35rem;
            border-radius: 16px;
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(15, 23, 42, 0.06);
            width: fit-content;
        }
        .stTabs [data-baseweb="tab"] {
            color: var(--ink-soft) !important;
            background: rgba(255,255,255,0.96);
            border: 1px solid rgba(17, 24, 39, 0.08);
            border-radius: 12px;
            padding: 0.58rem 1rem;
            box-shadow: none;
        }
        .stTabs [aria-selected="true"] {
            color: var(--ink-strong) !important;
            font-weight: 700;
            background: #ffffff !important;
            border-color: rgba(15, 23, 42, 0.10) !important;
            box-shadow: inset 0 -3px 0 #0ea5a4;
        }
        .stButton > button, .stDownloadButton > button {
            background: linear-gradient(135deg, #111827 0%, #1f2937 60%, #0f766e 100%);
            color: #ffffff !important;
            border: none;
            border-radius: 14px;
            box-shadow: 0 14px 24px rgba(17, 24, 39, 0.18);
            font-weight: 700;
        }
        .stButton > button:hover, .stDownloadButton > button:hover {
            background: linear-gradient(135deg, #0b1220 0%, #0f172a 60%, #115e59 100%);
            color: #ffffff !important;
        }
        [data-testid="stDataFrame"] {
            background: rgba(255, 255, 255, 0.94);
            border-radius: 16px;
            border: 1px solid rgba(17, 24, 39, 0.08);
            box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
        }
        .stCaption, [data-testid="stCaptionContainer"] {
            color: #4b5563 !important;
        }
        .stMarkdown, .stText, .stSubheader, .stHeader {
            color: var(--ink-strong) !important;
        }
        @media (max-width: 900px) {
            .hero h1 {
                font-size: 1.7rem;
            }
            .product-grid {
                grid-template-columns: 1fr;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def get_data():
    return load_lab_data()


def style_plotly_figure(figure):
    figure.update_layout(
        template="plotly_white",
        font=dict(color=PLOTLY_AXIS_COLOR, family="Arial"),
        title_font=dict(color="#102a43", size=22),
        legend_title_font=dict(color=PLOTLY_AXIS_COLOR),
        legend_font=dict(color=PLOTLY_AXIS_COLOR),
        paper_bgcolor=PLOTLY_PAPER_BG,
        plot_bgcolor="rgba(255,255,255,0.0)",
        margin=dict(l=20, r=20, t=60, b=20),
    )
    figure.update_xaxes(
        title_font=dict(color=PLOTLY_AXIS_COLOR),
        tickfont=dict(color=PLOTLY_AXIS_COLOR),
        gridcolor=PLOTLY_GRID_COLOR,
        zerolinecolor=PLOTLY_GRID_COLOR,
    )
    figure.update_yaxes(
        title_font=dict(color=PLOTLY_AXIS_COLOR),
        tickfont=dict(color=PLOTLY_AXIS_COLOR),
        gridcolor=PLOTLY_GRID_COLOR,
        zerolinecolor=PLOTLY_GRID_COLOR,
    )
    return figure


def build_line_chart(data, title):
    if data.empty:
        return None

    chart_data = data.sort_values(["AÑO", "MES_NUM", "EXAMEN"]).copy()
    if chart_data["AÑO"].nunique() == 1:
        chart_data["MES_LABEL"] = chart_data["MES"].str.title()
    else:
        chart_data["MES_LABEL"] = (
            chart_data["MES"].str.title() + " " + chart_data["AÑO"].astype(str)
        )

    figure = px.line(
        chart_data,
        x="MES_LABEL",
        y="TOTAL",
        color="EXAMEN",
        markers=True,
        title=title,
        color_discrete_sequence=["#0b6e4f", "#f4a259", "#3d5a80"],
        category_orders={"MES_LABEL": chart_data["MES_LABEL"].drop_duplicates().tolist()},
    )
    figure.update_layout(
        legend_title_text="Examen",
        xaxis_title="Mes",
        yaxis_title="Consumo",
    )
    return style_plotly_figure(figure)


def build_area_chart(data, title):
    if data.empty:
        return None

    figure = px.bar(
        data,
        x="AREA",
        y="CANTIDAD",
        color="EXAMEN",
        barmode="group",
        title=title,
        color_discrete_sequence=["#0b6e4f", "#f4a259", "#3d5a80"],
    )
    figure.update_layout(
        xaxis_title="Area de uso",
        yaxis_title="Cantidad",
        legend_title_text="Examen",
    )
    return style_plotly_figure(figure)


def build_sismed_chart(data):
    if data.empty:
        return None

    chart_data = data.melt(
        id_vars=["EXAMEN"],
        value_vars=["INGRESOS_TOTALES", "SALIDAS_TOTALES", "STOCK_FINAL"],
        var_name="METRICA",
        value_name="VALOR",
    )
    figure = px.bar(
        chart_data,
        x="EXAMEN",
        y="VALOR",
        color="METRICA",
        barmode="group",
        title="Abastecimiento por examen",
        color_discrete_sequence=["#0b6e4f", "#f4a259", "#3d5a80"],
    )
    figure.update_layout(
        xaxis_title="Examen",
        yaxis_title="Cantidad",
    )
    return style_plotly_figure(figure)


def build_sismed_coverage_chart(data):
    if data.empty:
        return None

    chart_data = data.melt(
        id_vars=["EXAMEN"],
        value_vars=["PROMEDIO_MENSUAL_6M", "STOCK_FINAL"],
        var_name="METRICA",
        value_name="VALOR",
    )
    figure = px.bar(
        chart_data,
        x="EXAMEN",
        y="VALOR",
        color="METRICA",
        barmode="group",
        title="Consumo promedio 6 meses vs stock en almacén",
        color_discrete_sequence=["#f4a259", "#3d5a80"],
    )
    figure.update_layout(
        xaxis_title="Examen",
        yaxis_title="Cantidad",
    )
    return style_plotly_figure(figure)


def show_exam_totals(data):
    if data.empty:
        return
    totals = data.groupby("EXAMEN", as_index=False)["TOTAL"].sum()
    columns = st.columns(len(TARGET_EXAMS))
    totals_map = {row["EXAMEN"]: row["TOTAL"] for _, row in totals.iterrows()}
    for index, exam in enumerate(TARGET_EXAMS):
        columns[index].metric(exam.title(), format_int(totals_map.get(exam, 0)))


def show_exam_monthly_averages(data):
    stats = exam_monthly_stats(data)
    adjusted_stats = exam_adjusted_monthly_stats(data)
    columns = st.columns(len(TARGET_EXAMS))
    for index, exam in enumerate(TARGET_EXAMS):
        with columns[index]:
            st.metric(
                f"Consumo Promedio Mensual {exam.title()}",
                format_int(stats["promedios_por_examen"][exam]),
                help=f"Total {format_int(stats['totales_por_examen'][exam])} / {stats['meses_analizados']} meses analizados",
            )
            adjusted_months = adjusted_stats["meses_ajustados_por_examen"][exam]
            total_months = stats["meses_analizados"]
            adjusted_value = adjusted_stats["promedios_ajustados_por_examen"][exam]
            if adjusted_months and adjusted_months < total_months:
                st.markdown(
                    f"""
                    <div class="adjusted-note">
                        Consumo Promedio ajustado: {format_int(adjusted_value)}<br>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def render_section_header(title):
    st.markdown(
        f"""
        <div class="section-head">
            <div class="section-title">{title}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sismed_product_cards(data):
    columns = st.columns(len(data))
    for column, (_, row) in zip(columns, data.iterrows()):
        with column:
            st.markdown(
                f"""
                <div class="product-card">
                    <h3>{row['EXAMEN']}</h3>
                    <div class="product-line">
                        <span class="product-label">Ingresos totales</span>
                        <span class="product-value">{format_int(row['INGRESOS_TOTALES'])}</span>
                    </div>
                    <div class="product-line">
                        <span class="product-label">Salidas totales</span>
                        <span class="product-value">{format_int(row['SALIDAS_TOTALES'])}</span>
                    </div>
                    <div class="product-line">
                        <span class="product-label">Stock en almacén</span>
                        <span class="product-value">{format_int(row['STOCK_FINAL'])}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def build_sismed_analysis_table(data):
    analysis_df = data[
        ["EXAMEN", "PROMEDIO_MENSUAL_6M", "STOCK_FINAL", "MESES_DISPONIBLES_STOCK"]
    ].copy()
    analysis_df["BRECHA_STOCK"] = analysis_df["STOCK_FINAL"] - analysis_df["PROMEDIO_MENSUAL_6M"]
    analysis_df["ESTADO_SEMAFORO"] = analysis_df["MESES_DISPONIBLES_STOCK"].apply(
        lambda value: "Rojo" if value < 2 else "Amarillo" if value <= 4 else "Verde"
    )
    return analysis_df


def render_summary_section(title, data, download_name):
    render_section_header(title)
    if data.empty:
        st.markdown(
            """
            <div class="empty-state">
                No hay datos disponibles para esta vista. Revisa que en los filtros de la izquierda haya al menos un año y un examen seleccionados.
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    show_exam_totals(data)
    show_exam_monthly_averages(data)

    monthly_df = monthly_consumption(data)
    area_df = area_usage(data)
    month_table = monthly_summary_table(data)
    exam_table = exam_summary_table(data)

    col1, col2 = st.columns([1.35, 1])
    with col1:
        line_chart = build_line_chart(monthly_df, "Consumo mensual por examen")
        if line_chart:
            st.plotly_chart(line_chart, use_container_width=True)
    with col2:
        area_chart = build_area_chart(area_df, "Distribucion por area de uso")
        if area_chart:
            st.plotly_chart(area_chart, use_container_width=True)

    table_col1, table_col2 = st.columns(2)
    with table_col1:
        st.markdown("**Resumen mensual**")
        st.dataframe(month_table, use_container_width=True, hide_index=True)
    with table_col2:
        st.markdown("**Resumen por examen**")
        st.dataframe(exam_table, use_container_width=True, hide_index=True)

def main():
    inject_styles()
    st.markdown(
        """
        <div class="hero">
            <h1>Análisis de consumo de laboratorio</h1>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data, issues = get_data()

    years_selected = [2025, 2026]
    exams_selected = TARGET_EXAMS.copy()

    if data.empty:
        st.error(
            "No se pudieron cargar datos de laboratorio. Revisa los archivos Excel y las dependencias."
        )
        if issues:
            with st.expander("Detalle de errores"):
                for issue in issues:
                    st.write(f"- {issue}")
        st.stop()

    data_2025 = apply_filters(data, [2025], exams_selected)
    data_2026 = apply_filters(data, [2026], exams_selected)
    if issues:
        with st.expander("Advertencias de carga"):
            for issue in issues:
                st.write(f"- {issue}")

    tabs = st.tabs(
        [
            "Año 2025",
            "Año 2026",
            "SISMED",
        ]
    )

    with tabs[0]:
        render_summary_section("Analisis año 2025", data_2025, "laboratorio_2025.xlsx")

    with tabs[1]:
        render_summary_section("Analisis año 2026", data_2026, "laboratorio_2026.xlsx")

    with tabs[2]:
        render_section_header("SISMED")
        sismed_df = sismed_static_data()
        average_df = six_month_average(data).rename(columns={"EXAMEN": "EXAMEN_BASE"})
        sismed_df = sismed_df.merge(average_df, on="EXAMEN_BASE", how="left").fillna(0)
        sismed_df["MESES_DISPONIBLES_STOCK"] = sismed_df.apply(
            lambda row: (row["STOCK_FINAL"] / row["PROMEDIO_MENSUAL_6M"])
            if row["PROMEDIO_MENSUAL_6M"]
            else 0,
            axis=1,
        )

        if sismed_df.empty:
            st.info("No hay datos suficientes para SISMED.")
        else:
            render_sismed_product_cards(sismed_df)
            analysis_df = build_sismed_analysis_table(sismed_df)

            sis_chart = build_sismed_chart(sismed_df)
            if sis_chart:
                st.plotly_chart(sis_chart, use_container_width=True)

            coverage_col1, coverage_col2 = st.columns([1.2, 1])
            with coverage_col1:
                coverage_chart = build_sismed_coverage_chart(sismed_df)
                if coverage_chart:
                    st.plotly_chart(coverage_chart, use_container_width=True)
            with coverage_col2:
                st.markdown("**Cobertura según consumo promedio de 6 meses**")
                st.dataframe(
                    analysis_df[
                        [
                            "EXAMEN",
                            "PROMEDIO_MENSUAL_6M",
                            "STOCK_FINAL",
                            "MESES_DISPONIBLES_STOCK",
                        ]
                    ].rename(
                        columns={
                            "EXAMEN": "Examen",
                            "PROMEDIO_MENSUAL_6M": "Consumo promedio 6 meses",
                            "STOCK_FINAL": "Stock final en almacén",
                            "MESES_DISPONIBLES_STOCK": "Cobertura en meses",
                        }
                    ),
                    use_container_width=True,
                    hide_index=True,
                )

if __name__ == "__main__":
    main()
