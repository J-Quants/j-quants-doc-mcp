"""バリデーションとエラーハンドリングのテスト。"""

import pytest
from j_quants_doc_mcp.schemas import (
    AnswerQuestionInput,
    DescribeEndpointInput,
    GenerateSampleCodeInput,
    SearchEndpointsInput,
)
from pydantic import ValidationError


class TestSearchEndpointsInput:
    """SearchEndpointsInput のバリデーションテスト。"""

    def test_valid_input(self):
        """正常な入力のテスト。"""
        input_data = SearchEndpointsInput(keyword="auth", category="token")
        assert input_data.keyword == "auth"
        assert input_data.category == "token"

    def test_keyword_whitespace_stripped(self):
        """キーワードの前後空白が削除されることを確認。"""
        input_data = SearchEndpointsInput(keyword="  auth  ")
        assert input_data.keyword == "auth"

    def test_empty_keyword_raises_error(self):
        """空のキーワードでエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            SearchEndpointsInput(keyword="")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "keyword" in str(errors[0]["loc"])

    def test_whitespace_only_keyword_raises_error(self):
        """空白のみのキーワードでエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            SearchEndpointsInput(keyword="   ")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "空白のみ" in errors[0]["msg"]

    def test_category_optional(self):
        """カテゴリが省略可能であることを確認。"""
        input_data = SearchEndpointsInput(keyword="auth")
        assert input_data.keyword == "auth"
        assert input_data.category is None

    def test_whitespace_only_category_raises_error(self):
        """空白のみのカテゴリでエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            SearchEndpointsInput(keyword="auth", category="   ")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "空白のみ" in errors[0]["msg"]


class TestDescribeEndpointInput:
    """DescribeEndpointInput のバリデーションテスト。"""

    def test_valid_input(self):
        """正常な入力のテスト。"""
        input_data = DescribeEndpointInput(endpoint_name="eq-master")
        assert input_data.endpoint_name == "eq-master"

    def test_endpoint_name_whitespace_stripped(self):
        """エンドポイント名の前後空白が削除されることを確認。"""
        input_data = DescribeEndpointInput(endpoint_name="  eq-master  ")
        assert input_data.endpoint_name == "eq-master"

    def test_empty_endpoint_name_raises_error(self):
        """空のエンドポイント名でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeEndpointInput(endpoint_name="")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "endpoint_name" in str(errors[0]["loc"])

    def test_whitespace_only_endpoint_name_raises_error(self):
        """空白のみのエンドポイント名でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            DescribeEndpointInput(endpoint_name="   ")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "空白のみ" in errors[0]["msg"]


class TestGenerateSampleCodeInput:
    """GenerateSampleCodeInput のバリデーションテスト。"""

    def test_valid_input_default_language(self):
        """正常な入力(デフォルト言語)のテスト。"""
        input_data = GenerateSampleCodeInput(endpoint_name="eq-master")
        assert input_data.endpoint_name == "eq-master"
        assert input_data.language == "python"
        assert input_data.params is None

    def test_valid_input_explicit_language(self):
        """正常な入力(明示的な言語指定)のテスト。"""
        input_data = GenerateSampleCodeInput(
            endpoint_name="eq-master", language="python"
        )
        assert input_data.endpoint_name == "eq-master"
        assert input_data.language == "python"

    def test_language_case_insensitive(self):
        """言語指定が大文字小文字を区別しないことを確認。"""
        input_data = GenerateSampleCodeInput(
            endpoint_name="eq-master", language="Python"
        )
        assert input_data.language == "python"

    def test_unsupported_language_raises_error(self):
        """サポートされていない言語でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateSampleCodeInput(endpoint_name="eq-master", language="javascript")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "サポートされていません" in errors[0]["msg"]

    def test_empty_endpoint_name_raises_error(self):
        """空のエンドポイント名でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            GenerateSampleCodeInput(endpoint_name="")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "endpoint_name" in str(errors[0]["loc"])


class TestAnswerQuestionInput:
    """AnswerQuestionInput のバリデーションテスト。"""

    def test_valid_input(self):
        """正常な入力のテスト。"""
        input_data = AnswerQuestionInput(question="認証方法は?")
        assert input_data.question == "認証方法は?"

    def test_question_whitespace_stripped(self):
        """質問の前後空白が削除されることを確認。"""
        input_data = AnswerQuestionInput(question="  認証方法は?  ")
        assert input_data.question == "認証方法は?"

    def test_empty_question_raises_error(self):
        """空の質問でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            AnswerQuestionInput(question="")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "question" in str(errors[0]["loc"])

    def test_whitespace_only_question_raises_error(self):
        """空白のみの質問でエラーが発生することを確認。"""
        with pytest.raises(ValidationError) as exc_info:
            AnswerQuestionInput(question="   ")

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert "空白のみ" in errors[0]["msg"]
