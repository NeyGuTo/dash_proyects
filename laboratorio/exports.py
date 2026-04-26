from io import BytesIO

import pandas as pd


def dataframe_to_excel_bytes(named_frames):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for sheet_name, frame in named_frames.items():
            export_frame = frame.copy()
            export_frame.to_excel(writer, sheet_name=sheet_name[:31], index=False)
    output.seek(0)
    return output.getvalue()
