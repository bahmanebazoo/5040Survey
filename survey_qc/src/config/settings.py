"""
Centralized configuration — all thresholds, defaults, and constants.
Single source of truth for tunable parameters.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class DeliveryThresholds:
    """Delivery time thresholds in hours."""
    fast: float = 6.0
    slow: float = 24.0
    very_slow: float = 48.0


@dataclass(frozen=True)
class PenaltyConfig:
    """Penalty points for each contradiction type."""
    qual_qual: float = 30.0
    quant_qual_very_slow: float = 25.0
    quant_qual_slow: float = 15.0
    quant_qual_fast_with_complaint: float = 10.0
    score_notes_severe: float = 25.0
    score_notes_moderate: float = 15.0
    score_notes_mild: float = 10.0


@dataclass(frozen=True)
class StatusThresholds:
    """Reliability score thresholds for status classification."""
    confirm_min: float = 80.0
    review_min: float = 50.0


@dataclass(frozen=True)
class SurveyFreshnessConfig:
    """
    تنظیمات تازگی نظرسنجی بر اساس روانشناسی شناختی.
    زمان بر حسب ساعت بین تاریخ تحویل و تاریخ نظرسنجی.
    """
    # مرزهای زمانی (ساعت)
    suspicious_max: float = 1.0
    golden_max: float = 6.0
    normal_max: float = 24.0
    faded_max: float = 72.0

    # ضرایب اعتماد
    suspicious_trust: float = 0.70
    golden_trust: float = 1.00
    normal_trust: float = 0.90
    faded_trust: float = 0.75
    stale_trust: float = 0.50

    def get_trust_factor(self, hours: float | None) -> tuple[float, str]:
        """محاسبه ضریب اعتماد و برچسب فارسی."""
        if hours is None:
            return 1.0, "نامشخص"
        if hours < 0:
            return 1.0, "نامعتبر"
        if hours <= self.suspicious_max:
            return self.suspicious_trust, "مشکوک (≤۱ ساعت)"
        if hours <= self.golden_max:
            return self.golden_trust, "طلایی (۱-۶ ساعت)"
        if hours <= self.normal_max:
            return self.normal_trust, "عادی (۶-۲۴ ساعت)"
        if hours <= self.faded_max:
            return self.faded_trust, "کم‌رنگ (۲۴-۷۲ ساعت)"
        return self.stale_trust, "کهنه (>۷۲ ساعت)"


@dataclass(frozen=True)
class Settings:
    """Master settings container."""
    delivery: DeliveryThresholds = field(default_factory=DeliveryThresholds)
    penalties: PenaltyConfig = field(default_factory=PenaltyConfig)
    status: StatusThresholds = field(default_factory=StatusThresholds)
    freshness: SurveyFreshnessConfig = field(default_factory=SurveyFreshnessConfig)

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

    # ──────────────────────────────────────────────────────────
    # ONLY these 4 pairs are real contradictions.
    # ──────────────────────────────────────────────────────────
    explicit_contradiction_pairs: list = field(default_factory=lambda: [
        ("تحویل به موقع", "تاخیر در ارسال سفارش"),
        ("رفتار محترمانه", "عدم توجه به حریم شخصی"),
        ("رفتار محترمانه", "رفتار نامناسب"),
        ("رعایت اصول بهداشتی", "عدم بسته‌بندی و سلامت کالا"),
    ])

    # Delay keywords for quantitative-qualitative detector
    delay_keywords: list = field(default_factory=lambda: [
        "تاخیر", "تأخیر", "دیر",
        "تاخیر در ارسال", "تأخیر در ارسال",
        "تاخیر در ارسال سفارش", "تأخیر در ارسال سفارش",
    ])

    # On-time keywords for quantitative-qualitative detector
    ontime_keywords: list = field(default_factory=lambda: [
        "تحویل به موقع",
    ])

    # Default key sheet data (fallback if key sheet not found)
    default_key_data: dict = field(default_factory=lambda: {
        "Option": [
            "رفتار محترمانه", "رعایت اصول بهداشتی", "تحویل به موقع",
            "بسته بندی مناسب", "سلامت کالا", "تحویل با پاکت",
            "رفتار نامناسب", "عدم توجه به حریم شخصی",
            "عدم رعایت بهداشت", "تاخیر در ارسال سفارش",
            "بسته بندی نامناسب", "عدم بسته‌بندی و سلامت کالا",
            "تحویل بدون پاکت", "برخورد نامناسب",
        ],
        "Score (+/-)": [
            "+", "+", "+", "+", "+", "+",
            "-", "-", "-", "-", "-", "-", "-", "-",
        ],
        "Priority": [1, 2, 3, 4, 5, 6, 1, 1, 2, 3, 4, 5, 6, 1],
    })
