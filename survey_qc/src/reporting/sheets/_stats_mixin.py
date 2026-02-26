"""Shared statistics computation for agency/courier sheets."""

import pandas as pd

from src.models.entities import QCResult
from src.models.enums import QCStatus


class StatsMixin:
    """Mixin providing group statistics computation and table writing."""

    @staticmethod
    def _compute_group_stats(
        results: list[QCResult], group_field: str
    ) -> pd.DataFrame:
        records = []
        for r in results:
            records.append({
                "group": getattr(r, group_field, "N/A"),
                "score": r.score,
                "reliability": r.reliability_score,
                "contradictions": len(r.contradictions),
                "confirmed": 1 if r.status == QCStatus.CONFIRM else 0,
                "review": 1 if r.status == QCStatus.REVIEW else 0,
                "rejected": 1 if r.status == QCStatus.REJECT else 0,
            })

        df = pd.DataFrame(records)
        if df.empty:
            return pd.DataFrame()

        stats = df.groupby("group").agg(
            تعداد=("score", "count"),
            میانگین_امتیاز=("score", "mean"),
            میانگین_اعتبار=("reliability", "mean"),
            مجموع_تناقضات=("contradictions", "sum"),
            تأیید=("confirmed", "sum"),
            بررسی=("review", "sum"),
            رد=("rejected", "sum"),
        ).round(2).reset_index()
        stats.rename(columns={"group": "نام"}, inplace=True)
        return stats

    def _write_stats_table(self, ws, stats_df: pd.DataFrame):
        if stats_df.empty:
            ws.cell(row=1, column=1, value="داده‌ای یافت نشد")
            return

        headers = list(stats_df.columns)
        self._write_header_row(ws, headers)

        for r_idx, (_, row) in enumerate(stats_df.iterrows(), start=2):
            for c_idx, col in enumerate(headers, start=1):
                ws.cell(row=r_idx, column=c_idx, value=row[col])

        self._auto_fit_columns(ws, headers)
