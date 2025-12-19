"""Pydantic schemas for tool input validation."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


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
        description="エンドポイント名(例: eq-master, eq-bars-daily等)",
    )

    @field_validator("endpoint_name")
    @classmethod
    def endpoint_name_must_not_be_whitespace(cls, v: str) -> str:
        """エンドポイント名が空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("エンドポイント名は空白のみにはできません")
        return v.strip()


class GenerateSampleCodeInput(BaseModel):
    """generate_sample_code ツールの入力スキーマ。"""

    endpoint_name: str = Field(
        ...,
        min_length=1,
        description="エンドポイント名(例: eq-master, eq-bars-daily)",
    )
    language: str = Field(
        default="python",
        description="生成する言語(現在は'python'のみ対応)",
    )
    params: dict[str, Any] | None = Field(
        None,
        description="追加パラメータ(将来の拡張用、現在は未使用)",
    )

    @field_validator("endpoint_name")
    @classmethod
    def endpoint_name_must_not_be_whitespace(cls, v: str) -> str:
        """エンドポイント名が空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("エンドポイント名は空白のみにはできません")
        return v.strip()

    @field_validator("language")
    @classmethod
    def language_must_be_supported(cls, v: str) -> str:
        """サポートされている言語であることを検証。"""
        supported = ["python"]
        v_lower = v.lower().strip()
        if v_lower not in supported:
            raise ValueError(
                f"言語 '{v}' はサポートされていません。"
                f"現在は {', '.join(supported)} のみ対応しています。"
            )
        return v_lower


class AnswerQuestionInput(BaseModel):
    """answer_question ツールの入力スキーマ。"""

    question: str = Field(
        ...,
        min_length=1,
        description="ユーザーからの質問(例: '認証方法は?', 'レート制限について教えて')",
    )

    @field_validator("question")
    @classmethod
    def question_must_not_be_whitespace(cls, v: str) -> str:
        """質問が空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("質問は空白のみにはできません")
        return v.strip()


class LookupPropertyInput(BaseModel):
    """lookup_property ツールの入力スキーマ。"""

    property_name: str = Field(
        ...,
        min_length=1,
        description="プロパティ名(例: Mkt, S17, ProdCat, HolDiv等)",
    )
    endpoint_name: str | None = Field(
        None,
        description="エンドポイント名(例: eq-master)。指定した場合、そのエンドポイント内にプロパティが存在するかも検証する。",
    )

    @field_validator("property_name")
    @classmethod
    def property_name_must_not_be_whitespace(cls, v: str) -> str:
        """プロパティ名が空白のみでないことを検証。"""
        if not v.strip():
            raise ValueError("プロパティ名は空白のみにはできません")
        return v.strip()

    @field_validator("endpoint_name")
    @classmethod
    def endpoint_name_must_not_be_whitespace(cls, v: str | None) -> str | None:
        """エンドポイント名が指定されている場合、空白のみでないことを検証。"""
        if v is not None and not v.strip():
            raise ValueError("エンドポイント名は空白のみにはできません")
        return v.strip() if v else None
