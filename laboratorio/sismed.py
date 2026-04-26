import pandas as pd


def sismed_static_data():
    return pd.DataFrame(
        [
            {
                "EXAMEN": "HEMOGLOBINA GLICOSILADA",
                "EXAMEN_BASE": "HEMOGLOBINA GLICOSILADA",
                "INGRESOS_TOTALES": 3000,
                "SALIDAS_TOTALES": 1000,
                "STOCK_FINAL": 2000,
            },
            {
                "EXAMEN": "CREATININA (CINETICA + ENZIMATICA)",
                "EXAMEN_BASE": "CREATININA",
                "INGRESOS_TOTALES": 12578,
                "SALIDAS_TOTALES": 8440,
                "STOCK_FINAL": 4138,
            },
            {
                "EXAMEN": "MICROALBUMINURIA",
                "EXAMEN_BASE": "MICROALBUMINURIA",
                "INGRESOS_TOTALES": 380,
                "SALIDAS_TOTALES": 0,
                "STOCK_FINAL": 380,
            },
        ]
    )
