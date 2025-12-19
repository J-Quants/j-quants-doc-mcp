"""MCP Server implementation for J-Quants documentation."""

import json
import logging
from typing import Any

from mcp.server.fastmcp import FastMCP
from pydantic import ValidationError as PydanticValidationError

from .exceptions import (
    format_internal_error,
    format_not_found_error,
    format_validation_error,
)
from .resources.specifications import (
    load_endpoints,
    load_patterns,
    load_sample_code,
)
from .schemas import (
    AnswerQuestionInput,
    DescribeEndpointInput,
    GenerateSampleCodeInput,
    LookupPropertyInput,
    SearchEndpointsInput,
)
from .tools.codegen import generate_sample_code as generate_sample_code_impl
from .tools.describe import describe_endpoint as describe_endpoint_impl
from .tools.lookup import lookup_property as lookup_property_impl
from .tools.qa import answer_question as answer_question_impl
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

    try:
        # 入力バリデーション
        validated_input = SearchEndpointsInput(keyword=keyword, category=category)
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        return search_endpoints_impl(validated_input.keyword, validated_input.category)
    except Exception as e:
        logger.error(f"Error in search_endpoints: {e}")
        return format_internal_error("エンドポイント検索", e)


@mcp.tool()
def describe_endpoint(endpoint_name: str) -> dict[str, Any]:
    """指定されたエンドポイントの詳細情報を取得する。

    Args:
        endpoint_name: エンドポイント名(例: eq-master, eq-bars-daily等)

    Returns:
        エンドポイントの詳細情報を含む辞書(名前、パス、メソッド、パラメータ、レスポンス、認証要否、利用可能プラン)
    """
    logger.info(f"describe_endpoint called with endpoint_name='{endpoint_name}'")

    try:
        # 入力バリデーション
        validated_input = DescribeEndpointInput(endpoint_name=endpoint_name)
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        result = describe_endpoint_impl(validated_input.endpoint_name)
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
def generate_sample_code(
    endpoint_name: str, language: str = "python", params: dict[str, Any] | None = None
) -> dict[str, Any] | str:
    """指定されたエンドポイントの実行可能なサンプルコードを生成する。

    Args:
        endpoint_name: エンドポイント名(例: eq-master, eq-bars-daily)
        language: 生成する言語(現在は"python"のみ対応、デフォルト: "python")
        params: 追加パラメータ(将来の拡張用、現在は未使用)

    Returns:
        生成されたサンプルコード(実行可能なPythonコード)、またはエラー辞書
    """
    logger.info(
        f"generate_sample_code called with endpoint_name='{endpoint_name}', language='{language}'"
    )

    try:
        # 入力バリデーション
        validated_input = GenerateSampleCodeInput(
            endpoint_name=endpoint_name, language=language, params=params
        )
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        result = generate_sample_code_impl(
            validated_input.endpoint_name,
            validated_input.language,
            validated_input.params,
        )
        if result is None:
            return format_not_found_error(
                resource_type="エンドポイント",
                identifier=validated_input.endpoint_name,
                suggestion="正しいエンドポイント名を指定してください。search_endpoints ツールで検索できます。",
            )
        return result
    except ValueError as e:
        # 言語未サポートエラー
        return format_validation_error("language", str(e))
    except Exception as e:
        logger.error(f"Error in generate_sample_code: {e}")
        return format_internal_error("サンプルコード生成", e)


@mcp.resource("jquants://api_specification")
def get_api_specification() -> str:
    """J-Quants API の全エンドポイント仕様を取得する。

    Returns:
        JSON形式の文字列(全エンドポイントの詳細仕様)
    """
    logger.info("get_api_specification resource accessed")

    try:
        endpoint_collection = load_endpoints()
        return endpoint_collection.model_dump_json(indent=2, exclude_none=True)
    except Exception as e:
        logger.error(f"Failed to load API specification: {e}")
        return json.dumps({"error": str(e)})


@mcp.resource("jquants://common_patterns")
def get_common_patterns() -> str:
    """J-Quants API の共通実装パターンを取得する。

    Returns:
        JSON形式の文字列(認証、ページネーション、レート制限等の実装パターン)
    """
    logger.info("get_common_patterns resource accessed")

    try:
        pattern_collection = load_patterns()

        # パターンをdict化し、sample_code_pathからsample_codeを読み込んで追加
        patterns_data = []
        for pattern in pattern_collection.patterns:
            pattern_dict = pattern.model_dump(exclude_none=True)

            # sample_code_pathがあれば、ファイルから読み込んでsample_codeとして追加
            if pattern.sample_code_path:
                try:
                    sample_code = load_sample_code(pattern.sample_code_path)
                    pattern_dict["sample_code"] = sample_code
                except Exception as e:
                    logger.warning(
                        f"Failed to load sample code for {pattern.pattern_name}: {e}"
                    )

            patterns_data.append(pattern_dict)

        return json.dumps({"patterns": patterns_data}, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Failed to load common patterns: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def answer_question(question: str) -> dict[str, Any]:
    """自然言語の質問に対してベストプラクティスや注意事項を回答する。

    J-Quants API の使用方法、認証、レート制限、ページネーション、圧縮、
    エラーハンドリングなどに関する質問に回答します。

    Args:
        question: ユーザーからの質問(例: '認証方法は?', 'レート制限について教えて')

    Returns:
        回答情報を含む辞書:
        - matched: マッチしたFAQがあるかどうか
        - count: マッチした回答数
        - answers: マッチした回答のリスト(最大3件)
            - category: カテゴリ(認証、レート制限、ページネーション等)
            - question: FAQ質問文
            - answer: 回答テキスト
            - related_endpoints: 関連するエンドポイント名のリスト
            - matched_keywords: マッチしたキーワード(ある場合)
        - suggestion: マッチしない場合の提案メッセージ
        - available_categories: 利用可能なカテゴリのリスト
    """
    logger.info(f"answer_question called with question='{question}'")

    try:
        # 入力バリデーション
        validated_input = AnswerQuestionInput(question=question)
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        return answer_question_impl(validated_input.question)
    except Exception as e:
        logger.error(f"Error in answer_question: {e}")
        return format_internal_error("質問への回答", e)


@mcp.tool()
def lookup_property(
    property_name: str, endpoint_name: str | None = None
) -> dict[str, Any]:
    """指定されたプロパティ名に関連する参照データを検索する。

    リクエスト/レスポンスで使用されるプロパティ名から、そのプロパティに
    紐づく有効な値の一覧（参照データ）を取得します。

    Args:
        property_name: プロパティ名(例: Mkt, S17, ProdCat, HolDiv等)
        endpoint_name: エンドポイント名(例: eq-master)。指定した場合、
                       そのエンドポイント内にプロパティが存在するかも検証する。

    Returns:
        検索結果を含む辞書:
        - found: 該当する参照データが見つかったかどうか
        - property_name: 検索したプロパティ名
        - endpoint_name: 指定されたエンドポイント名（指定された場合のみ）
        - property_exists: プロパティがエンドポイントに存在するかどうか
        - reference_data: 見つかった場合の参照データ情報
            - name: 参照データ名
            - description: 説明
            - endpoint: 関連エンドポイント
            - direction: request または response
            - fields: フィールド定義
            - values: 有効な値の一覧
        - message: 説明メッセージ
            - 参照データが見つかった場合: 参照データ情報
            - 参照データが見つからないがプロパティは存在: 自由に値を設定できる旨
            - プロパティが存在しない: 存在しないパラメータである旨
    """
    logger.info(
        f"lookup_property called with property_name='{property_name}', "
        f"endpoint_name='{endpoint_name}'"
    )

    try:
        # 入力バリデーション
        validated_input = LookupPropertyInput(
            property_name=property_name, endpoint_name=endpoint_name
        )
    except PydanticValidationError as e:
        error_details = e.errors()[0]
        field = error_details.get("loc", ["unknown"])[0]
        msg = error_details.get("msg", "バリデーションエラー")
        return format_validation_error(str(field), msg)

    try:
        return lookup_property_impl(
            validated_input.property_name, validated_input.endpoint_name
        )
    except Exception as e:
        logger.error(f"Error in lookup_property: {e}")
        return format_internal_error("プロパティ参照データ検索", e)


def run_server() -> None:
    """MCPサーバを起動する。"""
    logger.info("Starting J-Quants Documentation MCP Server...")
    mcp.run()


if __name__ == "__main__":
    run_server()
