"""
Detector: Quantitative-Qualitative contradictions.
Finds cases where delivery time data contradicts qualitative feedback.
"""

import pandas as pd

from src.config.settings import Settings
from src.models.entities import Contradiction
from src.models.enums import ContradictionType
from src.parsers.column_resolver import ColumnResolver
from src.parsers.date_parser import JalaliDateParser
from src.parsers.key_sheet_parser import KeySheetParser
from src.parsers.note_parser import NoteParser

from .base import ContradictionDetector


class QuantitativeQualitativeDetector(ContradictionDetector):
    """
    Detects contradictions between delivery time and qualitative notes.

    Example 1: Delivery took 48 hours but customer says "تحویل به موقع".
    Example 2: Delivery took 2 hours but customer complains about delay.
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()

    def detect(
        self,
        row: pd.Series,
        cols: ColumnResolver,
        key_parser: KeySheetParser,
    ) -> list[Contradiction]:
        contradictions = []

        entry_col = cols.get("entry_date")
        delivery_col = cols.get("delivery_date")

        if not entry_col or not delivery_col:
            return contradictions

        hours = JalaliDateParser.calculate_hours_between(
            row.get(entry_col), row.get(delivery_col)
        )
        if hours is None:
            return contradictions

        pos_notes = NoteParser.parse(
            row.get(cols.get("positive_notes")) if cols.get("positive_notes") else None
        )
        neg_notes = NoteParser.parse(
            row.get(cols.get("negative_notes")) if cols.get("negative_notes") else None
        )

        has_ontime = NoteParser.contains_keyword(pos_notes, "تحویل به موقع")
        has_delay = NoteParser.contains_any_keyword(
            neg_notes, ["تاخیر", "تأخیر", "دیر"]
        )

        thresholds = self._settings.delivery
        penalties = self._settings.penalties

        # Slow delivery + on-time claim
        if hours > thresholds.slow and has_ontime:
            penalty = (
                penalties.quant_qual_very_slow
                if hours > thresholds.very_slow
                else penalties.quant_qual_slow
            )
            contradictions.append(Contradiction(
                row_index=row.name,
                contradiction_type=ContradictionType.QUANTITATIVE_QUALITATIVE,
                description=(
                    f"زمان تحویل {hours:.1f} ساعت "
                    f"ولی «تحویل به موقع» انتخاب شده"
                ),
                penalty=penalty,
                detail=f"ساعت تحویل: {hours:.1f}",
            ))

        # Fast delivery + delay complaint
        if hours < thresholds.fast and has_delay:
            contradictions.append(Contradiction(
                row_index=row.name,
                contradiction_type=ContradictionType.QUANTITATIVE_QUALITATIVE,
                description=(
                    f"زمان تحویل {hours:.1f} ساعت "
                    f"ولی شکایت از تأخیر ثبت شده"
                ),
                penalty=penalties.quant_qual_fast_with_complaint,
                detail=f"ساعت تحویل: {hours:.1f}",
            ))

        return contradictions
