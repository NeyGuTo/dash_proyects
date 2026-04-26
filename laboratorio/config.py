from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

FILES_BY_YEAR = {
    2025: DATA_DIR / "data_lab_2025.xlsx",
    2026: DATA_DIR / "data_lab_2026.xlsx",
}

TARGET_EXAMS = [
    "HEMOGLOBINA GLICOSILADA",
    "CREATININA",
    "MICROALBUMINURIA",
]

USAGE_COLUMNS = [
    "Hospitaliz",
    "Emergenc",
    "C_Externa",
    "Privado",
    "Convenio",
    "Insolvencia",
]

TABLE_COLUMNS = [
    "EXAMEN",
    "Hospitaliz",
    "Emergenc",
    "C_Externa",
    "Privado",
    "Convenio",
    "Insolvencia",
    "TOTAL",
]

MONTH_ORDER = {
    "ENERO": 1,
    "FEBRERO": 2,
    "MARZO": 3,
    "ABRIL": 4,
    "MAYO": 5,
    "JUNIO": 6,
    "JULIO": 7,
    "AGOSTO": 8,
    "SETIEMBRE": 9,
    "OCTUBRE": 10,
    "NOVIEMBRE": 11,
    "DICIEMBRE": 12,
}

MONTH_ALIASES = {
    "ENERO": ("ENERO", 1),
    "FEBRERO": ("FEBRERO", 2),
    "MARZO": ("MARZO", 3),
    "ABRIL": ("ABRIL", 4),
    "MAYO": ("MAYO", 5),
    "JUN": ("JUNIO", 6),
    "JUNIO": ("JUNIO", 6),
    "JUL": ("JULIO", 7),
    "JULIO": ("JULIO", 7),
    "AGO": ("AGOSTO", 8),
    "AGOSTO": ("AGOSTO", 8),
    "SET": ("SETIEMBRE", 9),
    "SEPTIEMBRE": ("SETIEMBRE", 9),
    "SETIEMBRE": ("SETIEMBRE", 9),
    "OCT": ("OCTUBRE", 10),
    "OCTUBRE": ("OCTUBRE", 10),
    "NOV": ("NOVIEMBRE", 11),
    "NOVIEMBRE": ("NOVIEMBRE", 11),
    "DIC": ("DICIEMBRE", 12),
    "DICIEMBRE": ("DICIEMBRE", 12),
}
