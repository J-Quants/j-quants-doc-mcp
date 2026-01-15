"""Pydantic models for endpoint definitions."""

from pydantic import BaseModel, Field


class Parameter(BaseModel):
    """APIパラメータのモデル"""

    name: str = Field(..., description="パラメータ名")
    type: str = Field(..., description="パラメータの型 (String, Integer, etc.)")
    required: bool = Field(..., description="必須かどうか")
    description: str = Field(..., description="パラメータの説明")
    location: str = Field(..., description="パラメータの位置 (query, body, header)")


class DataUpdate(BaseModel):
    """データ更新情報のモデル"""

    frequency: str = Field(..., description="更新頻度 (日次, 週次, 不定期等)")
    time: str = Field(..., description="更新時刻")
    notes: str | None = Field(default=None, description="更新に関する補足情報")


class ValidRequestPattern(BaseModel):
    """有効なリクエストパターンのモデル"""

    params: list[str] = Field(default_factory=list, description="パラメータの組み合わせ")
    description: str = Field(..., description="パターンの説明")


class Pagination(BaseModel):
    """ページネーション情報のモデル"""

    supported: bool = Field(..., description="ページネーションがサポートされているか")
    param: str = Field(..., description="ページネーションに使用するパラメータ名")


class ResponseField(BaseModel):
    """レスポンスフィールドのモデル"""

    name: str = Field(..., description="フィールド名")
    type: str = Field(..., description="フィールドの型")
    description: str = Field(..., description="フィールドの説明")


class ResponseSummary(BaseModel):
    """レスポンス要旨のモデル"""

    description: str = Field(..., description="レスポンスの概要説明")
    fields: list[ResponseField] = Field(
        default_factory=list, description="主要なレスポンスフィールド"
    )


class Endpoint(BaseModel):
    """エンドポイント定義のモデル"""

    name: str = Field(..., description="エンドポイントの内部識別子")
    name_ja: str = Field(..., description="エンドポイントの日本語名")
    name_en: str = Field(..., description="エンドポイントの英語名")
    path: str = Field(..., description="エンドポイントのパス")
    path_old: str | None = Field(
        default=None, description="旧エンドポイントのパス（移行情報用）"
    )
    method: str = Field(..., description="HTTPメソッド (GET, POST, etc.)")
    description: str = Field(..., description="エンドポイントの説明")
    bulk_available: bool = Field(..., description="Bulk APIでデータ取得が可能かどうか")
    parameters: list[Parameter] = Field(
        default_factory=list, description="パラメータリスト"
    )
    response: ResponseSummary = Field(..., description="レスポンス要旨")
    auth_required: bool = Field(default=True, description="認証が必要かどうか")
    response_data_key: str | None = Field(
        default=None, description="レスポンスデータのキー"
    )
    plan: list[str] = Field(..., description="利用可能なプランのリスト")
    data_update: DataUpdate = Field(..., description="データ更新情報")
    valid_request_patterns: list[ValidRequestPattern] = Field(
        default_factory=list, description="有効なリクエストパターンのリスト"
    )
    pagination: Pagination | None = Field(
        default=None, description="ページネーション情報"
    )


class EndpointCollection(BaseModel):
    """エンドポイントコレクションのモデル"""

    endpoints: list[Endpoint] = Field(
        default_factory=list, description="エンドポイントのリスト"
    )
