"""
Detector: Score-Notes contradictions.
Finds cases where numerical score is inconsistent with qualitative notes.
"""

import pandas as pd

from src.config.settings import Settings
from src.models.entities import Contradiction
from src.models.enums import ContradictionType
from src.parsers.column_resolver import ColumnResolver
from src.parsers.key_sheet_parser import KeySheetParser
from src.parsers.note_parser import NoteParser

from .base import ContradictionDetector


class ScoreNotesDetector(ContradictionDetector):
    """
    Detects contradictions between numerical score and qualitative notes.

    Example 1: Score=5 with multiple negative notes and no positive notes.
    Example 2: Score=1 with only positive notes and no negative notes.
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

        score_col = cols.get("score")
        if not score_col:
            return contradictions

        try:
            score = float(row.get(score_col, 0))
        except (ValueError, TypeError):
            return contradictions

        pos_notes = NoteParser.parse(
            row.get(cols.get("positive_notes")) if cols.get("positive_notes") else None
        )
        neg_notes = NoteParser.parse(
            row.get(cols.get("negative_notes")) if cols.get("negative_notes") else None
        )

        pos_count = len(pos_notes)
        neg_count = len(neg_notes)
        penalties = self._settings.penalties

        # HIGH score + MANY negatives
        contradictions.extend(
            self._check_high_score(row.name, score, pos_count, neg_count, penalties)
        )

        # LOW score + ALL positives
        contradictions.extend(
            self._check_low_score(row.name, score, pos_count, neg_count, penalties)
        )

        # MIDDLE score + extreme notes
        contradictions.extend(
            self._check_middle_score(row.name, score, pos_count, neg_count, penalties)
        )

        return contradictions

    @staticmethod
    def _check_high_score(
        row_index, score, pos_count, neg_count, penalties
    ) -> list[Contradiction]:
        """Check high score (>=4) with disproportionate negatives."""
        results = []

        if score < 4:
            return results

        if neg_count >= 2 and pos_count == 0:
            results.append(Contradiction(
                row_index=row_index,
                contradiction_type=ContradictionType.SCORE_NOTES,
                description=(
                    f"امتیاز {score} ولی {neg_count} نکته منفی "
                    f"و بدون نکته مثبت"
                ),
                penalty=penalties.score_notes_severe,
                detail=f"امتیاز: {score}, مثبت: {pos_count}, منفی: {neg_count}",
            ))
        elif neg_count >= 1 and pos_count <= neg_count:
            results.append(Contradiction(
                row_index=row_index,
                contradiction_type=ContradictionType.SCORE_NOTES,
                description=(
                    f"امتیاز {score} ولی نکات منفی ({neg_count}) "
                    f"بیشتر/مساوی مثبت ({pos_count})"
                ),
                penalty=penalties.score_notes_moderate,
                detail=f"امتیاز: {score}, مثبت: {pos_count}, منفی: {neg_count}",
            ))

        return results

    @staticmethod
    def _check_low_score(
        row_index, score, pos_count, neg_count, penalties
    ) -> list[Contradiction]:
        """Check low score (<=2) with disproportionate positives."""
        results = []

        if score > 2:
            return results

        if pos_count >= 2 and neg_count == 0:
            results.append(Contradiction(
                row_index=row_index,
                contradiction_type=ContradictionType.SCORE_NOTES,
                description=(
                    f"امتیاز {score} ولی {pos_count} نکته مثبت "
                    f"و بدون نکته منفی"
                ),
                penalty=penalties.score_notes_severe,
                detail=f"امتیاز: {score}, مثبت: {pos_count}, منفی: {neg_count}",
            ))
        elif pos_count >= 1 and neg_count == 0:
            results.append(Contradiction(
                row_index=row_index,
                contradiction_type=ContradictionType.SCORE_NOTES,
                description=(
                    f"امتیاز {score} ولی نکات مثبت موجود بدون نکته منفی"
                ),
                penalty=penalties.score_notes_moderate,
                detail=f"امتیاز: {score}, مثبت: {pos_count}, منفی: {neg_count}",
            ))

        return results

    @staticmethod
    def _check_middle_score(
        row_index, score, pos_count, neg_count, penalties
    ) -> list[Contradiction]:
        """Check middle score (3) with extreme notes."""
        results = []

        if score != 3:
            return results

        if neg_count >= 3 and pos_count == 0:
            results.append(Contradiction(
                row_index=row_index,
                contradiction_type=ContradictionType.SCORE_NOTES,
                description=(
                    f"امتیاز {score} ولی {neg_count} نکته منفی بدون مثبت"
                ),
                penalty=penalties.score_notes_mild,
                detail=f"امتیاز: {score}, مثبت: {pos_count}, منفی: {neg_count}",
            ))

        return results
