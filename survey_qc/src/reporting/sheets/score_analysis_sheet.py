"""Score analysis sheet."""

import pandas as pd

from src.models.entities import QCResult
from src.parsers.column_resolver import ColumnResolver
from src.parsers.note_parser import NoteParser

from .base_sheet import BaseSheetWriter


class ScoreAnalysisSheetWriter(BaseSheetWriter):

    def __init__(self, workbook, results: list[QCResult],
                 survey_df: pd.DataFrame, cols: ColumnResolver):
        super().__init__(workbook)
        self._results = results
        self._survey_df = survey_df
        self._cols = cols

    def write(self):
        ws = self._create_sheet("⭐ تحلیل امتیاز")

        headers = [
            "ردیف", "سریال فاکتور", "نام مشتری", "نمایندگی", "پیک",
            "امتیاز مشتری", "تعداد مثبت", "تعداد منفی",
            "امتیاز اعتبار", "وضعیت",
        ]
        self._write_header_row(ws, headers)

        pos_col = self._cols.get("positive_notes")
        neg_col = self._cols.get("negative_notes")

        for i, result in enumerate(self._results, start=2):
            row_data = (
                self._survey_df.iloc[result.row_index]
                if result.row_index < len(self._survey_df)
                else None
            )

            pos_count = len(NoteParser.parse(
                row_data.get(pos_col) if row_data is not None and pos_col else None
            ))
            neg_count = len(NoteParser.parse(
                row_data.get(neg_col) if row_data is not None and neg_col else None
            ))

            ws.cell(row=i, column=1, value=i - 1)
            ws.cell(row=i, column=2, value=result.serial)
            ws.cell(row=i, column=3, value=result.customer_name)
            ws.cell(row=i, column=4, value=result.agency)
            ws.cell(row=i, column=5, value=result.courier)
            ws.cell(row=i, column=6, value=result.score)
            ws.cell(row=i, column=7, value=pos_count)
            ws.cell(row=i, column=8, value=neg_count)
            ws.cell(row=i, column=9, value=round(result.reliability_score, 1))
            status_cell = ws.cell(row=i, column=10, value=result.status.label)
            self._apply_status_fill(status_cell, result.status)

        self._auto_fit_columns(ws, headers)
        return ws
