import pandas as pd

from laboratorio.config import MONTH_ORDER, TARGET_EXAMS, USAGE_COLUMNS


def apply_filters(data, years=None, exams=None):
    filtered = data.copy()
    if years is not None:
        filtered = filtered[filtered["AÑO"].isin(years)]
    if exams is not None:
        filtered = filtered[filtered["EXAMEN"].isin(exams)]
    return filtered


def format_int(value):
    return f"{int(round(value)):,}".replace(",", ".")


def build_kpis(data):
    if data.empty:
        return {
            "total_consumo": 0,
            "promedio_mensual": 0,
            "meses_analizados": 0,
            "examen_top": "Sin datos",
        }

    monthly_totals = data.groupby(["AÑO", "MES_NUM"], as_index=False)["TOTAL"].sum()
    exam_totals = data.groupby("EXAMEN", as_index=False)["TOTAL"].sum().sort_values("TOTAL", ascending=False)

    return {
        "total_consumo": data["TOTAL"].sum(),
        "promedio_mensual": monthly_totals["TOTAL"].mean(),
        "meses_analizados": monthly_totals.shape[0],
        "examen_top": exam_totals.iloc[0]["EXAMEN"] if not exam_totals.empty else "Sin datos",
    }


def exam_monthly_stats(data):
    if data.empty:
        return {
            "meses_analizados": 0,
            "totales_por_examen": {exam: 0 for exam in TARGET_EXAMS},
            "promedios_por_examen": {exam: 0 for exam in TARGET_EXAMS},
        }

    meses_analizados = int(data[["AÑO", "MES_NUM"]].drop_duplicates().shape[0])
    totals = (
        data.groupby("EXAMEN", as_index=False)["TOTAL"]
        .sum()
        .set_index("EXAMEN")["TOTAL"]
        .to_dict()
    )
    totals = {exam: float(totals.get(exam, 0)) for exam in TARGET_EXAMS}
    promedios = {
        exam: (totals[exam] / meses_analizados) if meses_analizados else 0
        for exam in TARGET_EXAMS
    }

    return {
        "meses_analizados": meses_analizados,
        "totales_por_examen": totals,
        "promedios_por_examen": promedios,
    }


def exam_adjusted_monthly_stats(data):
    if data.empty:
        return {
            "meses_ajustados_por_examen": {exam: 0 for exam in TARGET_EXAMS},
            "promedios_ajustados_por_examen": {exam: 0 for exam in TARGET_EXAMS},
        }

    monthly = (
        data.groupby(["EXAMEN", "AÑO", "MES_NUM"], as_index=False)["TOTAL"]
        .sum()
        .sort_values(["EXAMEN", "AÑO", "MES_NUM"])
    )

    totals = (
        data.groupby("EXAMEN", as_index=False)["TOTAL"]
        .sum()
        .set_index("EXAMEN")["TOTAL"]
        .to_dict()
    )

    adjusted_months = {}
    adjusted_averages = {}

    for exam in TARGET_EXAMS:
        exam_monthly = monthly[monthly["EXAMEN"] == exam].copy()
        exam_total = float(totals.get(exam, 0))

        if exam_monthly.empty or exam_total <= 0:
            adjusted_months[exam] = 0
            adjusted_averages[exam] = 0
            continue

        positive_months = exam_monthly[exam_monthly["TOTAL"] > 0].copy()
        if positive_months.empty:
            adjusted_months[exam] = 0
            adjusted_averages[exam] = 0
            continue

        first_period = pd.Timestamp(
            year=int(positive_months.iloc[0]["AÑO"]),
            month=int(positive_months.iloc[0]["MES_NUM"]),
            day=1,
        )
        last_period = pd.Timestamp(
            year=int(exam_monthly.iloc[-1]["AÑO"]),
            month=int(exam_monthly.iloc[-1]["MES_NUM"]),
            day=1,
        )

        adjusted_count = (
            (last_period.year - first_period.year) * 12
            + (last_period.month - first_period.month)
            + 1
        )

        adjusted_months[exam] = adjusted_count
        adjusted_averages[exam] = exam_total / adjusted_count if adjusted_count else 0

    return {
        "meses_ajustados_por_examen": adjusted_months,
        "promedios_ajustados_por_examen": adjusted_averages,
    }


def monthly_consumption(data):
    if data.empty:
        return pd.DataFrame(columns=["AÑO", "MES", "MES_NUM", "PERIODO", "EXAMEN", "TOTAL"])

    monthly = (
        data.groupby(["AÑO", "MES", "MES_NUM", "PERIODO", "EXAMEN"], as_index=False)["TOTAL"]
        .sum()
        .sort_values(["AÑO", "MES_NUM", "EXAMEN"])
    )
    return monthly


def area_usage(data):
    if data.empty:
        return pd.DataFrame(columns=["EXAMEN", "AREA", "CANTIDAD"])

    area_df = (
        data.groupby("EXAMEN", as_index=False)[USAGE_COLUMNS]
        .sum()
        .melt(id_vars="EXAMEN", value_vars=USAGE_COLUMNS, var_name="AREA", value_name="CANTIDAD")
    )
    return area_df


def monthly_summary_table(data):
    if data.empty:
        return pd.DataFrame()

    summary = (
        data.pivot_table(
            index=["AÑO", "MES_NUM", "MES"],
            columns="EXAMEN",
            values="TOTAL",
            aggfunc="sum",
            fill_value=0,
        )
        .reset_index()
        .sort_values(["AÑO", "MES_NUM"])
    )
    return summary


def exam_summary_table(data):
    if data.empty:
        return pd.DataFrame()

    summary = (
        data.groupby("EXAMEN", as_index=False)[USAGE_COLUMNS + ["TOTAL"]]
        .sum()
        .sort_values("TOTAL", ascending=False)
    )
    return summary


def comparison_table(data):
    if data.empty:
        return pd.DataFrame(), pd.DataFrame()

    comparison_base = data[data["MES_NUM"] <= 2].copy()
    comparison = (
        comparison_base.groupby(["EXAMEN", "AÑO"], as_index=False)["TOTAL"]
        .sum()
        .pivot(index="EXAMEN", columns="AÑO", values="TOTAL")
        .reindex(TARGET_EXAMS, fill_value=0)
        .fillna(0)
        .reset_index()
    )

    for year in [2025, 2026]:
        if year not in comparison.columns:
            comparison[year] = 0

    comparison["VARIACION_ABS"] = comparison[2026] - comparison[2025]
    comparison["VARIACION_PCT"] = comparison.apply(
        lambda row: (row["VARIACION_ABS"] / row[2025] * 100) if row[2025] else 0,
        axis=1,
    )

    monthly_compare = (
        comparison_base.groupby(["MES_NUM", "MES", "AÑO"], as_index=False)["TOTAL"]
        .sum()
        .pivot(index=["MES_NUM", "MES"], columns="AÑO", values="TOTAL")
        .fillna(0)
        .reset_index()
        .sort_values("MES_NUM")
    )

    for year in [2025, 2026]:
        if year not in monthly_compare.columns:
            monthly_compare[year] = 0

    monthly_compare["VARIACION_ABS"] = monthly_compare[2026] - monthly_compare[2025]
    return comparison, monthly_compare


def sismed_window(data):
    if data.empty:
        return pd.DataFrame()

    mask = (
        ((data["AÑO"] == 2025) & (data["MES_NUM"] >= 9))
        | ((data["AÑO"] == 2026) & (data["MES_NUM"] <= 2))
    )
    window = data.loc[mask].copy()
    return window.sort_values(["AÑO", "MES_NUM", "EXAMEN"])


def six_month_average(data):
    window = sismed_window(data)
    if window.empty:
        return pd.DataFrame(columns=["EXAMEN", "PROMEDIO_MENSUAL_6M"])

    month_index = pd.MultiIndex.from_product(
        [TARGET_EXAMS, [2025, 2026], range(1, 13)],
        names=["EXAMEN", "AÑO", "MES_NUM"],
    )
    valid_mask = (
        ((month_index.get_level_values("AÑO") == 2025) & (month_index.get_level_values("MES_NUM").isin([9, 10, 11, 12])))
        | ((month_index.get_level_values("AÑO") == 2026) & (month_index.get_level_values("MES_NUM").isin([1, 2])))
    )
    month_index = month_index[valid_mask]

    aggregated = (
        window.groupby(["EXAMEN", "AÑO", "MES_NUM"], as_index=False)["TOTAL"]
        .sum()
        .set_index(["EXAMEN", "AÑO", "MES_NUM"])
        .reindex(month_index, fill_value=0)
        .reset_index()
    )

    average_df = (
        aggregated.groupby("EXAMEN", as_index=False)["TOTAL"]
        .mean()
        .rename(columns={"TOTAL": "PROMEDIO_MENSUAL_6M"})
    )
    return average_df


def period_label(year, month_num):
    month_name = next(name for name, number in MONTH_ORDER.items() if number == month_num)
    return f"{month_name} {year}"
