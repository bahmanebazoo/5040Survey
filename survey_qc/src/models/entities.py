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

    def apply_contradictions(self, contradictions: list[Contradiction]):
        """Apply detected contradictions and update reliability score."""
        self.contradictions.extend(contradictions)
        total_penalty = sum(c.penalty for c in self.contradictions)
        self.reliability_score = max(0.0, min(100.0, 100.0 - total_penalty))
        self.status = QCStatus.from_score(self.reliability_score)

    @property
    def has_contradictions(self) -> bool:
        return len(self.contradictions) > 0

    @property
    def contradiction_count(self) -> int:
        return len(self.contradictions)
