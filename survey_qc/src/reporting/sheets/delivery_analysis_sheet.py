"""Delivery time analysis sheet."""

import pandas as pd

from src.models.entities import QCResult
from src.parsers.column_resolver import ColumnResolver
from src.parsers.note_parser import NoteParser

from .base_sheet import BaseSheetWriter


class DeliveryAnalysisSheetWriter(BaseSheetWriter):

    def __init__(self, workbook, results: list[QCResult],
                 survey_df: pd.DataFrame, cols: ColumnResolver):
        super().__init__(workbook)
        self._results = results
        self._survey_df = survey_df
        self._cols = cols

    def write(self):
        ws = self._create_sheet("🚚 تحلیل زمان تحویل")

        headers = [
            "ردیف", "سریال فاکتور", "نام مشتری", "نمایندگی", "پیک",
            "تاریخ ورود", "تاریخ تحویل", "ساعت تحویل",
            "ادعای به‌موقع", "شکایت تأخیر", "وضعیت",
        ]
        self._write_header_row(ws, headers)

        entry_col = self._cols.get("entry_date")
        delivery_col = self._cols.get("delivery_date")
        pos_col = self._cols.get("positive_notes")
        neg_col = self._cols.get("negative_notes")

        for i, result in enumerate(self._results, start=2):
            row_data = (
                self._survey_df.iloc[result.row_index]
                if result.row_index < len(self._survey_df)
                else None
            )

            entry_val = str(row_data.get(entry_col, "")) if row_data is not None and entry_col else ""
            delivery_val = str(row_data.get(delivery_col, "")) if row_data is not None and delivery_col else ""

            pos_notes = NoteParser.parse(
                row_data.get(pos_col) if row_data is not None and pos_col else None
            )
            neg_notes = NoteParser.parse(
                row_data.get(neg_col) if row_data is not None and neg_col else None
            )

            has_ontime = "✅" if NoteParser.contains_keyword(pos_notes, "تحویل به موقع") else "—"
            has_delay = "🔴" if NoteParser.contains_any_keyword(neg_notes, ["تاخیر", "تأخیر"]) else "—"

            ws.cell(row=i, column=1, value=i - 1)
            ws.cell(row=i, column=2, value=result.serial)
            ws.cell(row=i, column=3, value=result.customer_name)
            ws.cell(row=i, column=4, value=result.agency)
            ws.cell(row=i, column=5, value=result.courier)
            ws.cell(row=i, column=6, value=entry_val)
            ws.cell(row=i, column=7, value=delivery_val)
            ws.cell(row=i, column=8, value=round(result.delivery_hours, 1) if result.delivery_hours else "N/A")
            ws.cell(row=i, column=9, value=has_ontime)
            ws.cell(row=i, column=10, value=has_delay)
            status_cell = ws.cell(row=i, column=11, value=result.status.label)
            self._apply_status_fill(status_cell, result.status)

        self._auto_fit_columns(ws, headers)
        return ws
