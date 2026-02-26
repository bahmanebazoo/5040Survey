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
        Parse a raw note value into a list of trimmed, normalized strings.
        """
        if pd.isna(value) or str(value).strip() == "":
            return []

        raw = str(value).strip()
        parts = cls._SEPARATOR_PATTERN.split(raw)
        return [cls._normalize(p) for p in parts if p.strip()]

    @classmethod
    def contains_keyword(cls, notes: list[str], keyword: str) -> bool:
        """Check if any note contains the given keyword (normalized)."""
        keyword_norm = cls._normalize(keyword)
        return any(keyword_norm in note for note in notes)

    @classmethod
    def contains_any_keyword(cls, notes: list[str], keywords: list[str]) -> bool:
        """Check if any note contains any of the given keywords (normalized)."""
        keywords_norm = [cls._normalize(k) for k in keywords]
        return any(
            kn in note
            for note in notes
            for kn in keywords_norm
        )

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize Persian text for consistent comparison:
        - Strip whitespace
        - Remove half-space (\\u200c)
        - Normalize ي→ی, ك→ک, ة→ه
        - Collapse multiple spaces
        """
        t = text.strip()
        t = t.replace("\u200c", " ")
        t = t.replace("ي", "ی")
        t = t.replace("ك", "ک")
        t = t.replace("ة", "ه")
        t = " ".join(t.split())
        return t
