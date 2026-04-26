import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from storytelling.data_pipeline import fmt_currency, load_cuadro_data, load_data
from storytelling.theme import style_figure


def _clean_sku(value) -> str:
    text = str(value).strip()
    return text[:-2] if text.endswith(".0") else text


def _render_status_cards(cuadro_df, col):
    st.subheader("Indicadores visuales y recomendación")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(cuadro_df.iterrows()):
        status = row["STATUS_INVENTARIO"]
        clase = row[col["clase"]]
        rec = row["RECOMENDACION"] or row[col["analysis"]]
        diff = row[col["diff"]]
        tone = "#f59e0b" if status == "SOBRESTOCK" else "#22c55e" if status == "DEFICIT" else "#38bdf8"
        cols[idx].markdown(
            f"""
            <div style="
                background: rgba(15,23,42,0.92);
                border: 1px solid rgba(148,163,184,0.35);
                border-left: 6px solid {tone};
                border-radius: 14px;
                padding: 0.7rem 0.8rem;
                min-height: 150px;
            ">
                <div style="font-size:0.9rem;color:#cbd5e1;font-weight:700;">Clase {clase}</div>
                <div style="font-size:1.05rem;color:#f8fbff;font-weight:800;margin:0.15rem 0 0.35rem 0;">{status}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Diferencia: {diff:,.0f}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;margin-top:0.4rem;">Recomendación: {rec}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_cuadro_resumen_cards(cuadro_df, col):
    st.subheader("Resumen por clase")
    cols = st.columns(3)
    for idx, (_, row) in enumerate(cuadro_df.iterrows()):
        clase = row[col["clase"]]
        ventas = row[col["ventas"]]
        rotacion = row[col["rotacion"]]
        inv_std = row[col["inv_std"]]
        inv_real = row[col["inv_real"]]
        diff_pct = row[col["diff_pct"]]
        analisis = row[col["analysis"]]
        cols[idx].markdown(
            f"""
            <div style="
                background: rgba(17,25,42,0.96);
                border: 1px solid rgba(148,163,184,0.35);
                border-radius: 14px;
                padding: 0.75rem 0.85rem;
                min-height: 220px;
            ">
                <div style="font-size:0.95rem;color:#7dd3fc;font-weight:800;">Clase {clase}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Ventas: {ventas:,.0f}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Rotación: {rotacion:,.2f}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Inventario estándar: {inv_std:,.0f}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Inventario real: {inv_real:,.0f}</div>
                <div style="font-size:0.88rem;color:#e2e8f0;">Diferencia %: {diff_pct:.2%}</div>
                <div style="font-size:0.84rem;color:#cbd5e1;margin-top:0.35rem;">Análisis: {analisis}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_datos_dashboard():
    try:
        df, col = load_data()
    except Exception as exc:
        st.error(f"Error cargando datos DATOS: {exc}")
        st.info("Ejecuta con un entorno que tenga instalados: streamlit, pandas, plotly, openpyxl")
        return

    st.sidebar.header("Filtros DATOS")
    abc_options = sorted([v for v in df[col["abc"]].dropna().unique() if str(v).strip()])
    proveedor_options = sorted([v for v in df[col["proveedor"]].dropna().unique() if str(v).strip()])
    grupo_options = sorted([v for v in df[col["grupo"]].dropna().unique() if str(v).strip()])

    selected_abc = st.sidebar.multiselect("CLASE ABC", options=abc_options, default=abc_options, key="datos_abc")
    selected_proveedor = st.sidebar.multiselect(
        "PROVEEDOR", options=proveedor_options, default=proveedor_options, key="datos_proveedor"
    )
    selected_grupo = st.sidebar.multiselect(
        "GRUPO DE MATERIAL", options=grupo_options, default=grupo_options, key="datos_grupo"
    )

    filtered = df[
        df[col["abc"]].isin(selected_abc)
        & df[col["proveedor"]].isin(selected_proveedor)
        & df[col["grupo"]].isin(selected_grupo)
    ].copy()

    filtered = filtered.sort_values(by=col["total"], ascending=False).reset_index(drop=True)
    total_compra = filtered[col["total"]].sum()
    num_skus = filtered[col["sku"]].nunique()
    compra_promedio = total_compra / num_skus if num_skus else 0

    top_row = filtered.iloc[0] if not filtered.empty else None
    top_sku = _clean_sku(top_row[col["sku"]]) if top_row is not None else "N/A"
    top_sku_compra = top_row[col["total"]] if top_row is not None else 0
    top_sku_desc = top_row[col["descripcion"]] if top_row is not None else "Sin descripción"

    filtered["ACUM_COMPRAS_CALC"] = filtered[col["total"]].cumsum()
    filtered["PCT_ACUM_COMPRA_CALC"] = (
        (filtered["ACUM_COMPRAS_CALC"] / total_compra) if total_compra > 0 else 0
    )

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total compra", fmt_currency(total_compra))
    k2.metric("Número de SKUs", f"{num_skus:,}")
    k3.metric("Compra promedio", fmt_currency(compra_promedio))
    k4.metric("SKU con mayor compra", top_sku)

    st.markdown(
        f"""
        <div style="
            background: rgba(15,23,42,0.92);
            border: 1px solid rgba(148,163,184,0.35);
            border-radius: 14px;
            padding: 0.75rem 0.9rem;
            margin-top: 0.35rem;
            margin-bottom: 0.35rem;
        ">
            <div style="font-size:0.9rem;color:#cbd5e1;font-weight:700;">Detalle SKU con mayor compra</div>
            <div style="font-size:1rem;color:#f8fbff;"><b>Código:</b> {top_sku}</div>
            <div style="font-size:1rem;color:#f8fbff;"><b>Compra:</b> {fmt_currency(top_sku_compra)}</div>
            <div style="font-size:0.95rem;color:#e2e8f0;"><b>Descripción:</b> {top_sku_desc}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Riesgo")
    estrategia_up = filtered[col["estrategia"]].astype(str).str.upper()
    proveedor_up = filtered[col["proveedor"]].astype(str).str.upper()

    risk_lead = int((filtered[col["lead"]] > 45).sum())
    risk_mto = int(estrategia_up.str.contains("MTO", na=False).sum())
    risk_import = int(
        proveedor_up.str.contains("IMPORT", na=False).sum()
        + estrategia_up.str.contains("IMPORT", na=False).sum()
        - (proveedor_up.str.contains("IMPORT", na=False) & estrategia_up.str.contains("IMPORT", na=False)).sum()
    )

    r1, r2, r3 = st.columns(3)
    r1.metric("Ítems lead time > 45", f"{risk_lead:,}")
    r2.metric("Ítems MTO", f"{risk_mto:,}")
    r3.metric("Ítems importados", f"{risk_import:,}")

    st.subheader("ABC")
    abc_summary = (
        filtered.groupby(col["abc"], as_index=False)
        .agg(
            compras=(col["total"], "sum"),
            skus=(col["sku"], "nunique"),
        )
        .sort_values("compras", ascending=False)
    )

    a1, a2 = st.columns(2)
    with a1:
        fig_abc_bar = px.bar(
            abc_summary,
            x=col["abc"],
            y="compras",
            text="compras",
            title="Compras por CLASE ABC",
        )
        fig_abc_bar.update_traces(
            texttemplate="%{text:,.0f}",
            textposition="outside",
            textfont=dict(color="#f8fbff", size=12),
            cliponaxis=False,
        )
        fig_abc_bar.update_layout(yaxis_title="Compra")
        st.plotly_chart(style_figure(fig_abc_bar), use_container_width=True)

    with a2:
        fig_abc_pie = px.pie(
            abc_summary,
            names=col["abc"],
            values="compras",
            hole=0.5,
            title="Participación ABC",
        )
        fig_abc_pie.update_traces(
            textfont=dict(color="#f8fbff", size=12),
            insidetextfont=dict(color="#f8fbff"),
            marker=dict(line=dict(color="#0f172a", width=2)),
        )
        st.plotly_chart(style_figure(fig_abc_pie), use_container_width=True)

    st.subheader("Pareto por SKU")
    top_n_pareto = st.slider(
        "Top SKUs a mostrar en Pareto", min_value=10, max_value=100, value=30, step=5, key="datos_pareto"
    )
    pareto_df = filtered.head(top_n_pareto).copy()

    fig_pareto = go.Figure()
    fig_pareto.add_trace(
        go.Bar(
            x=pareto_df[col["sku"]],
            y=pareto_df[col["total"]],
            name="Compra por SKU",
            marker_color="#38bdf8",
            customdata=pareto_df[[col["descripcion"]]].to_numpy(),
            hovertemplate=(
                "<b>SKU:</b> %{x}<br>"
                "<b>Compra:</b> %{y:,.0f}<br>"
                "<b>Descripción:</b> %{customdata[0]}<extra></extra>"
            ),
        )
    )
    fig_pareto.add_trace(
        go.Scatter(
            x=pareto_df[col["sku"]],
            y=pareto_df["PCT_ACUM_COMPRA_CALC"] * 100,
            name="% acumulado",
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#f59e0b", width=3),
            marker=dict(color="#fbbf24", size=7),
        )
    )
    fig_pareto.update_layout(
        title="Pareto: compras por SKU y % acumulado",
        xaxis=dict(title="SKU", tickangle=-45),
        yaxis=dict(title="Compra"),
        yaxis2=dict(title="% acumulado", overlaying="y", side="right", range=[0, 100]),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="closest",
    )
    st.plotly_chart(style_figure(fig_pareto), use_container_width=True)

    st.subheader("Top 10 SKUs más costosos")
    top10 = filtered.head(10).copy()

    fig_top10 = px.bar(
        top10.sort_values(col["total"], ascending=True),
        x=col["total"],
        y=col["sku"],
        orientation="h",
        text=col["total"],
        title="Top 10 por compra",
        custom_data=[col["descripcion"]],
    )
    fig_top10.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="#f8fbff", size=12),
        cliponaxis=False,
        hovertemplate=(
            "<b>SKU:</b> %{y}<br>"
            "<b>Compra:</b> %{x:,.0f}<br>"
            "<b>Descripción:</b> %{customdata[0]}<extra></extra>"
        ),
    )
    st.plotly_chart(style_figure(fig_top10), use_container_width=True)

    st.subheader("Compras por grupo de material")
    group_summary = (
        filtered.groupby(col["grupo"], as_index=False)[col["total"]]
        .sum()
        .sort_values(col["total"], ascending=False)
    )
    fig_group = px.bar(
        group_summary,
        x=col["grupo"],
        y=col["total"],
        title="Compras por GRUPO DE MATERIAL",
        text=col["total"],
    )
    fig_group.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="#f8fbff", size=11),
        cliponaxis=False,
    )
    fig_group.update_layout(xaxis_tickangle=-35)
    st.plotly_chart(style_figure(fig_group), use_container_width=True)


def render_cuadro_dashboard():
    try:
        cuadro_df, col = load_cuadro_data()
    except Exception as exc:
        st.error(f"Error cargando datos CUADRO: {exc}")
        return

    st.subheader("KPIs globales")
    total_ventas = cuadro_df[col["ventas"]].sum()
    total_inv_real = cuadro_df[col["inv_real"]].sum()
    total_inv_std = cuadro_df[col["inv_std"]].sum()
    total_diff = cuadro_df[col["diff"]].sum()
    total_diff_pct = (total_diff / total_inv_std) if total_inv_std else 0

    g1, g2, g3, g4, g5 = st.columns(5)
    g1.metric("Ventas totales", fmt_currency(total_ventas))
    g2.metric("Inventario real total", fmt_currency(total_inv_real))
    g3.metric("Inventario estándar total", fmt_currency(total_inv_std))
    g4.metric("Diferencia total", fmt_currency(total_diff))
    g5.metric("Diferencia porcentual total", f"{total_diff_pct:.2%}")

    _render_cuadro_resumen_cards(cuadro_df, col)

    st.subheader("Gráficos CUADRO")
    c1, c2 = st.columns(2)
    with c1:
        inv_compare = cuadro_df[[col["clase"], col["inv_std"], col["inv_real"]]].melt(
            id_vars=col["clase"],
            value_vars=[col["inv_std"], col["inv_real"]],
            var_name="Tipo",
            value_name="Valor",
        )
        fig_inv = px.bar(
            inv_compare,
            x=col["clase"],
            y="Valor",
            color="Tipo",
            barmode="group",
            title="Inventario estándar vs real por clase",
        )
        st.plotly_chart(style_figure(fig_inv), use_container_width=True)

    with c2:
        fig_diff_pct = px.bar(
            cuadro_df,
            x=col["clase"],
            y=col["diff_pct"],
            text=col["diff_pct"],
            title="Diferencia porcentual por clase",
        )
        fig_diff_pct.update_traces(
            texttemplate="%{text:.2%}",
            textposition="outside",
            textfont=dict(color="#f8fbff", size=12),
            cliponaxis=False,
        )
        st.plotly_chart(style_figure(fig_diff_pct), use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig_ventas_dona = px.pie(
            cuadro_df,
            names=col["clase"],
            values=col["ventas"],
            hole=0.52,
            title="Participación de ventas por clase",
        )
        fig_ventas_dona.update_traces(
            textfont=dict(color="#f8fbff", size=12),
            marker=dict(line=dict(color="#0f172a", width=2)),
        )
        st.plotly_chart(style_figure(fig_ventas_dona), use_container_width=True)

    with c4:
        fig_rot = px.line(
            cuadro_df,
            x=col["clase"],
            y=col["rotacion"],
            markers=True,
            title="Rotación por clase",
        )
        fig_rot.update_traces(line=dict(color="#22d3ee", width=3), marker=dict(size=10, color="#67e8f9"))
        st.plotly_chart(style_figure(fig_rot), use_container_width=True)

    fig_cov = px.bar(
        cuadro_df,
        x=col["clase"],
        y="COBERTURA_DIAS",
        text="COBERTURA_DIAS",
        title="Cobertura por clase (días)",
    )
    fig_cov.update_traces(
        texttemplate="%{text:,.0f}",
        textposition="outside",
        textfont=dict(color="#f8fbff", size=12),
        cliponaxis=False,
    )
    st.plotly_chart(style_figure(fig_cov), use_container_width=True)

    _render_status_cards(cuadro_df, col)
