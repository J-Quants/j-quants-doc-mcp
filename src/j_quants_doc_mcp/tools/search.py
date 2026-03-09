"""Search tool for J-Quants API documentation."""

import logging
from typing import Any

from ..exceptions import format_network_error_with_links
from ..loaders.markdown_loader import (
    get_external_links,
    load_endpoint_list,
    load_v1_endpoint_list,
)

logger = logging.getLogger(__name__)


def search_endpoints(
    keyword: str, category: str | None = None, api_version: str = "v2"
) -> dict[str, Any]:
    """エンドポイントをキーワードとカテゴリで検索する。

    Args:
        keyword: 検索キーワード(エンドポイント名、パス、説明から検索)
        category: オプションのカテゴリフィルタ(auth, listed, prices, fins等)
        api_version: APIバージョン("v1" or "v2")

    Returns:
        エンドポイント一覧ページのMarkdown全体と検索情報を含む辞書
    """
    logger.info(
        f"search_endpoints called with keyword='{keyword}', "
        f"category='{category}', api_version='{api_version}'"
    )

    try:
        if api_version == "v1":
            return _search_v1(keyword, category)
        return _search_v2(keyword, category)
    except RuntimeError as e:
        logger.error(f"Error in search_endpoints: {e}")
        return format_network_error_with_links(str(e))


def _search_v2(keyword: str, category: str | None) -> dict[str, Any]:
    endpoint_list = load_endpoint_list()
    external_links = get_external_links()

    return {
        "content": endpoint_list["content"],
        "source_url": endpoint_list["source_url"],
        "cached": endpoint_list["cached"],
        "api_version": "v2",
        "search_keyword": keyword,
        "search_category": category,
        "instruction": (
            f"このMarkdownからキーワード '{keyword}' "
            + (f"およびカテゴリ '{category}' " if category else "")
            + "に一致するエンドポイントを探してください。\n\n"
            "重要な注意事項:\n"
            "- 取得方法欄に「CSV」と記載されているエンドポイントは、Bulk APIで全銘柄データを一括取得できます。\n"
            "- ユーザーが「全銘柄データ」「過去データの一括取得」などを求めている場合は、"
            "通常のAPIではなくBulk APIの使用を強く推奨してください。\n"
            "- 該当するエンドポイントが見つからない場合は、以下の公式ドキュメントも参照するようユーザーに案内してください：\n"
            f"  - API仕様書: {external_links.get('spec_docs', '')}\n"
            f"  - ヘルプページ: {external_links.get('help', '')}\n"
        ),
    }


def _search_v1(keyword: str, category: str | None) -> dict[str, Any]:
    endpoint_list = load_v1_endpoint_list()
    external_links = get_external_links()

    return {
        "content": endpoint_list["content"],
        "source_url": endpoint_list["source_url"],
        "cached": endpoint_list["cached"],
        "api_version": "v1",
        "search_keyword": keyword,
        "search_category": category,
        "instruction": (
            "【重要】これはV1 API（旧バージョン）の情報です。"
            "V1 APIは閉鎖が予定されているため、V2 APIへの移行を強く推奨してください。\n\n"
            f"このMarkdownからキーワード '{keyword}' "
            + (f"およびカテゴリ '{category}' " if category else "")
            + "に一致するエンドポイントを探してください。\n\n"
            "回答時の注意事項:\n"
            "- V1の情報を提供した後、必ず「V1 APIは閉鎖予定のため、V2 APIへの移行をお願いします」と伝えてください。\n"
            "- V2への移行方法の詳細は migrate_v1_to_v2 ツールで取得できます。\n"
            f"- V2 API仕様書: {external_links.get('spec_docs', '')}\n"
            f"- 移行ガイド: {external_links.get('migration_v1_v2', '')}\n"
        ),
    }
