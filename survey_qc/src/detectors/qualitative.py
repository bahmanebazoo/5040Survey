"""
Detector: Qualitative-Qualitative contradictions.
Finds cases where positive and negative notes contradict each other.
"""

import pandas as pd

from src.config.settings import Settings
from src.models.entities import Contradiction
from src.models.enums import ContradictionType
from src.parsers.column_resolver import ColumnResolver
from src.parsers.key_sheet_parser import KeySheetParser
from src.parsers.note_parser import NoteParser

from .base import ContradictionDetector


class QualitativeQualitativeDetector(ContradictionDetector):
    """
    Detects contradictions between positive and negative notes.

    Example: Customer selects both "تحویل به موقع" and "تاخیر در تحویل".
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

        pos_col = cols.get("positive_notes")
        neg_col = cols.get("negative_notes")

        positive_notes = NoteParser.parse(row.get(pos_col) if pos_col else None)
        negative_notes = NoteParser.parse(row.get(neg_col) if neg_col else None)

        if not positive_notes or not negative_notes:
            return contradictions

        for pos_note in positive_notes:
            for neg_note in negative_notes:
                if self._is_contradictory(pos_note, neg_note, key_parser):
                    contradictions.append(Contradiction(
                        row_index=row.name,
                        contradiction_type=ContradictionType.QUALITATIVE_QUALITATIVE,
                        description=f"«{pos_note}» در تناقض با «{neg_note}»",
                        penalty=self._settings.penalties.qual_qual,
                        detail=f"مثبت: {pos_note} | منفی: {neg_note}",
                    ))

        return contradictions

    def _is_contradictory(
        self, pos: str, neg: str, key_parser: KeySheetParser
    ) -> bool:
        """Check known pairs, then keyword matching."""
        # Known pairs
        for p, n in key_parser.contradiction_pairs:
            if (pos.strip() == p.strip() and neg.strip() == n.strip()) or \
               (pos.strip() == n.strip() and neg.strip() == p.strip()):
                return True

        # Keyword matching from settings
        for positive_key, neg_keywords in self._settings.contradiction_keywords.items():
            if positive_key in pos:
                for nk in neg_keywords:
                    if nk in neg:
                        return True

        return False
