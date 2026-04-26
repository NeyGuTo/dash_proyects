import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import re

st.set_page_config(page_title="Dashboard Farmacia", layout="wide")
st.title("📊 Dashboard de Control de Farmacia")

def to_number(s):
    if pd.isna(s):
        return pd.NA
    if isinstance(s, (int, float)):
        return s
    s = str(s)
    m = re.search(r"-?\d+(?:[.,]\d+)?", s)
    if m:
        val = m.group(0).replace(",", ".")
        try:
            return float(val)
        except:
            return pd.NA
    return pd.NA

uploaded_file = st.file_uploader("Carga tu archivo Excel (columnas: medcod, mednom, contado, precio)", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()

    rename_map = {
        "medcod": "MEDCOD",
        "mednom": "MEDNOM",
        "contado": "CONTADO",
        "precio": "PRECIO"
    }
    df = df.rename(columns={c: rename_map.get(c, c) for c in df.columns})

    # Validación
    cols_req = ["MEDCOD", "MEDNOM", "CONTADO", "PRECIO"]
    if not all(col in df.columns for col in cols_req):
        st.error("❌ El archivo debe tener: medcod, mednom, contado, precio")
    else:
        df["MEDCOD"] = df["MEDCOD"].astype(str).str.zfill(5)
        df["CONTADO"] = df["CONTADO"].apply(to_number).fillna(0)
        df["PRECIO"] = df["PRECIO"].apply(to_number).fillna(0)

        # Calcular monto en soles solo para CONTADO
        df["MONTO_CONTADO"] = df["CONTADO"] * df["PRECIO"]

        # KPIs generales
        st.subheader("📌 Indicadores Generales")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total CONTADO", f"{int(df['CONTADO'].sum()):,}")
        c2.metric("Soles CONTADO", f"S/ {df['MONTO_CONTADO'].sum():,.2f}")
        c3.metric("Productos únicos", f"{df['MEDCOD'].nunique():,}")

        # --- Top 30 por CONTADO ---
        st.subheader("🔝 Top 30 productos más consumidos (CONTADO)")
        top_contado = df.sort_values(by="CONTADO", ascending=False).head(30)
        st.dataframe(top_contado[["MEDCOD", "MEDNOM", "CONTADO", "PRECIO", "MONTO_CONTADO"]].reset_index(drop=True), use_container_width=True)

        fig1, ax1 = plt.subplots(figsize=(10, 8))
        ax1.barh(top_contado["MEDNOM"], top_contado["CONTADO"], color="mediumseagreen")
        ax1.invert_yaxis()
        ax1.set_title("Top 30 productos por CONTADO")
        ax1.set_xlabel("Cantidad (CONTADO)")
        st.pyplot(fig1)

        # --- Top 30 por MONTO TOTAL (solo CONTADO) ---
        st.subheader("🔝 Top 30 productos con mayor monto total (CONTADO)")
        top_monto_total = df.sort_values(by="MONTO_CONTADO", ascending=False).head(30)
        st.dataframe(top_monto_total[["MEDCOD", "MEDNOM", "CONTADO", "PRECIO", "MONTO_CONTADO"]].reset_index(drop=True), use_container_width=True)

        fig2, ax2 = plt.subplots(figsize=(10, 8))
        ax2.barh(top_monto_total["MEDNOM"], top_monto_total["MONTO_CONTADO"], color="coral")
        ax2.invert_yaxis()
        ax2.set_title("Top 30 productos por MONTO CONTADO")
        ax2.set_xlabel("Monto total (S/)")
        st.pyplot(fig2)

        # Descarga de datos limpios
        st.subheader("💾 Descargar tabla procesada")
        csv = df.to_csv(index=False, sep=";")
        st.download_button("Descargar CSV", data=csv, file_name="farmacia_analisis_contado.csv", mime="text/csv")

else:
    st.info("📂 Por favor, sube un archivo Excel para comenzar.")
