"""Search tool for J-Quants API documentation."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

ENDPOINTS_DATA_PATH = Path(__file__).parent.parent / "data" / "endpoints.json"


def _load_endpoints() -> dict[str, Any]:
    """エンドポイントデータをロード"""
    with open(ENDPOINTS_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def search_endpoints(keyword: str, category: str | None = None) -> dict[str, Any]:
    """エンドポイントをキーワードとカテゴリで検索する。

    Args:
        keyword: 検索キーワード(エンドポイント名、パス、説明から検索)
        category: オプションのカテゴリフィルタ(auth, listed, prices, fins等)

    Returns:
        検索結果を含む辞書(該当件数と結果配列)
    """
    logger.info(
        f"search_endpoints called with keyword='{keyword}', category='{category}'"
    )

    data = _load_endpoints()
    keyword_lower = keyword.lower()

    # 検索処理
    results = []
    for endpoint in data.get("endpoints", []):
        # キーワード検索(名前、日本語名、英語名、パス、旧パス、説明)
        if not (
            keyword_lower in endpoint.get("name", "").lower()
            or keyword_lower in endpoint.get("name_ja", "").lower()
            or keyword_lower in endpoint.get("name_en", "").lower()
            or keyword_lower in endpoint.get("path", "").lower()
            or keyword_lower in endpoint.get("path_old", "").lower()
            or keyword_lower in endpoint.get("description", "").lower()
        ):
            continue

        # カテゴリフィルタリング(パスベース)
        if category:
            # パスからカテゴリを抽出 (例: /listed/*, /prices/*, /fins/*)
            path = endpoint.get("path", "")
            path_category = path.split("/")[1] if "/" in path else ""
            if category.lower() != path_category.lower():
                continue

        # 結果に追加
        results.append(
            {
                "name": endpoint.get("name", ""),
                "name_ja": endpoint.get("name_ja", ""),
                "name_en": endpoint.get("name_en", ""),
                "path": endpoint.get("path", ""),
                "description": endpoint.get("description", ""),
            }
        )

    return {"count": len(results), "results": results}
