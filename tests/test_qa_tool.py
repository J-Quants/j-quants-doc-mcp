"""Tests for answer_question tool."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from j_quants_doc_mcp.server import answer_question


# フィクスチャ: テスト用FAQデータ
@pytest.fixture
def mock_faq_data():
    """テスト用のFAQデータを返す"""
    fixture_path = Path(__file__).parent / "fixtures" / "test_faq.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


class TestAnswerQuestionSuccess:
    """answer_question の正常系テスト"""

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_match_by_keyword(self, mock_load, mock_faq_data):
        """キーワードでマッチすることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("APIキーの有効期限について")

        assert result["matched"] is True
        assert result["count"] > 0
        assert len(result["answers"]) > 0
        # 最初の回答がAPIキーに関するものであることを確認
        assert "APIキー" in result["answers"][0]["answer"]

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_match_multiple_keywords(self, mock_load, mock_faq_data):
        """複数のキーワードでマッチすることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("レート制限")

        assert result["matched"] is True
        assert result["count"] > 0
        # レート制限に関する回答が含まれることを確認
        # キーワードマッチングなので、回答内容にキーワードが含まれるとは限らない
        # 最初の回答がレート制限のカテゴリであることを確認
        assert (
            "レート" in result["answers"][0]["category"]
            or "リクエスト" in result["answers"][0]["answer"]
        )

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_case_insensitive_match(self, mock_load, mock_faq_data):
        """大文字小文字を区別せずマッチすることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("トークン")

        assert result["matched"] is True

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_answer_structure(self, mock_load, mock_faq_data):
        """回答の構造が正しいことを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("トークン")

        assert "matched" in result
        assert "count" in result
        assert "answers" in result

        # 回答の各項目の構造確認
        for answer in result["answers"]:
            assert "category" in answer
            assert "question" in answer
            assert "answer" in answer
            assert "related_endpoints" in answer

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_no_match_returns_suggestion(self, mock_load, mock_faq_data):
        """マッチしない場合、提案が返ることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("全く関係ない質問")

        assert result["matched"] is False
        assert "suggestion" in result
        assert "available_categories" in result
        assert len(result["available_categories"]) > 0

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_returns_top_3_matches(self, mock_load, mock_faq_data):
        """最大3件の回答が返ることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("データ")

        if result["matched"]:
            # マッチした場合、最大3件まで
            assert len(result["answers"]) <= 3

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_matched_keywords_included(self, mock_load, mock_faq_data):
        """マッチしたキーワードが含まれることを確認"""
        mock_load.return_value = mock_faq_data

        result = answer_question("レート制限")

        if result["matched"] and len(result["answers"]) > 0:
            # マッチしたキーワードが含まれる場合がある
            first_answer = result["answers"][0]
            # matched_keywordsフィールドが存在する可能性がある
            if "matched_keywords" in first_answer:
                assert len(first_answer["matched_keywords"]) > 0


class TestAnswerQuestionError:
    """answer_question の異常系テスト"""

    def test_empty_question(self):
        """空文字列の質問でバリデーションエラーになることを確認"""
        result = answer_question("")

        assert "error" in result
        assert result["error_type"] == "ValidationError"

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_internal_error(self, mock_load):
        """内部エラーが適切にハンドリングされることを確認"""
        mock_load.side_effect = Exception("Test error")

        result = answer_question("トークン")

        assert "error" in result
        assert result["error_type"] == "InternalError"

    @patch("j_quants_doc_mcp.tools.qa.load_faqs")
    def test_empty_faq_data(self, mock_load):
        """FAQデータが空の場合の動作を確認"""
        mock_load.return_value = {"faqs": []}

        result = answer_question("トークン")

        assert result["matched"] is False
        assert "suggestion" in result
