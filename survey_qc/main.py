"""
Survey QC System — Entry Point
===============================
Usage:
    python main.py
    python main.py --input survey.xlsx --output qc_report.xlsx
"""

import argparse
import sys
from pathlib import Path

from src.pipeline.survey_pipeline import SurveyQCPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="🔍 سیستم کنترل کیفیت خودکار نظرسنجی مشتریان",
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        default="survey.xlsx",
        help="Path to input Excel file (default: survey.xlsx)",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="qc_report.xlsx",
        help="Path to output report file (default: qc_report.xlsx)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    if not Path(args.input).exists():
        print(f"❌ فایل ورودی یافت نشد: {args.input}")
        sys.exit(1)

    pipeline = SurveyQCPipeline(
        input_path=args.input,
        output_path=args.output,
        verbose=args.verbose,
    )
    pipeline.run()


if __name__ == "__main__":
    main()
