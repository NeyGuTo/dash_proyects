import unicodedata
from pathlib import Path

import pandas as pd
import streamlit as st


DATA_FILE = Path(__file__).resolve().parent / "data" / "taller_abc.xlsx"
SHEET_NAME = "DATOS"
CUADRO_SHEET_NAME = "CUADRO"


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return " ".join(text.upper().strip().split())


def resolve_column(columns: list[str], *aliases: str) -> str:
    normalized_map = {normalize_text(col): col for col in columns}
    for alias in aliases:
        key = normalize_text(alias)
        if key in normalized_map:
            return normalized_map[key]
    raise KeyError(f"No se encontro ninguna columna para aliases={aliases}")


def to_numeric(series: pd.Series) -> pd.Series:
    as_text = (
        series.astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(" ", "", regex=False)
        .str.replace(",", "", regex=False)
    )
    return pd.to_numeric(as_text, errors="coerce").fillna(0)


@st.cache_data
def load_data(path: Path = DATA_FILE, sheet_name: str = SHEET_NAME):
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {path}")

    df = pd.read_excel(path, sheet_name=sheet_name, header=2)
    df.columns = [str(c).strip() for c in df.columns]
    df = df.dropna(how="all").copy()

    col_sku = resolve_column(df.columns.tolist(), "CODIGO", "SKU")
    col_descripcion = resolve_column(df.columns.tolist(), "DESCRIPCION", "PRODUCTO", "ITEM")
    col_total = resolve_column(df.columns.tolist(), "TOTAL COMPRA 2024", "TOTAL COMPRA")
    col_abc = resolve_column(df.columns.tolist(), "CLASE ABC", "ABC")
    col_proveedor = resolve_column(df.columns.tolist(), "PROVEEDOR")
    col_grupo = resolve_column(df.columns.tolist(), "GRUPO DE MATERIAL")
    col_lead = resolve_column(df.columns.tolist(), "TIEMPO DE ENTREGA", "LEAD TIME", "TIEMPO ENTREGA")
    col_estrategia = resolve_column(
        df.columns.tolist(),
        "ESTRATEGIA DEL FABRICANTE / PROVEEDOR",
        "ESTRATEGIA FABRICANTE / PROVEEDOR",
        "ESTRATEGIA",
    )

    df[col_total] = to_numeric(df[col_total])
    df[col_lead] = to_numeric(df[col_lead])
    df[col_sku] = df[col_sku].astype(str).str.strip()
    df[col_abc] = df[col_abc].astype(str).str.strip().str.upper()
    df[col_proveedor] = df[col_proveedor].astype(str).str.strip()
    df[col_grupo] = df[col_grupo].astype(str).str.strip()
    df[col_estrategia] = df[col_estrategia].astype(str).str.strip()
    df[col_descripcion] = df[col_descripcion].astype(str).str.strip()

    df = df[df[col_sku].ne("") & df[col_sku].ne("nan")].copy()
    df = df.sort_values(by=col_total, ascending=False).reset_index(drop=True)

    total_compra = df[col_total].sum()
    df["ACUM_COMPRAS_CALC"] = df[col_total].cumsum()
    df["PCT_ACUM_COMPRA_CALC"] = (df["ACUM_COMPRAS_CALC"] / total_compra) if total_compra > 0 else 0

    column_map = {
        "sku": col_sku,
        "total": col_total,
        "descripcion": col_descripcion,
        "abc": col_abc,
        "proveedor": col_proveedor,
        "grupo": col_grupo,
        "lead": col_lead,
        "estrategia": col_estrategia,
    }
    return df, column_map


@st.cache_data
def load_cuadro_data(path: Path = DATA_FILE, sheet_name: str = CUADRO_SHEET_NAME):
    if not path.exists():
        raise FileNotFoundError(f"No se encontro el archivo: {path}")

    df_raw = pd.read_excel(path, sheet_name=sheet_name, header=2)
    df_raw.columns = [str(c).strip() for c in df_raw.columns]
    df_raw = df_raw.dropna(how="all").copy()
    df_raw = df_raw.loc[:, ~df_raw.columns.str.contains("^Unnamed", na=False)].copy()

    col_clase = resolve_column(df_raw.columns.tolist(), "CLASE")
    col_ventas = resolve_column(df_raw.columns.tolist(), "VENTAS X CLASE", "VENTAS")
    col_rotacion = resolve_column(df_raw.columns.tolist(), "ROTACION")
    col_inv_std = resolve_column(df_raw.columns.tolist(), "INVENT. PROM. ESTANDAR", "INVENTARIO ESTANDAR")
    col_inv_real = resolve_column(df_raw.columns.tolist(), "INVENT. PROM. REAL", "INVENTARIO REAL")
    col_diff = resolve_column(df_raw.columns.tolist(), "DIFERENCIA")
    col_diff_pct = resolve_column(df_raw.columns.tolist(), "DIFERENCIA PORCENTUAL", "DIFERENCIA %")
    col_analysis = resolve_column(df_raw.columns.tolist(), "ANALISIS DEL INDICADOR")

    num_candidates = [col_ventas, col_rotacion, col_inv_std, col_inv_real, col_diff, col_diff_pct]
    for col_name in num_candidates:
        df_raw[col_name] = to_numeric(df_raw[col_name])

    df_raw[col_clase] = df_raw[col_clase].astype(str).str.strip().str.upper()
    class_rows = df_raw[df_raw[col_clase].isin(["A", "B", "C"])].copy()

    class_summary = class_rows[class_rows[col_ventas] > 0].copy()
    class_summary["STATUS_INVENTARIO"] = class_summary[col_diff].apply(
        lambda x: "SOBRESTOCK" if x > 0 else ("DEFICIT" if x < 0 else "BALANCEADO")
    )
    class_summary["RECOMENDACION"] = class_summary[col_analysis].astype(str).str.strip()

    # Cobertura derivada: dias de cobertura aproximados = 360 / rotacion.
    class_summary["COBERTURA_DIAS"] = class_summary[col_rotacion].apply(
        lambda r: (360 / r) if r and r > 0 else 0
    )

    class_summary = class_summary.sort_values(by=col_clase).reset_index(drop=True)

    column_map = {
        "clase": col_clase,
        "ventas": col_ventas,
        "rotacion": col_rotacion,
        "inv_std": col_inv_std,
        "inv_real": col_inv_real,
        "diff": col_diff,
        "diff_pct": col_diff_pct,
        "analysis": col_analysis,
    }

    return class_summary, column_map


def fmt_currency(value: float) -> str:
    return f"${value:,.0f}"
