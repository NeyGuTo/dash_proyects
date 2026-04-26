"""Dashboard SUNAT — Exportaciones del Perú 2005-2026."""
import pandas as pd
import plotly.express as px
import streamlit as st

from sunat.data_loader import load_long

st.set_page_config(
    page_title="Exportaciones SUNAT — Perú",
    page_icon="📦",
    layout="wide",
)

# ---------- Datos ----------
@st.cache_data(show_spinner="Cargando datos SUNAT...")
def get_data() -> pd.DataFrame:
    return load_long()

df = get_data()

MESES_NOMBRE = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
                "Jul", "Ago", "Set", "Oct", "Nov", "Dic"]

# ---------- Sidebar ----------
st.sidebar.title("Filtros")

anios = sorted(df["anio"].unique())
anio_min, anio_max = st.sidebar.select_slider(
    "Rango de años",
    options=anios,
    value=(anios[0], anios[-1]),
)

categorias_opt = ["(Todas)"] + sorted(df["categoria"].unique())
categoria_sel = st.sidebar.selectbox("Categoría", categorias_opt)

mask = df["anio"].between(anio_min, anio_max)
if categoria_sel != "(Todas)":
    mask &= df["categoria"] == categoria_sel
df_f = df[mask].copy()

subsectores_opt = ["(Todos)"] + sorted(df_f["subsector"].unique())
subsector_sel = st.sidebar.selectbox("Subsector", subsectores_opt)
if subsector_sel != "(Todos)":
    df_f = df_f[df_f["subsector"] == subsector_sel]

productos_opt = ["(Todos)"] + sorted(df_f["producto"].unique())
producto_sel = st.sidebar.selectbox("Producto", productos_opt)
if producto_sel != "(Todos)":
    df_f = df_f[df_f["producto"] == producto_sel]

st.sidebar.markdown("---")
st.sidebar.caption(f"Filas filtradas: **{len(df_f):,}**")
st.sidebar.caption("Fuente: SUNAT — Valor FOB en USD")

# ---------- Header ----------
st.title("📦 Exportaciones del Perú — SUNAT")
st.caption(f"Periodo seleccionado: **{anio_min} – {anio_max}**")

# ---------- KPIs ----------
total_usd = df_f["valor_usd"].sum()
n_anios = df_f["anio"].nunique()
prom_anual = total_usd / n_anios if n_anios else 0

# Top producto y top categoría dentro del filtro
top_producto = (
    df_f.groupby("producto")["valor_usd"].sum().sort_values(ascending=False)
)
top_prod_nombre = top_producto.index[0] if len(top_producto) else "—"
top_prod_valor = top_producto.iloc[0] if len(top_producto) else 0

share_minero = 0.0
if total_usd:
    minero = df_f[df_f["subsector"].str.contains("Minero", case=False, na=False)]["valor_usd"].sum()
    share_minero = 100 * minero / total_usd

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total exportado", f"US$ {total_usd/1e9:,.2f} B")
c2.metric("Promedio anual", f"US$ {prom_anual/1e9:,.2f} B")
c3.metric("Top producto", top_prod_nombre, f"US$ {top_prod_valor/1e9:,.2f} B")
c4.metric("% Minero", f"{share_minero:,.1f}%")

st.markdown("---")

# ---------- Gráfico 1: evolución anual por categoría ----------
st.subheader("Evolución anual por categoría")
ev = (
    df_f.groupby(["anio", "categoria"], as_index=False)["valor_usd"].sum()
)
ev["valor_musd"] = ev["valor_usd"] / 1e6
fig_line = px.area(
    ev,
    x="anio",
    y="valor_musd",
    color="categoria",
    labels={"valor_musd": "Millones USD", "anio": "Año", "categoria": "Categoría"},
    template="plotly_white",
)
fig_line.update_layout(hovermode="x unified", height=420)
st.plotly_chart(fig_line, use_container_width=True)

# ---------- Fila 2: Treemap + Top 10 ----------
col_left, col_right = st.columns([1.1, 1])

with col_left:
    st.subheader(f"Composición jerárquica ({anio_min}–{anio_max})")
    tm = df_f.groupby(["categoria", "subsector", "producto"], as_index=False)["valor_usd"].sum()
    tm = tm[tm["valor_usd"] > 0]
    if len(tm):
        fig_tm = px.treemap(
            tm,
            path=["categoria", "subsector", "producto"],
            values="valor_usd",
            color="valor_usd",
            color_continuous_scale="Blues",
        )
        fig_tm.update_layout(height=480, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_tm, use_container_width=True)
    else:
        st.info("No hay datos para los filtros seleccionados.")

with col_right:
    st.subheader("Top 10 productos")
    top10 = (
        df_f.groupby("producto", as_index=False)["valor_usd"].sum()
        .sort_values("valor_usd", ascending=True)
        .tail(10)
    )
    top10["valor_musd"] = top10["valor_usd"] / 1e6
    fig_bar = px.bar(
        top10,
        x="valor_musd",
        y="producto",
        orientation="h",
        text="valor_musd",
        labels={"valor_musd": "Millones USD", "producto": ""},
        template="plotly_white",
    )
    fig_bar.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_bar.update_layout(height=480, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)

# ---------- Heatmap mes vs año ----------
st.subheader("Estacionalidad mensual (heatmap)")
hm = (
    df_f.groupby(["anio", "mes"], as_index=False)["valor_usd"].sum()
    .pivot(index="mes", columns="anio", values="valor_usd")
    .reindex(range(1, 13))
)
hm.index = MESES_NOMBRE
fig_hm = px.imshow(
    hm / 1e6,
    aspect="auto",
    color_continuous_scale="YlOrRd",
    labels=dict(x="Año", y="Mes", color="Millones USD"),
)
fig_hm.update_layout(height=380)
st.plotly_chart(fig_hm, use_container_width=True)

# ---------- Tabla ----------
with st.expander("📋 Ver datos filtrados"):
    st.dataframe(
        df_f.sort_values(["anio", "mes"]).reset_index(drop=True),
        use_container_width=True,
    )
