"""Fetch tool for J-Quants specification pages."""

import logging
from typing import Any

from ..exceptions import format_network_error_with_links, format_not_found_error_with_links
from ..loaders.markdown_loader import load_spec_page

logger = logging.getLogger(__name__)


def fetch_spec_page(path: str) -> dict[str, Any]:
    """指定されたパスのSpecificationページを取得する。

    Args:
        path: Specificationページのパス（例: /spec/mkt-cal/holiday-division）

    Returns:
        SpecificationページのMarkdownを含む辞書、またはエラー辞書
    """
    logger.info(f"fetch_spec_page called with path='{path}'")

    try:
        # Specificationページを取得
        spec_page = load_spec_page(path)

        return {
            "content": spec_page["content"],
            "source_url": spec_page["source_url"],
            "path": spec_page["path"],
            "cached": spec_page["cached"],
            "instruction": (
                f"このMarkdownにはパス '{path}' のSpecification情報が含まれています。\n"
                "このMarkdownから必要な情報を読み取ってユーザーに提供してください。\n\n"
                "重要な注意事項:\n"
                "- エンドポイント一覧ページの場合、取得方法欄に「CSV」と記載されているエンドポイントは"
                "Bulk APIで全銘柄データを一括取得できます。\n"
                "- ユーザーが全銘柄データや大量データを求めている場合は、Bulk APIの使用を強く推奨してください。"
            ),
        }
    except FileNotFoundError:
        # ページが見つからない場合
        logger.warning(f"Spec page not found: {path}")
        return format_not_found_error_with_links("Specificationページ", path)
    except RuntimeError as e:
        # その他のエラー（ネットワークエラーなど）
        logger.error(f"Error in fetch_spec_page: {e}")
        return format_network_error_with_links(str(e))
