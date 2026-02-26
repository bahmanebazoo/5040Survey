"""Abstract base class for all contradiction detectors."""

from abc import ABC, abstractmethod

import pandas as pd

from src.models.entities import Contradiction
from src.parsers.column_resolver import ColumnResolver
from src.parsers.key_sheet_parser import KeySheetParser


class ContradictionDetector(ABC):
    """
    Strategy interface for contradiction detection.

    New detection rules can be added by subclassing this
    without modifying the QC engine (Open/Closed Principle).
    """

    @abstractmethod
    def detect(
        self,
        row: pd.Series,
        cols: ColumnResolver,
        key_parser: KeySheetParser,
    ) -> list[Contradiction]:
        """
        Analyze a single survey row and return detected contradictions.

        Args:
            row: A single row from the survey DataFrame.
            cols: Column resolver for flexible column access.
            key_parser: Parsed key sheet data.

        Returns:
            List of Contradiction objects found in this row.
        """
        ...
