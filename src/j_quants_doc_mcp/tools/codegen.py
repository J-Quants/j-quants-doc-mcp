"""Code generation tool for J-Quants API."""

import json
import logging
import re
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# テンプレートディレクトリのパス
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
ENDPOINTS_DATA_PATH = Path(__file__).parent.parent / "data" / "endpoints.json"


def _load_endpoints() -> dict[str, Any]:
    """エンドポイントデータをロード"""
    with open(ENDPOINTS_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _find_endpoint(endpoint_name: str) -> dict[str, Any] | None:
    """エンドポイント名から詳細情報を取得"""
    data = _load_endpoints()
    for endpoint in data.get("endpoints", []):
        if endpoint.get("name") == endpoint_name:
            return endpoint
    return None


def _convert_type_to_python(param_type: str) -> str:
    """パラメータ型をPythonの型アノテーションに変換"""
    type_mapping = {
        "String": "str",
        "Integer": "int",
        "Boolean": "bool",
        "Date": "str",  # ISO形式文字列として扱う
        "Array": "list",
        "Object": "dict",
    }
    return type_mapping.get(param_type, "str")


def _get_example_value(param_type: str, param_name: str) -> str:
    """パラメータの例示値を生成"""
    if (
        "date" in param_name.lower()
        or "from" in param_name.lower()
        or "to" in param_name.lower()
    ):
        return '"20230101"'
    if "code" in param_name.lower():
        return '"27800"'  # 日経平均のコード例
    if param_type == "Integer":
        return "1"
    if param_type == "Boolean":
        return "True"
    return f'"{param_name}_value"'


def _is_api_key_param(param_name: str) -> bool:
    """パラメータがAPIキー(有効期限のある認証情報)かどうかを判定"""
    api_key_keywords = ["apikey", "api-key"]
    param_lower = param_name.lower()
    return any(keyword in param_lower for keyword in api_key_keywords)


def _is_sensitive_param(param_name: str) -> bool:
    """パラメータが機密情報(長期的に保存すべき認証情報)かどうかを判定"""
    # APIキーは除外(APIキーは別途管理)
    if _is_api_key_param(param_name):
        return False

    sensitive_keywords = [
        "password",
        "secret",
        "key",
        "credential",
        "mailaddress",
        "email",
        "mail",
        "token",
        "idtoken",
        "refreshtoken",
    ]
    param_lower = param_name.lower()
    return any(keyword in param_lower for keyword in sensitive_keywords)


def _get_env_var_name(param_name: str) -> str:
    """パラメータ名から環境変数名を生成"""
    # キャメルケースをスネークケースに変換
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", param_name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    return "JQUANTS_" + s2.upper()


def _escape_reserved_keyword(param_name: str) -> str:
    """Pythonの予約語をエスケープする"""
    python_keywords = {
        "from",
        "to",
        "in",
        "is",
        "if",
        "for",
        "while",
        "def",
        "class",
        "return",
        "import",
        "as",
        "with",
        "try",
        "except",
        "raise",
        "pass",
        "break",
        "continue",
        "yield",
        "lambda",
        "global",
        "nonlocal",
        "assert",
    }

    if param_name.lower() in python_keywords:
        return f"{param_name}_"
    return param_name


def generate_sample_code(
    endpoint_name: str, language: str = "python", params: dict[str, Any] | None = None
) -> str | None:
    """指定されたエンドポイントのサンプルコードを生成する。

    Args:
        endpoint_name: エンドポイント名(例: eq-master, eq-bars-daily)
        language: 生成する言語(現在は"python"のみ対応)
        params: 追加パラメータ(将来の拡張用、現在は未使用)

    Returns:
        生成されたサンプルコード、またはNone(エンドポイントが見つからない場合)

    Raises:
        ValueError: サポートされていない言語の場合
    """
    logger.info(
        f"generate_sample_code called: endpoint_name={endpoint_name}, language={language}"
    )

    # 言語チェック
    if language != "python":
        raise ValueError(
            f"言語 '{language}' はサポートされていません。現在は 'python' のみ対応しています。"
        )

    # エンドポイント情報を取得
    endpoint = _find_endpoint(endpoint_name)
    if not endpoint:
        return None

    # パラメータを整理
    required_params = []
    optional_params = []
    query_params = []
    header_params = []
    body_params = []

    for param in endpoint.get("parameters", []):
        param_name = param.get("name")

        # pagination_keyはテンプレート側で別途管理するためスキップ
        if param_name == "pagination_key":
            continue

        is_sensitive = _is_sensitive_param(param_name)
        is_api_key = _is_api_key_param(param_name)

        # Pythonの予約語をエスケープ
        python_param_name = _escape_reserved_keyword(param_name)

        param_info = {
            "name": python_param_name,
            "original_name": param_name,  # API呼び出し時に使用する元の名前
            "type": param.get("type"),
            "python_type": _convert_type_to_python(param.get("type")),
            "description": param.get("description"),
            "location": param.get("location"),
            "required": param.get("required"),
            "example_value": _get_example_value(param.get("type"), param_name),
            "is_sensitive": is_sensitive,
            "is_api_key": is_api_key,
            "env_var_name": _get_env_var_name(param_name) if is_sensitive else None,
        }

        # location別に分類
        location = param.get("location")
        if location == "query":
            query_params.append(param_info)
        elif location == "header":
            header_params.append(param_info)
        elif location == "body":
            body_params.append(param_info)

        # required別に分類
        if param.get("required"):
            required_params.append(param_info)
        else:
            optional_params.append(param_info)

    # 関数名を生成(エンドポイント名をスネークケースとして使用)
    function_name = endpoint_name

    # 機密情報パラメータと非機密情報パラメータを分離
    has_sensitive_params = any(p.get("is_sensitive") for p in required_params)
    non_sensitive_required_params = [
        p for p in required_params if not p.get("is_sensitive")
    ]

    # ページネーション対応の判定
    has_pagination = any(
        p.get("name") == "pagination_key" for p in endpoint.get("parameters", [])
    )

    # レスポンスデータキーの取得
    response_data_key = endpoint.get("response_data_key", "")

    # Jinja2環境の設定
    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
    template = env.get_template("python_httpx.jinja2")

    # テンプレートをレンダリング
    code = template.render(
        endpoint_name=endpoint.get("name"),
        name_ja=endpoint.get("name_ja"),
        name_en=endpoint.get("name_en"),
        description=endpoint.get("description"),
        method=endpoint.get("method"),
        path=endpoint.get("path"),
        auth_required=endpoint.get("auth_required", False),
        function_name=function_name,
        required_params=required_params,
        optional_params=optional_params,
        query_params=query_params,
        header_params=header_params,
        body_params=body_params,
        has_sensitive_params=has_sensitive_params,
        non_sensitive_required_params=non_sensitive_required_params,
        has_pagination=has_pagination,
        response_data_key=response_data_key,
    )

    return code
