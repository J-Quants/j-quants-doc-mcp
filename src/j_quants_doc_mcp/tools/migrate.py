"""Migration guide tool for V1 to V2 API transition."""

import logging
from typing import Any

from ..exceptions import format_network_error_with_links, format_not_found_error_with_links
from ..loaders.markdown_loader import get_external_links, load_spec_page

logger = logging.getLogger(__name__)


def _get_migration_path() -> str:
    """external_linksから移行ガイドページのパスを取得する。"""
    from ..loaders.markdown_loader import _load_config

    config = _load_config()
    external_links = config.get("external_links", {})
    path = external_links.get("migration_v1_v2")
    if not path:
        raise ValueError("external_links に migration_v1_v2 が設定されていません")
    return path


def migrate_v1_to_v2(v1_endpoint: str | None = None) -> dict[str, Any]:
    """V1からV2への移行ガイドを取得し、V2仕様ページへの誘導情報を返す。

    Args:
        v1_endpoint: V1 APIのエンドポイントパスまたはキーワード（省略時は移行ガイド全体を返す）

    Returns:
        移行ガイドのMarkdownとLLM向けinstructionを含む辞書、またはエラー辞書
    """
    logger.info(f"migrate_v1_to_v2 called with v1_endpoint='{v1_endpoint}'")

    migration_path = _get_migration_path()

    try:
        spec_page = load_spec_page(migration_path)
    except FileNotFoundError:
        logger.warning(f"Migration spec page not found: {migration_path}")
        return format_not_found_error_with_links("移行ガイドページ", migration_path)
    except RuntimeError as e:
        logger.error(f"Error fetching migration spec page: {e}")
        return format_network_error_with_links(str(e))

    external_links = get_external_links()

    if v1_endpoint:
        instruction = (
            f"ユーザーはV1 APIのエンドポイント '{v1_endpoint}' からV2 APIへの移行方法を知りたがっています。\n\n"
            "以下のMarkdownにはV1→V2の移行ガイド（エンドポイント対応表を含む）が記載されています。\n"
            "この情報をもとに以下の手順で回答してください：\n\n"
            f"1. Markdownのエンドポイント対応表から '{v1_endpoint}' に該当するV1エンドポイントを特定し、"
            "対応するV2エンドポイントを案内してください。\n"
            "2. V2エンドポイントの詳細な仕様を確認するため、describe_endpoint ツールを使って"
            "V2エンドポイントの仕様書ページを取得し、その内容もあわせてユーザーに提供してください。\n"
            "3. 認証方式の変更（トークン方式→APIキー方式）やレスポンス形式の変更など、"
            "移行時に注意すべき全般的な変更点も伝えてください。\n\n"
            f"移行ガイド全文: {external_links.get('migration_v1_v2', '')}"
        )
    else:
        instruction = (
            "ユーザーはV1 APIからV2 APIへの移行について情報を求めています。\n\n"
            "以下のMarkdownにはV1→V2の移行ガイドが記載されています。\n"
            "この情報をもとに以下のポイントをユーザーに案内してください：\n\n"
            "1. 認証方式の変更（トークン方式→APIキー方式）\n"
            "2. プラン・データ提供範囲の変更\n"
            "3. レートリミットの新設\n"
            "4. エンドポイント・パラメータの変更（V1→V2の対応表）\n"
            "5. レスポンス形式の変更\n\n"
            f"移行ガイド全文: {external_links.get('migration_v1_v2', '')}"
        )

    return {
        "content": spec_page["content"],
        "source_url": spec_page["source_url"],
        "path": spec_page["path"],
        "cached": spec_page["cached"],
        "instruction": instruction,
    }
