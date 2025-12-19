"""エラーハンドリングの統合テスト。"""

from j_quants_doc_mcp.exceptions import (
    InternalError,
    NotFoundError,
    ValidationError,
    format_internal_error,
    format_not_found_error,
    format_validation_error,
)


class TestExceptionClasses:
    """例外クラスのテスト。"""

    def test_validation_error_basic(self):
        """ValidationError の基本動作。"""
        error = ValidationError("入力が不正です")
        assert error.message == "入力が不正です"
        assert error.details == {}

    def test_validation_error_with_details(self):
        """詳細情報付きの ValidationError。"""
        details = {"field": "keyword", "value": ""}
        error = ValidationError("入力が不正です", details)
        assert error.message == "入力が不正です"
        assert error.details == details

    def test_validation_error_to_dict(self):
        """ValidationError の辞書変換。"""
        error = ValidationError("入力が不正です", {"field": "keyword"})
        result = error.to_dict()

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert result["message"] == "入力が不正です"
        assert result["details"]["field"] == "keyword"

    def test_not_found_error(self):
        """NotFoundError の基本動作。"""
        error = NotFoundError("リソースが見つかりません")
        assert error.message == "リソースが見つかりません"

        result = error.to_dict()
        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"

    def test_internal_error(self):
        """InternalError の基本動作。"""
        error = InternalError("内部エラーが発生しました")
        assert error.message == "内部エラーが発生しました"

        result = error.to_dict()
        assert result["error"] is True
        assert result["error_type"] == "InternalError"


class TestErrorFormatters:
    """エラーフォーマット関数のテスト。"""

    def test_format_validation_error(self):
        """バリデーションエラーのフォーマット。"""
        result = format_validation_error("keyword", "キーワードは必須です")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "keyword" in result["message"]
        assert "キーワードは必須です" in result["message"]
        assert result["details"]["field"] == "keyword"
        assert result["details"]["validation_error"] == "キーワードは必須です"

    def test_format_not_found_error_basic(self):
        """リソース未検出エラーの基本フォーマット。"""
        result = format_not_found_error("エンドポイント", "invalid_endpoint")

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "invalid_endpoint" in result["message"]
        assert "見つかりませんでした" in result["message"]
        assert result["details"]["resource_type"] == "エンドポイント"
        assert result["details"]["identifier"] == "invalid_endpoint"

    def test_format_not_found_error_with_suggestion(self):
        """提案メッセージ付きリソース未検出エラー。"""
        result = format_not_found_error(
            "エンドポイント",
            "invalid_endpoint",
            "search_endpoints ツールで検索できます。",
        )

        assert result["error"] is True
        assert "search_endpoints" in result["message"]
        assert (
            result["details"]["suggestion"] == "search_endpoints ツールで検索できます。"
        )

    def test_format_internal_error(self):
        """内部エラーのフォーマット。"""
        original_error = ValueError("予期しないエラー")
        result = format_internal_error("エンドポイント検索", original_error)

        assert result["error"] is True
        assert result["error_type"] == "InternalError"
        assert "内部エラー" in result["message"]
        assert "エンドポイント検索" in result["message"]
        assert result["details"]["operation"] == "エンドポイント検索"
        assert result["details"]["original_error"] == "予期しないエラー"
        assert result["details"]["error_class"] == "ValueError"


class TestErrorMessages:
    """エラーメッセージの品質テスト。"""

    def test_validation_error_message_is_user_friendly(self):
        """バリデーションエラーメッセージがユーザーフレンドリーであることを確認。"""
        result = format_validation_error("keyword", "空白のみにはできません")

        # ユーザーが原因を理解できるメッセージであることを確認
        assert "keyword" in result["message"]
        assert "空白のみにはできません" in result["message"]
        assert "バリデーションエラー" in result["message"]

    def test_not_found_error_message_includes_suggestion(self):
        """未検出エラーメッセージに提案が含まれることを確認。"""
        result = format_not_found_error(
            "エンドポイント",
            "unknown_endpoint",
            "正しいエンドポイント名を指定してください。",
        )

        # 次のアクションを示す提案が含まれることを確認
        assert "正しいエンドポイント名を指定してください。" in result["message"]

    def test_internal_error_message_is_clear(self):
        """内部エラーメッセージが明確であることを確認。"""
        original_error = Exception("DB connection failed")
        result = format_internal_error("データベース接続", original_error)

        # 何が起こったかが明確であることを確認
        assert "内部エラー" in result["message"]
        assert "データベース接続" in result["message"]
        assert result["details"]["original_error"] == "DB connection failed"
