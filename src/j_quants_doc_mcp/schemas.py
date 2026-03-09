"""Pydantic schemas for tool input validation."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator

API_VERSION_DESCRIPTION = (
    "APIバージョン。会話の文脈からV1かV2かを判断して指定する。"
    "V1のエンドポイントパス(/v1/...)やV1特有の名前(daily_quotes等)が含まれる場合は'v1'を指定。"
    "デフォルトは'v2'。"
)


class SearchEndpointsInput(BaseModel):
    """search_endpoints ツールの入力スキーマ。"""

    keyword: str = Field(
        ...,
        min_length=1,
        description="検索キーワード(エンドポイント名、パス、説明から検索)",
    )
    category: str | None = Field(
        None,
        description="オプションのカテゴリフィルタ(auth, listed, prices, fins等)",
    )
    api_version: Literal["v1", "v2"] = Field(
        "v2",
        description=API_VERSION_DESCRIPTION,
    )

    @field_validator("keyword")
    @classmethod
    def keyword_must_not_be_whitespace(cls, v: str) -> str:
        """キーワードが空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("キーワードは空白のみにはできません")
        return v.strip()

    @field_validator("category")
    @classmethod
    def category_must_not_be_whitespace(cls, v: str | None) -> str | None:
        """カテゴリが指定されている場合、空白のみでないことを検証。"""
        if v is not None and not v.strip():
            raise ValueError("カテゴリは空白のみにはできません")
        return v.strip() if v else None


class DescribeEndpointInput(BaseModel):
    """describe_endpoint ツールの入力スキーマ。"""

    endpoint_name: str = Field(
        ...,
        min_length=1,
        description="エンドポイント名(V2例: eq-master, eq-bars-daily / V1例: daily_quotes, listed_info等)",
    )
    api_version: Literal["v1", "v2"] = Field(
        "v2",
        description=API_VERSION_DESCRIPTION,
    )

    @field_validator("endpoint_name")
    @classmethod
    def endpoint_name_must_not_be_whitespace(cls, v: str) -> str:
        """エンドポイント名が空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("エンドポイント名は空白のみにはできません")
        return v.strip()


class FetchSpecPageInput(BaseModel):
    """fetch_spec_page ツールの入力スキーマ。"""

    path: str = Field(
        ...,
        min_length=1,
        description="Specificationページのパス(例: /spec/mkt-cal/holiday-division)",
    )

    @field_validator("path")
    @classmethod
    def path_must_not_be_whitespace(cls, v: str) -> str:
        """パスが空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("パスは空白のみにはできません")
        return v.strip()


class MigrateV1ToV2Input(BaseModel):
    """migrate_v1_to_v2 ツールの入力スキーマ。"""

    v1_endpoint: str | None = Field(
        None,
        description="V1 APIのエンドポイントパスまたはキーワード(例: /v1/prices/daily_quotes, 株価四本値等)。指定しない場合は移行ガイド全体を返す。",
    )

    @field_validator("v1_endpoint")
    @classmethod
    def v1_endpoint_must_not_be_whitespace(cls, v: str | None) -> str | None:
        """V1エンドポイントが指定されている場合、空白のみでないことを検証。"""
        if v is not None and not v.strip():
            raise ValueError("V1エンドポイントは空白のみにはできません")
        return v.strip() if v else None
