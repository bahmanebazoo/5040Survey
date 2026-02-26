"""
Parses the key/reference sheet into structured KeyEntry objects.

CRITICAL FIX: Contradiction pairs come ONLY from Settings.explicit_contradiction_pairs.
NO priority-based guessing. NO keyword matching. ONLY explicit pairs.
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
    - Contradiction pairs (ONLY from explicit settings)
    """

    def __init__(self, key_df: pd.DataFrame, settings: Optional[Settings] = None):
        self._raw = key_df.copy()
        self._settings = settings or Settings()
        self._entries: list[KeyEntry] = []
        self._positive_options: set[str] = set()
        self._negative_options: set[str] = set()
        self._contradiction_pairs: list[tuple[str, str]] = []
        self._parse()

    # ── Public API ────────────────────────────────────────────

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

    # ── Parsing Logic ─────────────────────────────────────────

    def _parse(self):
        df = self._raw
        option_col = self._find_column(df, ["option", "گزینه", "آپشن"])
        score_col = self._find_column(df, [
            "score", "امتیاز", "نمره", "+/-", "score (+/-)",
            "score(+/-)", "نوع",
        ])
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

        # ONLY explicit pairs — nothing else
        self._build_contradiction_pairs()

    def _build_contradiction_pairs(self):
        """
        Build contradiction pairs ONLY from Settings.explicit_contradiction_pairs.

        NO priority-based pairing.
        NO keyword guessing.

        Uses normalized text to match against actual key sheet options,
        but the pairs themselves come ONLY from explicit configuration.
        """
        pairs = []
        all_options_normalized = {
            self._normalize(e.option): e.option for e in self._entries
        }

        for pos, neg in self._settings.explicit_contradiction_pairs:
            # Try to resolve each side to the actual key sheet text
            pos_norm = self._normalize(pos)
            neg_norm = self._normalize(neg)

            pos_actual = all_options_normalized.get(pos_norm, pos)
            neg_actual = all_options_normalized.get(neg_norm, neg)

            pairs.append((pos_actual, neg_actual))

        self._contradiction_pairs = pairs

    # ── Text Normalization ────────────────────────────────────

    @staticmethod
    def _normalize(text: str) -> str:
        """
        Normalize Persian text for comparison:
        - Remove half-space (\\u200c)
        - Normalize ی/ک/ة
        - Strip and collapse whitespace
        """
        if not text:
            return ""
        t = text.strip()
        t = t.replace("\u200c", " ")
        t = t.replace("ي", "ی")
        t = t.replace("ك", "ک")
        t = t.replace("ة", "ه")
        t = " ".join(t.split())
        return t

    # ── Column / Value Helpers ────────────────────────────────

    @staticmethod
    def _find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
        cols_lower = {str(c).strip().lower(): c for c in df.columns}
        for candidate in candidates:
            if candidate.lower() in cols_lower:
                return cols_lower[candidate.lower()]
        # Substring fallback
        for candidate in candidates:
            for col_lower, col_original in cols_lower.items():
                if candidate.lower() in col_lower:
                    return col_original
        return None

    @staticmethod
    def _parse_sentiment(value) -> str:
        if pd.isna(value):
            return "+"
        s = str(value).strip()
        if s in ("+", "مثبت", "1", "1.0", "positive", "pos"):
            return "+"
        if s in ("-", "منفی", "-1", "-1.0", "negative", "neg"):
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