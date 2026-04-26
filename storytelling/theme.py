import streamlit as st


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg-1: #070d1a;
            --bg-2: #101a2e;
            --ink: #f8fbff;
            --soft-ink: #d3def0;
            --card: rgba(17, 25, 42, 0.96);
            --stroke: rgba(148, 163, 184, 0.34);
            --accent: #7dd3fc;
            --accent-2: #38bdf8;
        }
        .stApp {
            background: radial-gradient(circle at top left, #1d315a 0%, var(--bg-1) 38%, var(--bg-2) 100%);
            color: var(--ink);
        }
        .stApp p, .stApp span, .stApp div, .stApp label, .stMarkdown, .stCaption, h1, h2, h3 {
            color: var(--ink);
        }
        [data-testid="block-container"] {
            max-width: 1380px;
            padding-top: 1.6rem;
            padding-bottom: 2.1rem;
        }
        [data-testid="stHeader"] {
            background: rgba(11, 18, 32, 0.78);
            border-bottom: 1px solid var(--stroke);
        }
        .hero {
            margin: 0 0 0.65rem 0;
            padding: 0.9rem 1rem;
            background: var(--card);
            border-radius: 16px;
            border: 1px solid var(--stroke);
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
            position: relative;
            overflow: hidden;
        }
        .hero::before {
            content: "";
            position: absolute;
            left: 0;
            top: 0;
            width: 100%;
            height: 4px;
            background: linear-gradient(90deg, var(--accent) 0%, var(--accent-2) 55%, #22d3ee 100%);
        }
        .hero h1 {
            margin: 0;
            color: var(--ink);
            font-size: 1.8rem;
            line-height: 1.1;
        }
        .hero p {
            margin: 0.25rem 0 0;
            color: var(--soft-ink);
            font-size: 0.95rem;
        }
        [data-testid="stMetric"] {
            background: var(--card);
            border: 1px solid var(--stroke);
            border-radius: 16px;
            padding: 0.9rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
        }
        [data-testid="stMetricLabel"] {
            color: var(--soft-ink) !important;
            font-weight: 700 !important;
        }
        [data-testid="stMetricValue"] {
            color: var(--ink) !important;
            font-weight: 800 !important;
        }
        [data-testid="stMetricDelta"] {
            color: var(--soft-ink) !important;
        }
        [data-testid="stPlotlyChart"],
        [data-testid="stDataFrame"] {
            background: var(--card);
            border: 1px solid var(--stroke);
            border-radius: 16px;
            padding: 0.4rem;
            box-shadow: 0 10px 24px rgba(0, 0, 0, 0.35);
        }
        [data-testid="stSidebar"] {
            background: rgba(11, 18, 32, 0.96);
            border-right: 1px solid var(--stroke);
        }
        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
            color: var(--ink) !important;
        }
        [data-testid="stSidebar"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-baseweb="tag"],
        [data-testid="stSidebar"] [data-baseweb="select"] input,
        [data-testid="stSidebar"] [data-baseweb="popover"] {
            background: rgba(30, 41, 59, 0.95) !important;
            color: var(--ink) !important;
            border-color: rgba(148, 163, 184, 0.38) !important;
        }
        [data-testid="stSelectbox"] div, [data-testid="stMultiSelect"] div, [data-testid="stSlider"] * {
            color: var(--ink) !important;
        }
        h2, h3 {
            color: var(--ink) !important;
            letter-spacing: 0.2px;
        }
        h3 {
            border-left: 4px solid var(--accent);
            padding-left: 0.55rem;
            margin-top: 1rem;
        }
        .stCaption {
            color: var(--soft-ink) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def style_figure(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#f8fbff"),
        colorway=["#7dd3fc", "#38bdf8", "#22d3ee", "#a78bfa", "#34d399", "#f59e0b"],
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fbff")),
        title=dict(font=dict(color="#f8fbff", size=20)),
        hoverlabel=dict(
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="rgba(125, 211, 252, 0.65)",
            font=dict(color="#f8fbff"),
        ),
        uniformtext_minsize=11,
        uniformtext_mode="hide",
        margin=dict(l=30, r=30, t=70, b=40),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.22)",
        zeroline=False,
        linecolor="rgba(203,213,225,0.35)",
        tickfont=dict(color="#e6eefc"),
        title_font=dict(color="#f8fbff"),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor="rgba(148,163,184,0.22)",
        zeroline=False,
        linecolor="rgba(203,213,225,0.35)",
        tickfont=dict(color="#e6eefc"),
        title_font=dict(color="#f8fbff"),
    )
    return fig

