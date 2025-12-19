"""ツールの統合テスト(想定外入力のエラーメッセージ確認)。"""

from j_quants_doc_mcp.server import (
    answer_question,
    describe_endpoint,
    generate_sample_code,
    search_endpoints,
)


class TestSearchEndpointsIntegration:
    """search_endpoints の統合テスト。"""

    def test_empty_keyword_returns_validation_error(self):
        """空のキーワードで適切なバリデーションエラーが返されることを確認。"""
        result = search_endpoints(keyword="")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "keyword" in result["message"]
        assert "details" in result
        assert result["details"]["field"] == "keyword"

    def test_whitespace_only_keyword_returns_validation_error(self):
        """空白のみのキーワードで適切なバリデーションエラーが返されることを確認。"""
        result = search_endpoints(keyword="   ")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "空白のみ" in result["message"]

    def test_whitespace_only_category_returns_validation_error(self):
        """空白のみのカテゴリで適切なバリデーションエラーが返されることを確認。"""
        result = search_endpoints(keyword="auth", category="   ")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "空白のみ" in result["message"]

    def test_valid_input_returns_results(self):
        """正常な入力で結果が返されることを確認。"""
        result = search_endpoints(keyword="auth")

        # エラーではなく通常の結果が返される
        assert "error" not in result or result.get("error") is False
        assert "count" in result
        assert "results" in result


class TestDescribeEndpointIntegration:
    """describe_endpoint の統合テスト。"""

    def test_empty_endpoint_name_returns_validation_error(self):
        """空のエンドポイント名で適切なバリデーションエラーが返されることを確認。"""
        result = describe_endpoint(endpoint_name="")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "endpoint_name" in result["message"]

    def test_whitespace_only_endpoint_name_returns_validation_error(self):
        """空白のみのエンドポイント名で適切なバリデーションエラーが返されることを確認。"""
        result = describe_endpoint(endpoint_name="   ")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "空白のみ" in result["message"]

    def test_nonexistent_endpoint_returns_not_found_error(self):
        """存在しないエンドポイントで適切な未検出エラーが返されることを確認。"""
        result = describe_endpoint(endpoint_name="invalid_endpoint_name")

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "invalid_endpoint_name" in result["message"]
        assert "見つかりませんでした" in result["message"]
        # 提案メッセージが含まれることを確認
        assert "search_endpoints" in result["message"]

    def test_valid_endpoint_returns_details(self):
        """正常なエンドポイント名で詳細が返されることを確認。"""
        result = describe_endpoint(endpoint_name="eq-master")

        # エラーではなく通常の結果が返される
        assert "error" not in result or result.get("error") is False
        assert "name" in result
        assert "path" in result
        assert "method" in result


class TestGenerateSampleCodeIntegration:
    """generate_sample_code の統合テスト。"""

    def test_empty_endpoint_name_returns_validation_error(self):
        """空のエンドポイント名で適切なバリデーションエラーが返されることを確認。"""
        result = generate_sample_code(endpoint_name="")

        assert isinstance(result, dict)
        assert result["error"] is True
        assert result["error_type"] == "ValidationError"

    def test_unsupported_language_returns_validation_error(self):
        """サポートされていない言語で適切なバリデーションエラーが返されることを確認。"""
        result = generate_sample_code(endpoint_name="eq-master", language="javascript")

        assert isinstance(result, dict)
        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "サポートされていません" in result["message"]
        assert "python" in result["message"]

    def test_nonexistent_endpoint_returns_not_found_error(self):
        """存在しないエンドポイントで適切な未検出エラーが返されることを確認。"""
        result = generate_sample_code(endpoint_name="invalid_endpoint")

        assert isinstance(result, dict)
        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "invalid_endpoint" in result["message"]

    def test_valid_input_returns_code(self):
        """正常な入力でコードが返されることを確認。"""
        result = generate_sample_code(endpoint_name="eq-master")

        # エラーではなく文字列(コード)が返される
        assert isinstance(result, str)
        assert "import httpx" in result or "def " in result


class TestAnswerQuestionIntegration:
    """answer_question の統合テスト。"""

    def test_empty_question_returns_validation_error(self):
        """空の質問で適切なバリデーションエラーが返されることを確認。"""
        result = answer_question(question="")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "question" in result["message"]

    def test_whitespace_only_question_returns_validation_error(self):
        """空白のみの質問で適切なバリデーションエラーが返されることを確認。"""
        result = answer_question(question="   ")

        assert result["error"] is True
        assert result["error_type"] == "ValidationError"
        assert "空白のみ" in result["message"]

    def test_valid_question_returns_answer(self):
        """正常な質問で回答が返されることを確認。"""
        result = answer_question(question="認証方法は?")

        # エラーではなく通常の結果が返される
        assert "error" not in result or result.get("error") is False
        assert "matched" in result


class TestErrorMessageQuality:
    """エラーメッセージの品質を確認する統合テスト。"""

    def test_validation_error_is_user_friendly(self):
        """バリデーションエラーがユーザーフレンドリーであることを確認。"""
        result = search_endpoints(keyword="")

        # ユーザーが問題を理解できるメッセージ
        assert "error" in result
        assert "message" in result
        assert len(result["message"]) > 0  # メッセージが空でない

        # フィールド名が含まれる
        assert "keyword" in result["message"] or "keyword" in str(result["details"])

    def test_not_found_error_includes_helpful_suggestion(self):
        """未検出エラーに役立つ提案が含まれることを確認。"""
        result = describe_endpoint(endpoint_name="nonexistent")

        assert result["error"] is True
        assert "message" in result
        # 次のアクションを示す提案が含まれる
        assert (
            "search_endpoints" in result["message"]
            or "正しい" in result["message"]
            or "suggestion" in result["details"]
        )

    def test_error_response_has_consistent_structure(self):
        """すべてのエラーレスポンスが一貫した構造を持つことを確認。"""
        # バリデーションエラー
        val_error = search_endpoints(keyword="")
        assert "error" in val_error
        assert "error_type" in val_error
        assert "message" in val_error
        assert "details" in val_error

        # 未検出エラー
        not_found_error = describe_endpoint(endpoint_name="invalid")
        assert "error" in not_found_error
        assert "error_type" in not_found_error
        assert "message" in not_found_error
        assert "details" in not_found_error
