"""
QC Engine — Orchestrates contradiction detection across all detectors.
Follows Dependency Inversion: depends on abstractions, not concretes.
"""

from typing import Optional

import pandas as pd

from src.detectors.base import ContradictionDetector
from src.models.entities import QCResult
from src.parsers.column_resolver import ColumnResolver
from src.parsers.date_parser import JalaliDateParser
from src.parsers.key_sheet_parser import KeySheetParser


class QCEngine:
    """
    Core engine that runs all registered contradiction detectors
    against each survey row and produces QCResult objects.

    ⚠ freshness_detector جدا از detectors است:
       - detectors: لیست ContradictionDetector با متد detect()
       - freshness_detector: SurveyFreshnessDetector با متد evaluate()
    """

    def __init__(
        self,
        detectors: list[ContradictionDetector],
        key_parser: KeySheetParser,
        col_resolver: ColumnResolver,
        freshness_detector=None,
        verbose: bool = False,
    ):
        self._detectors = detectors
        self._key_parser = key_parser
        self._cols = col_resolver
        self._freshness = freshness_detector
        self._verbose = verbose

    def analyze(self, df: pd.DataFrame) -> list[QCResult]:
        """
        Analyze all rows in the DataFrame.

        Args:
            df: Survey DataFrame.

        Returns:
            List of QCResult objects, one per row.
        """
        results = []
        total = len(df)

        for idx, row in df.iterrows():
            if self._verbose and (idx + 1) % 100 == 0:
                print(f"   Processing row {idx + 1}/{total}...")
            result = self._analyze_row(row)
            results.append(result)

        return results

    def _analyze_row(self, row: pd.Series) -> QCResult:
        """Analyze a single row."""
        # Extract base info
        serial = self._safe_str(row, self._cols.get("serial"))
        customer = self._safe_str(row, self._cols.get("customer_name"))
        agency = self._safe_str(row, self._cols.get("agency"))
        courier = self._safe_str(row, self._cols.get("courier"))
        score = self._safe_float(row, self._cols.get("score"))

        # Calculate delivery hours
        delivery_hours = self._calculate_delivery_hours(row)

        # ── محاسبه تازگی نظرسنجی ──
        survey_hours: Optional[float] = None
        freshness_trust: float = 1.0
        freshness_label: str = "نامشخص"

        if self._freshness is not None:
            survey_hours, freshness_trust, freshness_label = (
                self._freshness.evaluate(row, self._cols)
            )
        # ──────────────────────────

        result = QCResult(
            row_index=row.name,
            serial=serial,
            customer_name=customer,
            agency=agency,
            courier=courier,
            score=score,
            delivery_hours=delivery_hours,
            survey_hours=survey_hours,
            freshness_label=freshness_label,
            freshness_trust=freshness_trust,
        )

        # Run all contradiction detectors
        all_contradictions = []
        for detector in self._detectors:
            try:
                found = detector.detect(row, self._cols, self._key_parser)
                all_contradictions.extend(found)
            except Exception as e:
                if self._verbose:
                    print(
                        f"  ⚠ {detector.__class__.__name__} "
                        f"error at row {row.name}: {e}"
                    )

        # اعمال تناقضات با ضریب اعتماد
        result.apply_contradictions(all_contradictions, trust_factor=freshness_trust)
        return result

    def _calculate_delivery_hours(self, row: pd.Series) -> float | None:
        """Calculate delivery hours from entry and delivery dates."""
        entry_col = self._cols.get("entry_date")
        delivery_col = self._cols.get("delivery_date")
        if not entry_col or not delivery_col:
            return None
        return JalaliDateParser.calculate_hours_between(
            row.get(entry_col), row.get(delivery_col)
        )

    @staticmethod
    def _safe_str(row: pd.Series, col: str | None) -> str:
        if col is None:
            return "N/A"
        val = row.get(col, "N/A")
        return str(val) if not pd.isna(val) else "N/A"

    @staticmethod
    def _safe_float(row: pd.Series, col: str | None) -> float:
        if col is None:
            return 0.0
        try:
            return float(row.get(col, 0))
        except (ValueError, TypeError):
            return 0.0
