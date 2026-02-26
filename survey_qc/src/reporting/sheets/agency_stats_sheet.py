"""Agency statistics sheet."""

from src.models.entities import QCResult

from .base_sheet import BaseSheetWriter
from ._stats_mixin import StatsMixin


class AgencyStatsSheetWriter(StatsMixin, BaseSheetWriter):

    def __init__(self, workbook, results: list[QCResult]):
        super().__init__(workbook)
        self._results = results

    def write(self):
        ws = self._create_sheet("🏢 آمار نمایندگی")
        stats = self._compute_group_stats(self._results, group_field="agency")
        self._write_stats_table(ws, stats)
        return ws
