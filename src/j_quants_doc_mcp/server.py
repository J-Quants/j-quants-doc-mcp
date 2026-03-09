"""MCP Server implementation for J-Quants documentation."""

import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    format_internal_error,
    format_not_found_error,
    format_validation_error,
)
from .resources.specifications import load_patterns, load_sample_code
from .schemas import (
    DescribeEndpointInput,
    FetchSpecPageInput,
    MigrateV1ToV2Input,
    SearchEndpointsInput,
)
from .tools.describe import describe_endpoint as describe_endpoint_impl
from .tools.fetch import fetch_spec_page as fetch_spec_page_impl
from .tools.migrate import migrate_v1_to_v2 as migrate_v1_to_v2_impl
from .tools.info import get_info as get_info_impl
from .tools.search import search_endpoints as search_endpoints_impl

# ロギング設定
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastMCP サーバインスタンスの作成
mcp = FastMCP("j-quants-doc-mcp")


@mcp.tool()
def health_check() -> dict[str, Any]:
    """ヘルスチェック用の簡易Tool。

    サーバが正常に動作しているかを確認するためのツールです。

    Returns:
        サーバの状態を示す辞書
    """
    logger.info("Health check called")
    return {"status": "healthy", "service": "j-quants-doc-mcp", "version": "0.1.0"}


@mcp.tool()
def search_endpoints(
    keyword: str, category: str | None = None, api_version: str = "v2"
) -> dict[str, Any]:
    """エンドポイントをキーワードとカテゴリで検索する。

    Args:
        keyword: 検索キーワード(エンドポイント名、パス、説明から検索)
        category: オプションのカテゴリフィルタ(auth, listed, prices, fins等)
        api_version: APIバージョン。会話の文脈からV1かV2かを判断して指定する。V1のエンドポイントパス(/v1/...)やV1特有の名前(daily_quotes等)が含まれる場合は'v1'を指定。デフォルトは'v2'。

    Returns:
        検索結果を含む辞書(該当件数と結果配列)
    """
    logger.info(
        f"search_endpoints called with keyword='{keyword}', "
        f"category='{category}', api_version='{api_version}'"
    )

    try:
        # 入力バリデーション
        validated_input = SearchEndpointsInput(
            keyword=keyword, category=category, api_version=api_version
        )
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        return search_endpoints_impl(
            validated_input.keyword,
            validated_input.category,
            validated_input.api_version,
        )
    except Exception as e:
        logger.error(f"Error in search_endpoints: {e}")
        return format_internal_error("エンドポイント検索", e)


@mcp.tool()
def describe_endpoint(endpoint_name: str, api_version: str = "v2") -> dict[str, Any]:
    """指定されたエンドポイントの詳細情報を取得する。

    Args:
        endpoint_name: エンドポイント名(V2例: eq-master, eq-bars-daily / V1例: daily_quotes, listed_info等)
        api_version: APIバージョン。会話の文脈からV1かV2かを判断して指定する。V1のエンドポイントパス(/v1/...)やV1特有の名前(daily_quotes等)が含まれる場合は'v1'を指定。デフォルトは'v2'。

    Returns:
        エンドポイントの詳細情報を含む辞書(名前、パス、メソッド、パラメータ、レスポンス、認証要否、利用可能プラン)
    """
    logger.info(
        f"describe_endpoint called with endpoint_name='{endpoint_name}', "
        f"api_version='{api_version}'"
    )

    try:
        # 入力バリデーション
        validated_input = DescribeEndpointInput(
            endpoint_name=endpoint_name, api_version=api_version
        )
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        result = describe_endpoint_impl(
            validated_input.endpoint_name, validated_input.api_version
        )
        if result is None:
            return format_not_found_error(
                resource_type="エンドポイント",
                identifier=validated_input.endpoint_name,
                suggestion="正しいエンドポイント名を指定してください。search_endpoints ツールで検索できます。",
            )
        return result
    except Exception as e:
        logger.error(f"Error in describe_endpoint: {e}")
        return format_internal_error("エンドポイント詳細取得", e)


@mcp.tool()
def get_pattern(pattern_name: str | None = None) -> dict[str, Any]:
    """実装パターン情報を取得する。

    Args:
        pattern_name: パターン名（指定しない場合は全パターンの一覧を返す）

    Returns:
        パターン情報を含む辞書
    """
    logger.info(f"get_pattern called with pattern_name='{pattern_name}'")

    try:
        pattern_collection = load_patterns()

        # パターン名が指定されていない場合は一覧のみ返す
        if pattern_name is None:
            pattern_list = [
                {
                    "pattern_name": p.pattern_name,
                    "description": p.description,
                    "related_endpoints": p.related_endpoints,
                }
                for p in pattern_collection.patterns
            ]
            return {
                "count": len(pattern_list),
                "patterns": pattern_list,
                "hint": "詳細を取得するには pattern_name を指定してください",
            }

        # 指定されたパターンを検索
        for pattern in pattern_collection.patterns:
            if pattern.pattern_name == pattern_name:
                pattern_dict = pattern.model_dump(exclude_none=True)

                # サンプルコードを読み込む
                if pattern.sample_code_path:
                    try:
                        sample_code = load_sample_code(pattern.sample_code_path)
                        pattern_dict["sample_code"] = sample_code
                    except Exception as e:
                        logger.warning(
                            f"Failed to load sample code for {pattern.pattern_name}: {e}"
                        )

                return pattern_dict

        # パターンが見つからない場合
        return format_not_found_error(
            resource_type="パターン",
            identifier=pattern_name,
            suggestion="get_pattern() を引数なしで呼び出して、利用可能なパターン一覧を確認してください。",
        )

    except Exception as e:
        logger.error(f"Error in get_pattern: {e}")
        return format_internal_error("パターン取得", e)


@mcp.tool()
def fetch_spec_page(path: str) -> dict[str, Any]:
    """指定されたパスのSpecificationページを取得する。

    エンドポイント詳細だけでなく、参照データページ（例: 休日区分、市場コード等）も取得できます。
    Markdown内のリンクを辿って追加情報を取得する際に使用してください。

    Args:
        path: Specificationページのパス(例: /spec/mkt-cal/holiday-division)

    Returns:
        Specificationページの情報を含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - path: リクエストされたパス
        - cached: キャッシュから取得したかどうか
        - instruction: LLMへの指示
    """
    logger.info(f"fetch_spec_page called with path='{path}'")

    try:
        # 入力バリデーション
        validated_input = FetchSpecPageInput(path=path)
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        result = fetch_spec_page_impl(validated_input.path)
        # エラーが含まれている場合はそのまま返す
        if result.get("error"):
            return result
        return result
    except Exception as e:
        logger.error(f"Error in fetch_spec_page: {e}")
        return format_internal_error("Specificationページ取得", e)


@mcp.tool()
def migrate_v1_to_v2(v1_endpoint: str | None = None) -> dict[str, Any]:
    """V1 APIからV2 APIへの移行ガイドを提供する。

    V1 APIを利用中のユーザーがV2 APIへ移行する際に、
    エンドポイントの対応関係や変更点を案内し、V2の仕様書ページへ誘導します。

    Args:
        v1_endpoint: V1 APIのエンドポイントパスまたはキーワード(例: /v1/prices/daily_quotes, 株価四本値等)。指定しない場合は移行ガイド全体を返す。

    Returns:
        移行ガイドのMarkdownとV2仕様ページへの誘導情報を含む辞書
    """
    logger.info(f"migrate_v1_to_v2 called with v1_endpoint='{v1_endpoint}'")

    try:
        # 入力バリデーション
        validated_input = MigrateV1ToV2Input(v1_endpoint=v1_endpoint)
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        result = migrate_v1_to_v2_impl(validated_input.v1_endpoint)
        if result.get("error"):
            return result
        return result
    except Exception as e:
        logger.error(f"Error in migrate_v1_to_v2: {e}")
        return format_internal_error("V1→V2移行ガイド取得", e)


@mcp.tool()
def get_info(query: str | None = None) -> dict[str, Any]:
    """API仕様書の範囲外の質問に回答するためのツール。

    以下のような質問を受けた場合に、他のツール(search_endpoints等)ではなくこのツールを使用してください:
    - プランの種類、料金、価格
    - 契約方法、申込方法、支払い方法
    - 各プランで利用可能なデータ範囲・期間
    - プランの変更・アップグレード・解約
    - 無料プランと有料プランの違い
    - データ提供期間・データ格納期間の詳細
    - アカウント・ログインに関する問い合わせ
    - サポート・お問い合わせ先

    このツールは正確な情報源として公式ページへのリンクを提供します。

    Args:
        query: ユーザーの質問内容(例: 「Premiumプランの料金は？」「問い合わせ先は？」等)

    Returns:
        公式ページへの案内リンクとLLM向けの回答指示を含む辞書
    """
    logger.info(f"get_info called with query='{query}'")

    try:
        return get_info_impl(query)
    except Exception as e:
        logger.error(f"Error in get_info: {e}")
        return format_internal_error("情報取得", e)


def run_server() -> None:
    """MCPサーバを起動する。"""
    logger.info("Starting J-Quants Documentation MCP Server...")
    mcp.run()


if __name__ == "__main__":
    run_server()
