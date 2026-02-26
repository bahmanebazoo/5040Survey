"""
Main Pipeline — Composition Root.
Wires all components together and orchestrates the full QC workflow.
"""

from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from src.config.settings import Settings
from src.detectors import (
    ContradictionDetector,
    QualitativeQualitativeDetector,
    QuantitativeQualitativeDetector,
    ScoreNotesDetector,
)
from src.engine.qc_engine import QCEngine
from src.models.entities import QCResult
from src.models.enums import QCStatus
from src.models.exceptions import DataLoadError
from src.parsers.column_resolver import ColumnResolver
from src.parsers.key_sheet_parser import KeySheetParser
from src.reporting.report_generator import ExcelReportGenerator


class SurveyQCPipeline:
    """
    Single entry point for the entire QC system.
    """

    def __init__(
        self,
        input_path: str,
        output_path: str = "qc_report.xlsx",
        settings: Optional[Settings] = None,
        verbose: bool = False,
    ):
        self._input_path = input_path
        self._output_path = output_path
        self._settings = settings or Settings()
        self._verbose = verbose

    def run(self) -> list[QCResult]:
        """Execute the full QC pipeline."""
        self._print_header()

        # 1. Load data
        print("\n📥 بارگذاری داده‌ها...")
        survey_df, key_df = self._load_data()
        print(f"   ✅ تعداد نظرسنجی: {len(survey_df)}")
        print(f"   ✅ تعداد ردیف کلید: {len(key_df)}")

        # 2. Parse key sheet
        print("\n🔑 پردازش شیت کلیدها...")
        key_parser = KeySheetParser(key_df, self._settings)
        print(f"   ✅ گزینه‌های مثبت: {key_parser.positive_options}")
        print(f"   ✅ گزینه‌های منفی: {key_parser.negative_options}")
        print(f"   ✅ جفت‌های متناقض ({len(key_parser.contradiction_pairs)}):")
        for pos, neg in key_parser.contradiction_pairs:
            print(f"      • «{pos}» ↔ «{neg}»")

        # 3. Resolve columns
        print("\n📋 شناسایی ستون‌ها...")
        col_resolver = ColumnResolver(survey_df, self._settings)
        self._print_column_resolution(col_resolver)

        # 4. Build detectors
        detectors = self._build_detectors()

        # 5. Run QC engine
        print("\n⚙️ اجرای موتور کنترل کیفیت...")
        engine = QCEngine(detectors, key_parser, col_resolver, self._verbose)
        results = engine.analyze(survey_df)

        # 6. Print summary
        self._print_summary(results)

        # 7. Generate report
        print("\n📊 تولید گزارش اکسل...")
        report_gen = ExcelReportGenerator(results, survey_df, key_parser, col_resolver)
        report_gen.generate(self._output_path)

        self._print_footer()
        return results

    # ── Data Loading ──────────────────────────────────────────

    def _load_data(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        path = Path(self._input_path)
        if not path.exists():
            raise DataLoadError(f"File not found: {self._input_path}")

        try:
            xls = pd.ExcelFile(self._input_path)
        except Exception as e:
            raise DataLoadError(f"Cannot open Excel file: {e}")

        sheet_names = xls.sheet_names
        print(f"   📄 شیت‌های موجود: {sheet_names}")

        survey_sheet = self._find_sheet(sheet_names, ["survey", "نظرسنجی", "data"])
        if survey_sheet is None:
            survey_sheet = sheet_names[0]
        print(f"   → شیت نظرسنجی: {survey_sheet}")

        key_sheet = self._find_sheet(sheet_names, ["key", "کلید", "keys", "reference"])
        if key_sheet is None and len(sheet_names) > 1:
            key_sheet = sheet_names[1]
        print(f"   → شیت کلید: {key_sheet}")

        survey_df = pd.read_excel(self._input_path, sheet_name=survey_sheet)

        if key_sheet:
            key_df = pd.read_excel(self._input_path, sheet_name=key_sheet)
        else:
            print("   ⚠️ شیت کلید یافت نشد — استفاده از پیش‌فرض")
            key_df = pd.DataFrame(self._settings.default_key_data)

        return survey_df, key_df

    # ── Detectors ─────────────────────────────────────────────

    def _build_detectors(self) -> list[ContradictionDetector]:
        return [
            QualitativeQualitativeDetector(self._settings),
            QuantitativeQualitativeDetector(self._settings),
            ScoreNotesDetector(self._settings),
        ]

    # ── Helpers ───────────────────────────────────────────────

    @staticmethod
    def _find_sheet(names: list[str], candidates: list[str]) -> Optional[str]:
        for candidate in candidates:
            for name in names:
                if candidate.lower() in name.lower():
                    return name
        return None

    @staticmethod
    def _print_column_resolution(col_resolver: ColumnResolver):
        important_keys = [
            "serial", "customer_name", "score", "positive_notes",
            "negative_notes", "entry_date", "delivery_date", "agency", "courier",
        ]
        for key in important_keys:
            resolved = col_resolver.get(key)
            status = f"→ {resolved}" if resolved else "⚠️ NOT FOUND"
            print(f"   {key}: {status}")

    @staticmethod
    def _print_summary(results: list[QCResult]):
        total = len(results)
        if total == 0:
            print("   ⚠️ هیچ داده‌ای برای تحلیل یافت نشد")
            return

        confirmed = sum(1 for r in results if r.status == QCStatus.CONFIRM)
        review = sum(1 for r in results if r.status == QCStatus.REVIEW)
        rejected = sum(1 for r in results if r.status == QCStatus.REJECT)
        total_contra = sum(r.contradiction_count for r in results)
        with_contra = sum(1 for r in results if r.has_contradictions)
        avg_reliability = np.mean([r.reliability_score for r in results])

        print(f"\n{'─' * 50}")
        print(f"📊 خلاصه نتایج:")
        print(f"{'─' * 50}")
        print(f"   📋 کل نظرسنجی‌ها:        {total}")
        print(f"   ✅ تأیید:                {confirmed} ({confirmed/total*100:.1f}%)")
        print(f"   ⚠️  نیاز به بررسی:       {review} ({review/total*100:.1f}%)")
        print(f"   ❌ رد:                   {rejected} ({rejected/total*100:.1f}%)")
        print(f"   🔴 تعداد کل تناقضات:     {total_contra}")
        print(f"   🔍 نظرسنجی‌های با تناقض:  {with_contra}")
        print(f"   📊 میانگین اعتبار:        {avg_reliability:.1f}")

        # Show problematic rows
        problematic = [r for r in results if r.has_contradictions]
        if problematic:
            print(f"\n   🔍 نمونه‌های مشکل‌دار (حداکثر 15):")
            for r in problematic[:15]:
                contras = " | ".join(c.description for c in r.contradictions)
                print(
                    f"      سریال {r.serial} | {r.customer_name} | "
                    f"اعتبار: {r.reliability_score:.0f} | {r.status.label}"
                )
                print(f"        → {contras}")

    @staticmethod
    def _print_header():
        print("=" * 60)
        print("🔍 سیستم کنترل کیفیت خودکار نظرسنجی مشتریان")
        print("   نسخه 1.1 — رفع مشکل تناقضات کیفی-کیفی")
        print("=" * 60)

    @staticmethod
    def _print_footer():
        print("\n" + "=" * 60)
        print("✅ عملیات با موفقیت انجام شد!")
        print("=" * 60)
