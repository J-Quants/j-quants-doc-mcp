"""Describe tool for J-Quants API documentation."""

import logging
from typing import Any

from ..exceptions import format_network_error_with_links, format_not_found_error_with_links
from ..loaders.markdown_loader import (
    get_external_links,
    load_endpoint_detail,
    load_v1_endpoint_detail,
)

logger = logging.getLogger(__name__)


def describe_endpoint(
    endpoint_name: str, api_version: str = "v2"
) -> dict[str, Any] | None:
    """指定されたエンドポイントの詳細情報を取得する。

    Args:
        endpoint_name: エンドポイント名
        api_version: APIバージョン("v1" or "v2")

    Returns:
        エンドポイントの詳細Markdownを含む辞書、またはNone(見つからない場合)
    """
    logger.info(
        f"describe_endpoint called with endpoint_name='{endpoint_name}', "
        f"api_version='{api_version}'"
    )

    if api_version == "v1":
        return _describe_v1(endpoint_name)
    return _describe_v2(endpoint_name)


def _describe_v2(endpoint_name: str) -> dict[str, Any] | None:
    try:
        endpoint_detail = load_endpoint_detail(endpoint_name)

        return {
            "content": endpoint_detail["content"],
            "source_url": endpoint_detail["source_url"],
            "endpoint_name": endpoint_detail["endpoint_name"],
            "cached": endpoint_detail["cached"],
            "api_version": "v2",
            "instruction": (
                f"このMarkdownにはエンドポイント '{endpoint_name}' の詳細情報が含まれています。\n"
                "パス、メソッド、パラメータ、レスポンス情報などを"
                "このMarkdownから読み取ってユーザーに提供してください。\n\n"
                "重要な注意事項:\n"
                "- 詳細な情報はsource_urlを参照するようユーザーに促してください。\n"
                "- このエンドポイントがBulk API対応（取得方法: CSV）の場合、"
                "ユーザーが全銘柄データや大量データを求めている際は、Bulk APIの使用を強く推奨してください。"
            ),
        }
    except FileNotFoundError:
        logger.warning(f"Endpoint not found: {endpoint_name}")
        return format_not_found_error_with_links("エンドポイント", endpoint_name)
    except RuntimeError as e:
        logger.error(f"Error in describe_endpoint: {e}")
        return format_network_error_with_links(str(e))


def _describe_v1(endpoint_name: str) -> dict[str, Any] | None:
    external_links = get_external_links()

    try:
        endpoint_detail = load_v1_endpoint_detail(endpoint_name)

        return {
            "content": endpoint_detail["content"],
            "source_url": endpoint_detail["source_url"],
            "endpoint_name": endpoint_detail["endpoint_name"],
            "cached": endpoint_detail["cached"],
            "api_version": "v1",
            "instruction": (
                "【重要】これはV1 API（旧バージョン）の情報です。"
                "V1 APIは閉鎖が予定されているため、V2 APIへの移行を強く推奨してください。\n\n"
                f"このMarkdownにはV1エンドポイント '{endpoint_name}' の詳細情報が含まれています。\n"
                "パス、メソッド、パラメータ、レスポンス情報などを読み取ってユーザーに提供してください。\n\n"
                "回答時の注意事項:\n"
                "- V1の情報を提供した後、必ず「V1 APIは閉鎖予定のため、V2 APIへの移行をお願いします」と伝えてください。\n"
                "- V2への移行方法の詳細は migrate_v1_to_v2 ツールで取得できます。\n"
                f"- V2 API仕様書: {external_links.get('spec_docs', '')}\n"
                f"- 移行ガイド: {external_links.get('migration_v1_v2', '')}\n"
            ),
        }
    except FileNotFoundError:
        logger.warning(f"V1 Endpoint not found: {endpoint_name}")
        return format_not_found_error_with_links("V1エンドポイント", endpoint_name)
    except RuntimeError as e:
        logger.error(f"Error in describe_endpoint (V1): {e}")
        return format_network_error_with_links(str(e))
