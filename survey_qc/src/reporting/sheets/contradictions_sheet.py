"""Contradictions list sheet."""

from src.models.entities import QCResult

from .base_sheet import BaseSheetWriter


class ContradictionsSheetWriter(BaseSheetWriter):

    def __init__(self, workbook, results: list[QCResult]):
        super().__init__(workbook)
        self._results = results

    def write(self):
        ws = self._create_sheet("🔴 لیست تناقضات")

        headers = [
            "ردیف", "سریال فاکتور", "نام مشتری", "نمایندگی",
            "نوع تناقض", "توضیحات", "جزئیات", "جریمه",
            "امتیاز اعتبار", "وضعیت",
        ]
        self._write_header_row(ws, headers)

        row_num = 2
        for result in self._results:
            for contradiction in result.contradictions:
                ws.cell(row=row_num, column=1, value=row_num - 1)
                ws.cell(row=row_num, column=2, value=result.serial)
                ws.cell(row=row_num, column=3, value=result.customer_name)
                ws.cell(row=row_num, column=4, value=result.agency)
                ws.cell(row=row_num, column=5, value=contradiction.contradiction_type.value)
                ws.cell(row=row_num, column=6, value=contradiction.description)
                ws.cell(row=row_num, column=7, value=contradiction.detail)
                ws.cell(row=row_num, column=8, value=contradiction.penalty)
                ws.cell(row=row_num, column=9, value=round(result.reliability_score, 1))
                status_cell = ws.cell(row=row_num, column=10, value=result.status.label)
                self._apply_status_fill(status_cell, result.status)
                row_num += 1

        if row_num == 2:
            ws.cell(row=2, column=1, value="هیچ تناقضی یافت نشد ✅").font = \
                self._styles.SUCCESS_FONT

        self._auto_fit_columns(ws, headers)
        return ws
