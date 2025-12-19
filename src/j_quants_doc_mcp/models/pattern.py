"""Pydantic models for usage pattern definitions."""

from pydantic import BaseModel, Field


class UsagePattern(BaseModel):
    """利用パターンのモデル"""

    pattern_name: str = Field(..., description="パターン名")
    description: str = Field(..., description="パターンの説明")
    related_endpoints: list[str] = Field(
        default_factory=list, description="関連するエンドポイントのリスト"
    )
    notes: list[str] = Field(default_factory=list, description="注意点や補足事項")
    sample_code_path: str | None = Field(
        None, description="サンプルコードファイルへのパス(templates配下からの相対パス)"
    )


class PatternCollection(BaseModel):
    """パターンコレクションのモデル"""

    patterns: list[UsagePattern] = Field(
        default_factory=list, description="利用パターンのリスト"
    )
