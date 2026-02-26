"""Jalali (Persian) date parsing and conversion utilities."""

import re
from typing import Optional

import pandas as pd


class JalaliDateParser:
    """
    Handles parsing Jalali date strings and converting to Gregorian timestamps.
    Tries jdatetime library first, falls back to manual conversion.
    """

    @classmethod
    def parse(cls, value) -> Optional[pd.Timestamp]:
        """
        Parse a Jalali date value to a Gregorian pd.Timestamp.

        Args:
            value: Jalali date string, datetime, Timestamp, or NaN.

        Returns:
            pd.Timestamp in Gregorian, or None if parsing fails.
        """
        if pd.isna(value):
            return None

        if isinstance(value, pd.Timestamp):
            return value

        s = str(value).strip()
        if not s:
            return None

        # Try jdatetime first
        result = cls._try_jdatetime(s)
        if result is not None:
            return result

        # Fallback to manual
        return cls._parse_manual(s)

    @classmethod
    def calculate_hours_between(cls, start, end) -> Optional[float]:
        """
        Calculate hours between two date values.

        Args:
            start: Start date value (Jalali string, Timestamp, etc.)
            end: End date value.

        Returns:
            Hours as float, or None if either date cannot be parsed.
        """
        ts_start = cls.parse(start)
        ts_end = cls.parse(end)
        if ts_start is None or ts_end is None:
            return None
        delta = ts_end - ts_start
        return delta.total_seconds() / 3600.0

    # ---- Private Methods ----

    @classmethod
    def _try_jdatetime(cls, s: str) -> Optional[pd.Timestamp]:
        """Try parsing with jdatetime library."""
        try:
            import jdatetime
        except ImportError:
            return None

        patterns = [
            "%Y/%m/%d %H:%M:%S",
            "%Y/%m/%d %H:%M",
            "%Y/%m/%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
        ]
        for fmt in patterns:
            try:
                jdt = jdatetime.datetime.strptime(s, fmt)
                gdt = jdt.togregorian()
                return pd.Timestamp(gdt)
            except (ValueError, TypeError):
                continue
        return None

    @classmethod
    def _parse_manual(cls, s: str) -> Optional[pd.Timestamp]:
        """Manual Jalali-to-Gregorian conversion (no external dependency)."""
        match = re.match(
            r"(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})"
            r"(?:\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?)?",
            s,
        )
        if not match:
            return None

        jy = int(match.group(1))
        jm = int(match.group(2))
        jd = int(match.group(3))
        hour = int(match.group(4) or 0)
        minute = int(match.group(5) or 0)
        second = int(match.group(6) or 0)

        try:
            gy, gm, gd = cls._jalali_to_gregorian(jy, jm, jd)
            return pd.Timestamp(
                year=gy, month=gm, day=gd,
                hour=hour, minute=minute, second=second,
            )
        except (ValueError, OverflowError):
            return None

    @staticmethod
    def _jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
        """
        Convert a Jalali date to Gregorian.

        Algorithm based on the standard Jalali-Gregorian conversion formula.
        """
        jy -= 979
        jm -= 1
        jd -= 1

        month_days = [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29]

        j_day_no = 365 * jy + (jy // 33) * 8 + (jy % 33 + 3) // 4
        for i in range(jm):
            j_day_no += month_days[i]
        j_day_no += jd

        g_day_no = j_day_no + 79

        gy = 1600 + 400 * (g_day_no // 146097)
        g_day_no %= 146097

        if g_day_no >= 36525:
            g_day_no -= 1
            gy += 100 * (g_day_no // 36524)
            g_day_no %= 36524
            if g_day_no >= 365:
                g_day_no += 1

        gy += 4 * (g_day_no // 1461)
        g_day_no %= 1461

        if g_day_no >= 366:
            gy += (g_day_no - 1) // 365
            g_day_no = (g_day_no - 1) % 365

        g_month_days = [
            31,
            28 + (1 if (gy % 4 == 0 and gy % 100 != 0) or gy % 400 == 0 else 0),
            31, 30, 31, 30, 31, 31, 30, 31, 30, 31,
        ]

        gm = 0
        while gm < 12 and g_day_no >= g_month_days[gm]:
            g_day_no -= g_month_days[gm]
            gm += 1

        return gy, gm + 1, g_day_no + 1
