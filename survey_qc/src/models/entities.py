"""Domain entities — immutable value objects and mutable result containers."""

from dataclasses import dataclass, field
from typing import Optional

from .enums import QCStatus, ContradictionType


@dataclass(frozen=True)
class KeyEntry:
    """A single entry from the key/reference sheet."""
    option: str
    sentiment: str  # '+' or '-'
    priority: int


@dataclass(frozen=True)
class Contradiction:
    """Immutable record of a single detected contradiction."""
    row_index: int
    contradiction_type: ContradictionType
    description: str
    penalty: float
    detail: str = ""


@dataclass
class QCResult:
    """QC analysis result for a single survey row."""
    row_index: int
    serial: str
    customer_name: str
    agency: str
    courier: str
    score: float
    reliability_score: float = 100.0
    status: QCStatus = QCStatus.CONFIRM
    contradictions: list[Contradiction] = field(default_factory=list)
    delivery_hours: Optional[float] = None

    # فیلدهای تازگی نظرسنجی
    survey_hours: Optional[float] = None
    freshness_label: str = "نامشخص"
    freshness_trust: float = 1.0

    def apply_contradictions(
        self,
        contradictions: list[Contradiction],
        trust_factor: float = 1.0,
    ):
        """
        Apply detected contradictions and update reliability score.

        جریمه بر اساس ضریب اعتماد تازگی نظرسنجی تنظیم می‌شود:
        - مشکوک (≤1h): تشدید جریمه (تقسیم بر 0.7)
        - طلایی (1-6h): بدون تغییر
        - عادی (6-24h): تخفیف 10%
        - کم‌رنگ (24-72h): تخفیف 25%
        - کهنه (>72h): تخفیف 50%
        """
        self.contradictions.extend(contradictions)
        raw_penalty = sum(c.penalty for c in self.contradictions)

        # تنظیم جریمه بر اساس تازگی
        if trust_factor == 1.0 or self.survey_hours is None:
            adjusted_penalty = raw_penalty
        elif self.survey_hours is not None and self.survey_hours <= 1.0:
            # مشکوک: تشدید جریمه
            adjusted_penalty = raw_penalty / trust_factor if trust_factor > 0 else raw_penalty
        else:
            # کهنه/کم‌رنگ: تخفیف جریمه
            adjusted_penalty = raw_penalty * trust_factor

        self.reliability_score = max(0.0, min(100.0, 100.0 - adjusted_penalty))
        self.status = QCStatus.from_score(self.reliability_score)

    @property
    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0

    @property
    def contradiction_count(self) -> int:
        return len(self.contradictions)
