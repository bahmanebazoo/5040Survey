"""
Parses the key/reference sheet into structured KeyEntry objects.
Handles both string ('+', '-') and numeric score columns.
"""

from typing import Optional

import pandas as pd

from src.config.settings import Settings
from src.models.entities import KeyEntry
from src.models.exceptions import KeySheetError


class KeySheetParser:
    """
    Parses the key sheet and builds:
    - Positive/negative option sets
    - Contradiction pair list (hard-coded + dynamically detected)
    """

    def __init__(self, key_df: pd.DataFrame, settings: Optional[Settings] = None):
        self._raw = key_df.copy()
        self._settings = settings or Settings()
        self._entries: list[KeyEntry] = []
        self._positive_options: set[str] = set()
        self._negative_options: set[str] = set()
        self._contradiction_pairs: list[tuple[str, str]] = []
        self._parse()

    # ---- Public API ----

    @property
    def positive_options(self) -> set[str]:
        return self._positive_options

    @property
    def negative_options(self) -> set[str]:
        return self._negative_options

    @property
    def contradiction_pairs(self) -> list[tuple[str, str]]:
        return self._contradiction_pairs

    @property
    def entries(self) -> list[KeyEntry]:
        return list(self._entries)

    # ---- Parsing Logic ----

    def _parse(self):
        df = self._raw
        option_col = self._find_column(df, ["option", "گزینه", "آپشن"])
        score_col = self._find_column(df, ["score", "امتیاز", "نمره", "+/-", "score (+/-)"])
        priority_col = self._find_column(df, ["priority", "اولویت", "ترتیب"])

        if option_col is None:
            raise KeySheetError(
                f"Cannot find 'Option' column in key sheet. "
                f"Available columns: {list(df.columns)}"
            )

        for _, row in df.iterrows():
            option_raw = row.get(option_col, "")
            if pd.isna(option_raw) or str(option_raw).strip() == "":
                continue

            option = str(option_raw).strip()
            sentiment = self._parse_sentiment(
                row.get(score_col, "+") if score_col else "+"
            )
            priority = self._parse_priority(
                row.get(priority_col, 1) if priority_col else 1
            )

            entry = KeyEntry(option=option, sentiment=sentiment, priority=priority)
            self._entries.append(entry)

            if sentiment == "+":
                self._positive_options.add(option)
            else:
                self._negative_options.add(option)

        self._build_contradiction_pairs()

    def _build_contradiction_pairs(self):
        """Combine hard-coded pairs with dynamically detected ones."""
        pairs = set()

        # Hard-coded known pairs
        for p, n in self._settings.known_contradiction_pairs:
            pairs.add((p, n))

        # Dynamic: pair positive vs negative with semantic overlap
        for pos in self._positive_options:
            for neg in self._negative_options:
                if self._are_semantically_contradictory(pos, neg):
                    pairs.add((pos, neg))

        self._contradiction_pairs = list(pairs)

    def _are_semantically_contradictory(self, pos: str, neg: str) -> bool:
        """Check using keyword mapping from settings."""
        for positive_key, neg_keywords in self._settings.contradiction_keywords.items():
            if positive_key in pos:
                for nk in neg_keywords:
                    if nk in neg:
                        return True

        # Fallback: shared content words with negation indicator
        pos_words = set(pos.split())
        neg_words = set(neg.split())
        negation_indicators = {"عدم", "نا", "بدون", "نامناسب"}
        trivial = {"و", "در", "به", "با", "از", "کالا", "بسته"}
        shared = (pos_words & neg_words) - trivial
        if len(shared) >= 1 and neg_words & negation_indicators:
            return True

        return False

    # ---- Static Helpers ----

    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
        cols_lower = {str(c).strip().lower(): c for c in df.columns}
        for candidate in candidates:
            if candidate.lower() in cols_lower:
                return cols_lower[candidate.lower()]
        for candidate in candidates:
            for col_lower, col_original in cols_lower.items():
                if candidate.lower() in col_lower:
                    return col_original
        return None

    @staticmethod
    def _parse_sentiment(value) -> str:
        """Convert any score representation to '+' or '-'."""
        if pd.isna(value):
            return "+"
        s = str(value).strip()
        if s in ("+", "مثبت", "1", "positive", "pos"):
            return "+"
        if s in ("-", "منفی", "-1", "negative", "neg"):
            return "-"
        try:
            return "+" if float(s) >= 0 else "-"
        except (ValueError, TypeError):
            return "+"

    @staticmethod
    def _parse_priority(value) -> int:
        if pd.isna(value):
            return 1
        try:
            return int(float(str(value).strip()))
        except (ValueError, TypeError):
            return 1
