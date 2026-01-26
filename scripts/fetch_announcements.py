#!/usr/bin/env python3
"""
Fetch company announcements
"""
import sys
from pathlib import Path
import pandas as pd

try:
    import akshare as ak
except ImportError:
    print("Error: akshare not installed. Install with: pip install akshare")
    sys.exit(1)

from utils import save_json, normalize_stock_code


def fetch_announcements(stock_code: str, output_dir: Path) -> list:
    """Fetch company announcements"""
    try:
        print("Fetching company announcements...")
        code_without_suffix = stock_code.split('.')[0]

        # Get announcements
        announcements = ak.stock_notice_report(symbol=code_without_suffix)

        if announcements.empty:
            print("  ✗ No announcements found")
            return []

        # Save to CSV
        announcements.to_csv(
            output_dir / 'raw_data' / 'announcements' / 'all_announcements.csv',
            index=False,
            encoding='utf-8-sig'
        )

        # Filter important announcements
        important_keywords = [
            '重大', '分红', '派息', '业绩', '预告', '快报',
            '重组', '并购', '收购', '增持', '减持', '股权',
            '诉讼', '仲裁', '处罚', '调查', '风险'
        ]

        important_announcements = []
        for _, row in announcements.iterrows():
            title = str(row.get('公告标题', ''))
            if any(keyword in title for keyword in important_keywords):
                important_announcements.append(row.to_dict())

        # Save important announcements
        if important_announcements:
            save_json(
                important_announcements,
                output_dir / 'processed_data' / 'important_announcements.json'
            )

        print(f"  ✓ Total announcements: {len(announcements)}")
        print(f"  ✓ Important announcements: {len(important_announcements)}")

        return important_announcements

    except Exception as e:
        print(f"  ✗ Failed to fetch announcements: {e}")
        return []


def main(stock_code: str, output_dir: Path):
    """Main function"""
    normalized_code, market, market_type = normalize_stock_code(stock_code)

    print(f"\n{'='*60}")
    print(f"Fetching Announcements for {normalized_code}")
    print(f"{'='*60}\n")

    if market_type == 'HK':
        print("Note: Hong Kong stock announcements require manual collection")
        print("Please visit HKEx website: www.hkexnews.hk")
        announcements = []
    else:
        announcements = fetch_announcements(normalized_code, output_dir)

    print(f"\n{'='*60}")
    print("Announcement collection completed!")
    print(f"{'='*60}\n")

    return announcements


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python fetch_announcements.py <stock_code> <output_dir>")
        sys.exit(1)

    stock_code = sys.argv[1]
    output_dir = Path(sys.argv[2])

    main(stock_code, output_dir)