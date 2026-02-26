"""
Detector: Qualitative-Qualitative contradictions.
Finds cases where positive and negative notes contradict each other.

CRITICAL FIX: Uses ONLY the explicit contradiction pairs from KeySheetParser.
NO keyword matching. NO semantic guessing.
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

    Uses ONLY the 4 explicit pairs defined in Settings:
    1. "تحویل به موقع" ↔ "تاخیر در ارسال سفارش"
    2. "رفتار محترمانه" ↔ "عدم توجه به حریم شخصی"
    3. "رفتار محترمانه" ↔ "رفتار نامناسب"
    4. "رعایت اصول بهداشتی" ↔ "عدم بسته‌بندی و سلامت کالا"
    """

    def __init__(self, settings: Settings | None = None):
        self._settings = settings or Settings()
        self._normalized_pairs: list[tuple[str, str]] | None = None

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

        # Build normalized pairs cache on first call
        if self._normalized_pairs is None:
            self._normalized_pairs = [
                (self._normalize(p), self._normalize(n))
                for p, n in key_parser.contradiction_pairs
            ]

        for pos_note in positive_notes:
            for neg_note in negative_notes:
                if self._is_contradictory(pos_note, neg_note):
                    contradictions.append(Contradiction(
                        row_index=row.name,
                        contradiction_type=ContradictionType.QUALITATIVE_QUALITATIVE,
                        description=f"«{pos_note}» در تناقض با «{neg_note}»",
                        penalty=self._settings.penalties.qual_qual,
                        detail=f"مثبت: {pos_note} | منفی: {neg_note}",
                    ))

        return contradictions

    def _is_contradictory(self, pos: str, neg: str) -> bool:
        """
        Check if a positive note contradicts a negative note.
        Uses ONLY the explicit normalized pairs. Nothing else.
        """
        pos_norm = self._normalize(pos)
        neg_norm = self._normalize(neg)

        for pair_pos_norm, pair_neg_norm in self._normalized_pairs:
            if pos_norm == pair_pos_norm and neg_norm == pair_neg_norm:
                return True

        return False

    @staticmethod
    def _normalize(text: str) -> str:
        """Same normalization as KeySheetParser and NoteParser."""
        t = text.strip()
        t = t.replace("\u200c", " ")
        t = t.replace("ي", "ی")
        t = t.replace("ك", "ک")
        t = t.replace("ة", "ه")
        t = " ".join(t.split())
        return t