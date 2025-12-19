#!/usr/bin/env python3
"""Validate patterns.json against Pydantic models."""
import json
import sys
from pathlib import Path

from j_quants_doc_mcp.models.pattern import PatternCollection


def validate_patterns() -> bool:
    """Validate patterns.json file."""
    # パスの設定
    base_dir = Path(__file__).parent
    patterns_file = base_dir / "data" / "patterns.json"

    if not patterns_file.exists():
        print(f"❌ Error: {patterns_file} が見つかりません", file=sys.stderr)
        return False

    # JSONファイルの読み込み
    try:
        with open(patterns_file, encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析エラー: {e}", file=sys.stderr)
        return False
    except Exception as e:
        print(f"❌ ファイル読み込みエラー: {e}", file=sys.stderr)
        return False

    # Pydantic検証
    try:
        pattern_collection = PatternCollection(**data)
        print("✅ patterns.json の検証が成功しました")
        print(f"   - パターン数: {len(pattern_collection.patterns)}")

        # 各パターンの詳細を表示
        for i, pattern in enumerate(pattern_collection.patterns, 1):
            print(f"\n{i}. {pattern.pattern_name}")
            print(f"   説明: {pattern.description}")
            print(f"   関連エンドポイント数: {len(pattern.related_endpoints)}")
            print(f"   注意点数: {len(pattern.notes)}")
            print(f"   サンプルコードパス: {pattern.sample_code_path or 'なし'}")

        return True
    except Exception as e:
        print(f"❌ Pydantic検証エラー: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point."""
    success = validate_patterns()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
