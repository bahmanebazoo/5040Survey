"""
Survey Freshness Detector
=========================
محاسبه فاصله زمانی بین تحویل و نظرسنجی و تعیین ضریب اعتماد.

این دتکتور جدا از ContradictionDetector هاست:
- ContradictionDetector: متد detect() → لیست Contradiction
- SurveyFreshnessDetector: متد evaluate() → (hours, trust, label)
"""

from typing import Optional

import pandas as pd

from src.config.settings import SurveyFreshnessConfig
from src.parsers.column_resolver import ColumnResolver
from src.parsers.date_parser import JalaliDateParser


class SurveyFreshnessDetector:
    """محاسبه تازگی نظرسنجی و برگرداندن ضریب اعتماد."""

    def __init__(self, config: SurveyFreshnessConfig):
        self._config = config

    def evaluate(
        self,
        row: pd.Series,
        cols: ColumnResolver,
    ) -> tuple[Optional[float], float, str]:
        """
        محاسبه تازگی نظرسنجی.

        Args:
            row: یک سطر از DataFrame
            cols: ColumnResolver برای یافتن نام ستون‌ها

        Returns:
            (hours_gap, trust_factor, persian_label)
        """
        delivery_col = cols.get("delivery_date")
        survey_col = cols.get("survey_date")

        if not delivery_col or not survey_col:
            return None, 1.0, "نامشخص"

        delivery_val = row.get(delivery_col)
        survey_val = row.get(survey_col)

        if pd.isna(delivery_val) or pd.isna(survey_val):
            return None, 1.0, "نامشخص"

        hours = JalaliDateParser.calculate_hours_between(delivery_val, survey_val)

        trust_factor, label = self._config.get_trust_factor(hours)
        return hours, trust_factor, label
