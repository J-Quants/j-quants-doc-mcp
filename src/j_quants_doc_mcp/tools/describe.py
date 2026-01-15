"""Describe tool for J-Quants API documentation."""

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


def describe_endpoint(endpoint_name: str) -> dict[str, Any] | None:
    """指定されたエンドポイントの詳細情報を取得する。

    Args:
        endpoint_name: エンドポイント名(例: eq-master, eq-bars-daily等)

    Returns:
        エンドポイントの詳細情報を含む辞書、またはNone(見つからない場合)
    """
    logger.info(f"describe_endpoint called with endpoint_name='{endpoint_name}'")

    data = _load_endpoints()

    # エンドポイントを検索
    for endpoint in data.get("endpoints", []):
        if endpoint.get("name") == endpoint_name:
            # パラメータを必須/任意で分類
            required_params = []
            optional_params = []
            for param in endpoint.get("parameters", []):
                param_info = {
                    "name": param.get("name"),
                    "type": param.get("type"),
                    "description": param.get("description"),
                    "location": param.get("location"),
                }
                if param.get("required"):
                    required_params.append(param_info)
                else:
                    optional_params.append(param_info)

            # レスポンス情報の構築
            response = endpoint.get("response", {})
            response_summary = {
                "description": response.get("description", ""),
                "fields": [
                    {
                        "name": field.get("name"),
                        "type": field.get("type"),
                        "description": field.get("description"),
                    }
                    for field in response.get("fields", [])
                ],
            }

            # データ更新情報の構築
            data_update = endpoint["data_update"]
            data_update_info = {
                "frequency": data_update["frequency"],
                "time": data_update["time"],
            }
            if data_update.get("notes"):
                data_update_info["notes"] = data_update["notes"]

            result = {
                "name": endpoint["name"],
                "name_ja": endpoint["name_ja"],
                "name_en": endpoint["name_en"],
                "path": endpoint["path"],
                "method": endpoint["method"],
                "description": endpoint["description"],
                "api_available": endpoint.get("api_available", True),
                "bulk_available": endpoint.get("bulk_available", False),
                "parameters": {
                    "required": required_params,
                    "optional": optional_params,
                },
                "response": response_summary,
                "auth_required": endpoint.get("auth_required", True),
                "plan": endpoint["plan"],
                "data_update": data_update_info,
                "valid_request_patterns": endpoint.get(
                    "valid_request_patterns", []
                ),
            }

            # 旧パスが定義されている場合のみ含める
            if endpoint.get("path_old"):
                result["path_old"] = endpoint["path_old"]

            # response_data_key が定義されている場合のみ含める
            if "response_data_key" in endpoint:
                result["response_data_key"] = endpoint["response_data_key"]

            # ページネーション情報が存在する場合のみ追加（オプション）
            pagination = endpoint.get("pagination")
            if pagination:
                result["pagination"] = pagination

            return result

    # エンドポイントが見つからない場合
    return None
