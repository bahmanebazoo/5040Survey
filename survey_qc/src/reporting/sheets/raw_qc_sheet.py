"""Raw QC data sheet."""

from src.models.entities import QCResult

from .base_sheet import BaseSheetWriter


class RawQCSheetWriter(BaseSheetWriter):

    def __init__(self, workbook, results: list[QCResult]):
        super().__init__(workbook)
        self._results = results

    def write(self):
        ws = self._create_sheet("📄 داده خام QC")

        headers = [
            "ردیف", "سریال", "مشتری", "نمایندگی", "پیک",
            "امتیاز", "ساعت تحویل", "امتیاز اعتبار",
            "تعداد تناقض", "وضعیت", "توضیحات تناقضات",
        ]
        self._write_header_row(ws, headers)

        for i, result in enumerate(self._results, start=2):
            contra_desc = (
                " | ".join(c.description for c in result.contradictions)
                if result.contradictions
                else "—"
            )
            ws.cell(row=i, column=1, value=i - 1)
            ws.cell(row=i, column=2, value=result.serial)
            ws.cell(row=i, column=3, value=result.customer_name)
            ws.cell(row=i, column=4, value=result.agency)
            ws.cell(row=i, column=5, value=result.courier)
            ws.cell(row=i, column=6, value=result.score)
            ws.cell(row=i, column=7, value=(
                round(result.delivery_hours, 1)
                if result.delivery_hours else "N/A"
            ))
            ws.cell(row=i, column=8, value=round(result.reliability_score, 1))
            ws.cell(row=i, column=9, value=result.contradiction_count)
            status_cell = ws.cell(row=i, column=10, value=result.status.label)
            self._apply_status_fill(status_cell, result.status)
            ws.cell(row=i, column=11, value=contra_desc)

        self._auto_fit_columns(ws, headers)
        return ws
