"""例外クラスとエラーハンドリングのユーティリティ。"""

from typing import Any


def _get_external_links_for_error(language: str | None = None) -> dict[str, str]:
    """エラーレスポンス用の外部リンクを取得（循環importを避けるため遅延import）。
    
    Args:
        language: 言語コード
        
    Returns:
        外部リンクの辞書
    """
    from .loaders.markdown_loader import get_external_links
    
    return get_external_links(language)


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


def format_error_with_external_links(
    error_type: str,
    message: str,
    custom_instruction: str | None = None,
    language: str | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """外部リンク付きエラーレスポンスを生成する。

    Args:
        error_type: エラータイプ（例: "NotFoundError", "RuntimeError"）
        message: エラーメッセージ
        custom_instruction: カスタム指示（Noneの場合はデフォルトの指示を使用）
        language: 言語コード
        **kwargs: エラーレスポンスに追加する任意のフィールド

    Returns:
        外部リンクとLLM向け指示を含むエラーレスポンス
    """
    external_links = _get_external_links_for_error(language)

    default_instruction = (
        "以下の公式ドキュメントを参照するようユーザーに案内してください：\n"
        f"- API仕様書: {external_links.get('spec_docs', '')}\n"
        f"- ヘルプページ: {external_links.get('help', '')}"
    )

    response = {
        "error": True,
        "error_type": error_type,
        "message": message,
        "external_links": external_links,
        "instruction": custom_instruction or default_instruction,
    }

    # 追加のフィールドをマージ
    response.update(kwargs)

    return response


def format_network_error_with_links(
    message: str, language: str | None = None
) -> dict[str, Any]:
    """ネットワークエラー用の外部リンク付きレスポンスを生成する。

    Args:
        message: エラーメッセージ
        language: 言語コード

    Returns:
        外部リンク付きエラーレスポンス
    """
    external_links = _get_external_links_for_error(language)

    return format_error_with_external_links(
        error_type="NetworkError",
        message=message,
        custom_instruction=(
            "エラーが発生しました。上記のメッセージをユーザーに伝えてください。\n"
            f"また、以下の公式ドキュメントも参照するよう案内してください：\n"
            f"- API仕様書: {external_links.get('spec_docs', '')}\n"
            f"- ヘルプページ: {external_links.get('help', '')}"
        ),
        language=language,
    )


def format_not_found_error_with_links(
    resource_type: str,
    identifier: str,
    language: str | None = None,
) -> dict[str, Any]:
    """リソース未検出エラー用の外部リンク付きレスポンスを生成する。

    Args:
        resource_type: リソースの種類
        identifier: リソースの識別子
        language: 言語コード

    Returns:
        外部リンク付きエラーレスポンス
    """
    external_links = _get_external_links_for_error(language)
    message = f"{resource_type} '{identifier}' が見つかりませんでした。"

    return format_error_with_external_links(
        error_type="NotFoundError",
        message=message,
        custom_instruction=(
            "指定されたリソースが見つかりませんでした。\n"
            "以下の公式ドキュメントを参照するようユーザーに案内してください：\n"
            f"- API仕様書: {external_links.get('spec_docs', '')}\n"
            f"- ヘルプページ: {external_links.get('help', '')}"
        ),
        language=language,
        resource_type=resource_type,
        identifier=identifier,
    )
