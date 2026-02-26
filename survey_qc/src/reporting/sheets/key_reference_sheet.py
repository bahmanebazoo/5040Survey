"""Key reference sheet."""

from src.parsers.key_sheet_parser import KeySheetParser

from .base_sheet import BaseSheetWriter


class KeyReferenceSheetWriter(BaseSheetWriter):

    def __init__(self, workbook, key_parser: KeySheetParser):
        super().__init__(workbook)
        self._key_parser = key_parser

    def write(self):
        ws = self._create_sheet("🔑 مرجع کلیدها")

        headers = ["گزینه", "نوع (مثبت/منفی)", "اولویت"]
        self._write_header_row(ws, headers)

        for i, entry in enumerate(self._key_parser.entries, start=2):
            ws.cell(row=i, column=1, value=entry.option)
            ws.cell(
                row=i, column=2,
                value="مثبت ✅" if entry.sentiment == "+" else "منفی 🔴",
            )
            ws.cell(row=i, column=3, value=entry.priority)

        # Contradiction pairs section
        row_start = len(self._key_parser.entries) + 4
        ws.cell(row=row_start, column=1, value="جفت‌های متناقض شناسایی‌شده").font = \
            self._styles.SECTION_FONT

        pair_headers = ["نکته مثبت", "نکته منفی متناقض"]
        for col_idx, header in enumerate(pair_headers, start=1):
            cell = ws.cell(row=row_start + 1, column=col_idx, value=header)
            cell.font = self._styles.HEADER_FONT
            cell.fill = self._styles.HEADER_FILL

        for i, (pos, neg) in enumerate(
            self._key_parser.contradiction_pairs, start=row_start + 2
        ):
            ws.cell(row=i, column=1, value=pos)
            ws.cell(row=i, column=2, value=neg)

        self._auto_fit_columns(ws, headers)
        return ws
