"""
Centralized configuration — all thresholds, defaults, and constants.
Single source of truth for tunable parameters.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeliveryThresholds:
    """Delivery time thresholds in hours."""
    fast: float = 6.0        # Under this = definitely fast
    slow: float = 24.0       # Over this = definitely slow
    very_slow: float = 48.0  # Over this = very slow


@dataclass(frozen=True)
class PenaltyConfig:
    """Penalty points for each contradiction type."""
    # Qualitative-Qualitative
    qual_qual: float = 30.0

    # Quantitative-Qualitative
    quant_qual_very_slow: float = 25.0
    quant_qual_slow: float = 15.0
    quant_qual_fast_with_complaint: float = 10.0

    # Score-Notes
    score_notes_severe: float = 25.0
    score_notes_moderate: float = 15.0
    score_notes_mild: float = 10.0


@dataclass(frozen=True)
class StatusThresholds:
    """Reliability score thresholds for status classification."""
    confirm_min: float = 80.0
    review_min: float = 50.0


@dataclass(frozen=True)
class Settings:
    """Master settings container."""
    delivery: DeliveryThresholds = field(default_factory=DeliveryThresholds)
    penalties: PenaltyConfig = field(default_factory=PenaltyConfig)
    status: StatusThresholds = field(default_factory=StatusThresholds)

    # Column name candidates for flexible resolution
    column_mappings: dict = field(default_factory=lambda: {
        "serial": ["سریال فاکتور", "سریال", "شماره فاکتور", "serial"],
        "customer_name": ["نام مشتری", "مشتری", "نام", "customer"],
        "customer_phone": ["شماره مشتری", "شماره تلفن", "تلفن", "phone"],
        "province": ["استان", "province"],
        "city": ["شهر", "city"],
        "agency": ["نمایندگی", "agency", "نماینده"],
        "registrar": ["ثبت کننده", "ثبت‌کننده", "registrar"],
        "entry_date": ["تاریخ ورود به نمایندگی", "تاریخ ورود", "entry_date"],
        "delivery_date": ["تاریخ تحویل", "delivery_date"],
        "courier": ["نام پیک", "پیک", "courier"],
        "survey_date": ["تاریخ نظر سنجی", "تاریخ نظرسنجی", "survey_date"],
        "score": ["امتیاز", "score", "نمره"],
        "positive_notes": ["نکات مثبت", "مثبت", "positive"],
        "negative_notes": ["نکات منفی", "منفی", "negative"],
        "invoice_amount": ["مبلغ فاکتور", "مبلغ", "amount"],
        "products": ["محصولات", "products"],
    })

    # Known semantic contradiction keywords
    contradiction_keywords: dict = field(default_factory=lambda: {
        "تحویل به موقع": ["تاخیر", "تأخیر", "دیر"],
        "رفتار محترمانه": ["نامناسب", "بد", "بی‌ادب", "بی ادب"],
        "رعایت اصول بهداشتی": ["عدم بهداشت", "عدم رعایت", "کثیف"],
        "بسته بندی مناسب": ["عدم بسته بندی", "بسته بندی نامناسب", "بدون بسته بندی"],
        "تحویل با پاکت": ["بدون پاکت"],
        "سلامت کالا": ["عدم سلامت", "آسیب"],
    })

    # Known hard-coded contradiction pairs
    known_contradiction_pairs: list = field(default_factory=lambda: [
        ("تحویل به موقع", "تاخیر در تحویل"),
        ("تحویل به موقع", "تأخیر در تحویل"),
        ("تحویل به موقع", "تاخیر تحویل"),
        ("رفتار محترمانه", "رفتار نامناسب"),
        ("رفتار محترمانه", "برخورد نامناسب"),
        ("رعایت اصول بهداشتی", "عدم رعایت بهداشت"),
        ("رعایت اصول بهداشتی", "عدم بهداشت"),
        ("بسته بندی مناسب", "عدم بسته بندی و سلامت کالا"),
        ("بسته بندی مناسب", "بسته بندی نامناسب"),
        ("سلامت کالا", "عدم بسته بندی و سلامت کالا"),
        ("تحویل با پاکت", "تحویل بدون پاکت"),
    ])

    # Default key sheet data (fallback)
    default_key_data: dict = field(default_factory=lambda: {
        "Option": [
            "رفتار محترمانه", "رعایت اصول بهداشتی", "تحویل به موقع",
            "بسته بندی مناسب", "سلامت کالا", "تحویل با پاکت",
            "رفتار نامناسب", "عدم رعایت بهداشت", "تاخیر در تحویل",
            "تأخیر در تحویل", "بسته بندی نامناسب", "عدم بسته بندی و سلامت کالا",
            "تحویل بدون پاکت", "برخورد نامناسب",
        ],
        "Score (+/-)": [
            "+", "+", "+", "+", "+", "+",
            "-", "-", "-", "-", "-", "-", "-", "-",
        ],
        "Priority": [1, 2, 3, 4, 5, 6, 1, 2, 3, 3, 4, 5, 6, 1],
    })
