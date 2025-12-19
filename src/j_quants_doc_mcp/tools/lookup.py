"""Lookup tool for J-Quants API reference data."""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

REFERENCE_DATA_PATH = Path(__file__).parent.parent / "data" / "reference_data.json"
ENDPOINTS_DATA_PATH = Path(__file__).parent.parent / "data" / "endpoints.json"


def _load_reference_data() -> dict[str, Any]:
    """参照データをロード"""
    with open(REFERENCE_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _load_endpoints() -> dict[str, Any]:
    """エンドポイントデータをロード"""
    with open(ENDPOINTS_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _check_property_exists_in_endpoint(
    property_name: str, endpoint_name: str | None
) -> tuple[bool, str | None]:
    """エンドポイント内にプロパティが存在するか確認する。

    Args:
        property_name: プロパティ名
        endpoint_name: エンドポイント名（Noneの場合は全エンドポイントを検索）

    Returns:
        (存在するかどうか, 見つかったエンドポイント名またはNone)
    """
    endpoints_data = _load_endpoints()

    for endpoint in endpoints_data.get("endpoints", []):
        # endpoint_nameが指定されている場合は、そのエンドポイントのみチェック
        if endpoint_name and endpoint.get("name") != endpoint_name:
            continue

        # パラメータをチェック
        for param in endpoint.get("parameters", []):
            if param.get("name", "").lower() == property_name.lower():
                return True, endpoint.get("name")

        # レスポンスフィールドをチェック
        response = endpoint.get("response", {})
        for field in response.get("fields", []):
            if field.get("name", "").lower() == property_name.lower():
                return True, endpoint.get("name")

    return False, None


def lookup_property(
    property_name: str, endpoint_name: str | None = None
) -> dict[str, Any]:
    """指定されたプロパティ名に関連する参照データを検索する。

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
        - message: 説明メッセージ
    """
    logger.info(
        f"lookup_property called with property_name='{property_name}', "
        f"endpoint_name='{endpoint_name}'"
    )

    # エンドポイント内にプロパティが存在するか確認
    property_exists, found_in_endpoint = _check_property_exists_in_endpoint(
        property_name, endpoint_name
    )

    # プロパティがエンドポイントに存在しない場合
    if not property_exists:
        result: dict[str, Any] = {
            "found": False,
            "property_name": property_name,
            "property_exists": False,
            "reference_data": None,
            "message": (
                f"プロパティ '{property_name}' は"
                + (f"エンドポイント '{endpoint_name}' に" if endpoint_name else "")
                + "存在しないパラメータです。"
            ),
        }
        if endpoint_name:
            result["endpoint_name"] = endpoint_name
        return result

    # 参照データを検索
    data = _load_reference_data()
    matched_entry = None

    # 各参照データのrelated_propertiesを検索
    for ref_entry in data.get("reference_data", []):
        for related_prop in ref_entry.get("related_properties", []):
            # プロパティ名が一致するか確認（大文字小文字を区別しない）
            if related_prop.get("property", "").lower() == property_name.lower():
                # endpoint_nameが指定されている場合は、エンドポイントも一致するかチェック
                if endpoint_name and related_prop.get("endpoint") != endpoint_name:
                    continue

                matched_entry = {
                    "name": ref_entry.get("name"),
                    "description": ref_entry.get("description"),
                    "endpoint": related_prop.get("endpoint"),
                    "direction": related_prop.get("direction"),
                    "fields": ref_entry.get("fields", []),
                    "values": ref_entry.get("reference_data", []),
                }
                break
        if matched_entry:
            break

    if matched_entry:
        result = {
            "found": True,
            "property_name": property_name,
            "property_exists": True,
            "reference_data": matched_entry,
            "message": f"プロパティ '{property_name}' に関連する参照データが見つかりました。",
        }
        if endpoint_name:
            result["endpoint_name"] = endpoint_name
        return result
    else:
        result = {
            "found": False,
            "property_name": property_name,
            "property_exists": True,
            "reference_data": None,
            "message": (
                f"プロパティ '{property_name}' に関連する参照データは登録されていません。"
                "このプロパティは特定の値セットに紐づかないため、自由に値を格納できます。"
            ),
        }
        if endpoint_name:
            result["endpoint_name"] = endpoint_name
        return result
