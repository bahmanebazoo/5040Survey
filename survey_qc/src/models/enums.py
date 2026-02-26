"""Enumerations for the QC system."""

from enum import Enum


class QCStatus(Enum):
    """Survey reliability status classification."""
    CONFIRM = ("✅ تأیید", 80, 101)
    REVIEW = ("⚠️ بررسی", 50, 80)
    REJECT = ("❌ رد", 0, 50)

    def __init__(self, label: str, lower: int, upper: int):
        self.label = label
        self.lower = lower
        self.upper = upper

    @classmethod
    def from_score(cls, score: float) -> "QCStatus":
        """Classify a reliability score into a status."""
        for status in cls:
            if status.lower <= score < status.upper:
                return status
        return cls.REJECT


class ContradictionType(Enum):
    """Types of contradictions the system can detect."""
    QUALITATIVE_QUALITATIVE = "تناقض کیفی-کیفی"
    QUANTITATIVE_QUALITATIVE = "تناقض کمّی-کیفی"
    SCORE_NOTES = "تناقض امتیاز-نکات"
