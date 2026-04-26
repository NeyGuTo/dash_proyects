import unicodedata

import pandas as pd

from laboratorio.config import FILES_BY_YEAR, MONTH_ALIASES, TABLE_COLUMNS, TARGET_EXAMS


EXPECTED_HEADER = [
    "HOSPITALIZ",
    "EMERGENC",
    "C EXTERNA",
    "PRIVADO",
    "CONVENIO",
    "INSOLVENCIA",
    "TOTAL",
]


def normalize_text(value):
    if pd.isna(value):
        return ""
    text = str(value).strip().upper()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(char for char in text if not unicodedata.combining(char))
    text = text.replace(".", " ")
    text = " ".join(text.split())
    return text


def normalize_sheet_name(sheet_name):
    normalized = normalize_text(sheet_name)
    return MONTH_ALIASES.get(normalized)


def _find_header_row(raw_df):
    for index, row in raw_df.iterrows():
        values = [normalize_text(item) for item in row.tolist()]
        if values[1:8] == EXPECTED_HEADER:
            return index
    return None


def _clean_month_sheet(raw_df, year, sheet_name, file_name):
    header_row = _find_header_row(raw_df)
    if header_row is None:
        raise ValueError("No se encontró la cabecera de columnas esperada.")

    table = raw_df.iloc[header_row + 1 :, :8].copy()
    table.columns = TABLE_COLUMNS
    table = table.dropna(how="all")
    table["EXAMEN"] = table["EXAMEN"].apply(lambda value: str(value).strip() if pd.notna(value) else "")
    table = table[table["EXAMEN"] != ""].copy()

    target_map = {normalize_text(name): name for name in TARGET_EXAMS}
    table["EXAMEN_NORMALIZADO"] = table["EXAMEN"].apply(normalize_text)
    table = table[table["EXAMEN_NORMALIZADO"].isin(target_map)].copy()
    table["EXAMEN"] = table["EXAMEN_NORMALIZADO"].map(target_map)

    if table.empty:
        return table

    for column in TABLE_COLUMNS[1:]:
        table[column] = pd.to_numeric(table[column], errors="coerce").fillna(0)

    month_info = normalize_sheet_name(sheet_name)
    if month_info is None:
        raise ValueError(f"La hoja '{sheet_name}' no corresponde a un mes válido.")

    month_name, month_number = month_info
    table["AÑO"] = year
    table["MES"] = month_name
    table["MES_NUM"] = month_number
    table["PERIODO"] = pd.to_datetime(
        {"year": table["AÑO"], "month": table["MES_NUM"], "day": 1}
    )
    table["FUENTE"] = file_name
    table["HOJA"] = sheet_name

    return table.drop(columns=["EXAMEN_NORMALIZADO"])


def read_year_file(year, file_path):
    issues = []
    frames = []

    if not file_path.exists():
        issues.append(f"No se encontró el archivo {file_path.name}.")
        return pd.DataFrame(), issues

    try:
        excel_file = pd.ExcelFile(file_path, engine="openpyxl")
    except Exception as exc:
        issues.append(f"No se pudo abrir {file_path.name}: {exc}")
        return pd.DataFrame(), issues

    month_sheets = [sheet for sheet in excel_file.sheet_names if normalize_sheet_name(sheet)]
    if year == 2026:
        month_sheets = [
            sheet for sheet in month_sheets if normalize_sheet_name(sheet)[1] in [1, 2]
        ]
    if not month_sheets:
        issues.append(f"{file_path.name} no contiene hojas mensuales reconocibles.")
        return pd.DataFrame(), issues

    for sheet_name in month_sheets:
        try:
            raw_df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=None,
                usecols="A:H",
                engine="openpyxl",
            )
            clean_df = _clean_month_sheet(raw_df, year, sheet_name, file_path.name)
            if clean_df.empty:
                issues.append(
                    f"La hoja {sheet_name} de {file_path.name} no contiene los exámenes objetivo."
                )
                continue
            frames.append(clean_df)
        except Exception as exc:
            issues.append(f"No se pudo procesar la hoja {sheet_name} de {file_path.name}: {exc}")

    if not frames:
        return pd.DataFrame(), issues

    year_df = pd.concat(frames, ignore_index=True)
    if year == 2026:
        year_df = year_df[year_df["MES_NUM"] <= 2].copy()
    year_df = year_df.sort_values(["AÑO", "MES_NUM", "EXAMEN"]).reset_index(drop=True)
    return year_df, issues


def load_lab_data():
    frames = []
    issues = []

    for year, file_path in FILES_BY_YEAR.items():
        year_df, year_issues = read_year_file(year, file_path)
        if not year_df.empty:
            frames.append(year_df)
        issues.extend(year_issues)

    if not frames:
        return pd.DataFrame(), issues

    data = pd.concat(frames, ignore_index=True)
    data["TOTAL"] = pd.to_numeric(data["TOTAL"], errors="coerce").fillna(0)
    return data, issues
