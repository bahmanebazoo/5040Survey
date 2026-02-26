"""
Excel Report Generator — Orchestrates all sheet writers.
"""

import pandas as pd
from openpyxl import Workbook

from src.models.entities import QCResult
from src.parsers.column_resolver import ColumnResolver
from src.parsers.key_sheet_parser import KeySheetParser

from .sheets import (
    SummarySheetWriter,
    ContradictionsSheetWriter,
    ScoreAnalysisSheetWriter,
    DeliveryAnalysisSheetWriter,
    AgencyStatsSheetWriter,
    CourierStatsSheetWriter,
    RawQCSheetWriter,
    KeyReferenceSheetWriter,
    ChartsSheetWriter,
)


class ExcelReportGenerator:
    """
    Generates the complete Excel QC report by delegating
    to individual sheet writers (Single Responsibility).
    """

    def __init__(
        self,
        results: list[QCResult],
        survey_df: pd.DataFrame,
        key_parser: KeySheetParser,
        col_resolver: ColumnResolver,
    ):
        self._results = results
        self._survey_df = survey_df
        self._key_parser = key_parser
        self._cols = col_resolver

    def generate(self, output_path: str):
        """Generate the complete report to the given path."""
        wb = Workbook()
        # Remove the default sheet
        wb.remove(wb.active)

        # Create all sheets via their dedicated writers
        writers = [
            SummarySheetWriter(wb, self._results),
            ContradictionsSheetWriter(wb, self._results),
            ScoreAnalysisSheetWriter(wb, self._results, self._survey_df, self._cols),
            DeliveryAnalysisSheetWriter(wb, self._results, self._survey_df, self._cols),
            AgencyStatsSheetWriter(wb, self._results),
            CourierStatsSheetWriter(wb, self._results),
            RawQCSheetWriter(wb, self._results),
            KeyReferenceSheetWriter(wb, self._key_parser),
            ChartsSheetWriter(wb, self._results),
        ]

        for writer in writers:
            writer.write()

        wb.save(output_path)
        print(f"\n✅ Report saved to: {output_path}")
