"""例外クラスとエラーハンドリングのユーティリティ。"""

from typing import Any


class JQuantsDocMCPError(Exception):
    """J-Quants Doc MCP の基底例外クラス。"""

    def __init__(self, message: str, details: dict[str, Any] | None = None):
        """エラーを初期化。

        Args:
            message: エラーメッセージ
            details: 追加の詳細情報
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """例外を辞書形式に変換。"""
        result = {
            "error": True,
            "error_type": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(JQuantsDocMCPError):
    """入力バリデーションエラー。

    ユーザーが提供した入力が不正な場合に発生します。
    """

    pass


class NotFoundError(JQuantsDocMCPError):
    """リソースが見つからないエラー。

    指定されたエンドポイントやデータが存在しない場合に発生します。
    """

    pass


class InternalError(JQuantsDocMCPError):
    """内部エラー。

    サーバー側の問題により処理が失敗した場合に発生します。
    """

    pass


def format_validation_error(field: str, message: str) -> dict[str, Any]:
    """バリデーションエラーを整形したメッセージを返す。

    Args:
        field: エラーが発生したフィールド名
        message: エラーメッセージ

    Returns:
        エラー情報を含む辞書
    """
    return ValidationError(
        message=f"入力パラメータ '{field}' のバリデーションエラー: {message}",
        details={"field": field, "validation_error": message},
    ).to_dict()


def format_not_found_error(
    resource_type: str, identifier: str, suggestion: str | None = None
) -> dict[str, Any]:
    """リソース未検出エラーを整形したメッセージを返す。

    Args:
        resource_type: リソースの種類(例: "エンドポイント", "カテゴリ")
        identifier: リソースの識別子
        suggestion: オプションの提案メッセージ

    Returns:
        エラー情報を含む辞書
    """
    message = f"{resource_type} '{identifier}' が見つかりませんでした。"
    if suggestion:
        message += f" {suggestion}"

    return NotFoundError(
        message=message,
        details={
            "resource_type": resource_type,
            "identifier": identifier,
            "suggestion": suggestion,
        },
    ).to_dict()


def format_internal_error(operation: str, original_error: Exception) -> dict[str, Any]:
    """内部エラーを整形したメッセージを返す。

    Args:
        operation: 実行していた操作
        original_error: 元の例外

    Returns:
        エラー情報を含む辞書
    """
    return InternalError(
        message=f"{operation} 中に内部エラーが発生しました。",
        details={
            "operation": operation,
            "original_error": str(original_error),
            "error_class": original_error.__class__.__name__,
        },
    ).to_dict()
