"""Validate endpoints.json against Pydantic models."""

import json
from pathlib import Path

from .models.endpoint import EndpointCollection


def validate_endpoints() -> EndpointCollection:
    """endpoints.jsonをPydanticモデルで検証する"""
    # JSONファイルのパスを取得
    data_dir = Path(__file__).parent / "data"
    endpoints_file = data_dir / "endpoints.json"

    # JSONファイルを読み込み
    with open(endpoints_file, encoding="utf-8") as f:
        data = json.load(f)

    # Pydanticモデルで検証
    try:
        endpoint_collection = EndpointCollection(**data)
        print("✓ 検証成功！")
        print(
            f"✓ {len(endpoint_collection.endpoints)}個のエンドポイントが定義されています:\n"
        )

        for endpoint in endpoint_collection.endpoints:
            # 日本語名・英語名があれば表示
            name_display = endpoint.name
            if endpoint.name_ja:
                name_display += f" ({endpoint.name_ja})"
            if endpoint.name_en:
                name_display += f" [{endpoint.name_en}]"

            print(f"  - {name_display}")
            print(f"    {endpoint.method} {endpoint.path}")
            print(
                f"    必須パラメータ: {sum(1 for p in endpoint.parameters if p.required)}個"
            )
            print(f"    レスポンスフィールド: {len(endpoint.response.fields)}個")
            print()

        return endpoint_collection

    except Exception as e:
        print(f"✗ 検証失敗: {e}")
        raise


if __name__ == "__main__":
    validate_endpoints()
