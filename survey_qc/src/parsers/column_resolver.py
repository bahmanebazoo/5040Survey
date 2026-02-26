"""Flexible column name resolution for survey DataFrames."""

from typing import Optional

import pandas as pd

from src.config.settings import Settings
from src.models.exceptions import ColumnNotFoundError


class ColumnResolver:
    """
    Resolves logical column names to actual DataFrame column names.

    Handles variations in naming by trying exact match, then substring match.
    """

    def __init__(self, df: pd.DataFrame, settings: Optional[Settings] = None):
        self._df_columns = list(df.columns)
        self._settings = settings or Settings()
        self._resolved: dict[str, Optional[str]] = {}
        self._resolve_all()

    def get(self, key: str) -> Optional[str]:
        """Get the resolved column name, or None if not found."""
        return self._resolved.get(key)

    def get_or_raise(self, key: str) -> str:
        """Get the resolved column name, or raise if not found."""
        col = self.get(key)
        if col is None:
            raise ColumnNotFoundError(key, self._df_columns)
        return col

    @property
    def resolved_map(self) -> dict[str, Optional[str]]:
        """Return the full resolution map (for debugging)."""
        return dict(self._resolved)

    # ---- Private ----

    def _resolve_all(self):
        for key, candidates in self._settings.column_mappings.items():
            self._resolved[key] = self._find(candidates)

    def _find(self, candidates: list[str]) -> Optional[str]:
        cols_map = {str(c).strip(): c for c in self._df_columns}
        cols_lower = {str(c).strip().lower(): c for c in self._df_columns}

        # 1. Exact match
        for candidate in candidates:
            if candidate in cols_map:
                return cols_map[candidate]

        # 2. Case-insensitive exact match
        for candidate in candidates:
            if candidate.lower() in cols_lower:
                return cols_lower[candidate.lower()]

        # 3. Substring match
        for candidate in candidates:
            for col_lower, col_original in cols_lower.items():
                if candidate.lower() in col_lower:
                    return col_original

        return None
