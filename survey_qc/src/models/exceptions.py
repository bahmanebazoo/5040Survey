"""Custom exceptions for clear error reporting and debugging."""


class SurveyQCError(Exception):
    """Base exception for the Survey QC system."""
    pass


class DataLoadError(SurveyQCError):
    """Raised when data cannot be loaded from the Excel file."""
    pass


class ColumnNotFoundError(SurveyQCError):
    """Raised when a required column cannot be resolved."""
    def __init__(self, key: str, available: list[str]):
        self.key = key
        self.available = available
        super().__init__(
            f"Required column '{key}' not found. "
            f"Available columns: {available}"
        )


class ParseError(SurveyQCError):
    """Raised when data parsing fails."""
    def __init__(self, field_name: str, value, reason: str = ""):
        self.field_name = field_name
        self.value = value
        msg = f"Failed to parse '{field_name}': value={value!r}"
        if reason:
            msg += f" — {reason}"
        super().__init__(msg)


class KeySheetError(SurveyQCError):
    """Raised when the key sheet is malformed."""
    pass


class DetectorError(SurveyQCError):
    """Raised when a contradiction detector encounters an error."""
    def __init__(self, detector_name: str, row_index: int, reason: str):
        self.detector_name = detector_name
        self.row_index = row_index
        super().__init__(
            f"Detector '{detector_name}' failed at row {row_index}: {reason}"
        )
