"""General inquiry tool for J-Quants API (non-technical questions)."""

import logging
from typing import Any

from ..loaders.markdown_loader import get_external_links

logger = logging.getLogger(__name__)


def get_info(query: str | None = None) -> dict[str, Any]:
    """API仕様書の範囲外の問い合わせに対し、公式ページへのリンクを案内する。

    Args:
        query: ユーザーの質問内容（ログ・instructionへの反映用）

    Returns:
        公式ページへの案内とLLM向けinstructionを含む辞書
    """
    logger.info(f"get_info called with query='{query}'")

    external_links = get_external_links()

    instruction = (
        "【重要】プラン・契約・料金・データ提供範囲・アカウントに関する情報は、"
        "正確性を保証するためにこのツールでは直接回答しません。\n\n"
        "ユーザーには以下のように案内してください：\n"
        "- プランごとの料金、データ提供範囲、契約内容については公式ページを参照してください。\n"
        "- 具体的な契約・支払い・アカウントに関する問い合わせはヘルプページからお問い合わせください。\n\n"
        "絶対に独自の推測や古い情報でプラン内容を回答しないでください。"
    )

    return {
        "error": False,
        "external_links": external_links,
        "query": query,
        "instruction": instruction,
    }
