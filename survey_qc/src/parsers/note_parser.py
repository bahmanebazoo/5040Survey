"""Parses comma-separated Persian notes into clean lists."""

import re

import pandas as pd


class NoteParser:
    """
    Stateless utility for parsing survey note fields.

    Notes are comma-separated (English or Persian comma) Persian text.
    Example: "رفتار محترمانه، تحویل به موقع، سلامت کالا"
    """

    # Separators: English comma, Persian comma, newline
    _SEPARATOR_PATTERN = re.compile(r"[,،\n]+")

    @classmethod
    def parse(cls, value) -> list[str]:
        """
        Parse a raw note value into a list of trimmed strings.

        Args:
            value: Raw cell value (str, NaN, None, etc.)

        Returns:
            List of non-empty trimmed note strings.
        """
        if pd.isna(value) or str(value).strip() == "":
            return []

        raw = str(value).strip()
        parts = cls._SEPARATOR_PATTERN.split(raw)
        return [p.strip() for p in parts if p.strip()]

    @classmethod
    def contains_keyword(cls, notes: list[str], keyword: str) -> bool:
        """Check if any note contains the given keyword."""
        return any(keyword in note for note in notes)

    @classmethod
    def contains_any_keyword(cls, notes: list[str], keywords: list[str]) -> bool:
        """Check if any note contains any of the given keywords."""
        return any(
            keyword in note
            for note in notes
            for keyword in keywords
        )
