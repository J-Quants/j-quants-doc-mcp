"""Tests for search_endpoints tool."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from j_quants_doc_mcp.server import search_endpoints


# フィクスチャ: テスト用エンドポイントデータ
@pytest.fixture
def mock_endpoints_data():
    """テスト用のエンドポイントデータを返す"""
    fixture_path = Path(__file__).parent / "fixtures" / "test_endpoints.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


class TestSearchEndpointsSuccess:
    """search_endpoints の正常系テスト"""

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_by_name(self, mock_load, mock_endpoints_data):
        """エンドポイント名で検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("eq-master")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "eq-master"
        assert result["results"][0]["path"] == "/equities/master"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_by_path(self, mock_load, mock_endpoints_data):
        """パスで検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("equities")

        # eq-masterとeq-bars-dailyの両方がヒット
        assert result["count"] == 2
        paths = [r["path"] for r in result["results"]]
        assert "/equities/master" in paths
        assert "/equities/bars/daily" in paths

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_by_description(self, mock_load, mock_endpoints_data):
        """説明文で検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("銘柄")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "eq-master"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_by_name_ja(self, mock_load, mock_endpoints_data):
        """日本語名で検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("上場銘柄一覧")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "eq-master"
        assert result["results"][0]["name_ja"] == "上場銘柄一覧"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_by_name_en(self, mock_load, mock_endpoints_data):
        """英語名で検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("Listed Issue")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "eq-master"
        assert result["results"][0]["name_en"] == "Listed Issue Information"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_result_includes_name_ja_en(self, mock_load, mock_endpoints_data):
        """検索結果にname_ja/name_enが含まれることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("eq-master")

        assert result["count"] == 1
        assert "name_ja" in result["results"][0]
        assert "name_en" in result["results"][0]

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_with_category(self, mock_load, mock_endpoints_data):
        """カテゴリフィルタで検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("master", category="equities")

        assert result["count"] >= 1
        assert any(r["name"] == "eq-master" for r in result["results"])

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_case_insensitive(self, mock_load, mock_endpoints_data):
        """大文字小文字を区別せず検索できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("EQ-MASTER")

        assert result["count"] == 1
        assert result["results"][0]["name"] == "eq-master"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_search_no_results(self, mock_load, mock_endpoints_data):
        """該当なしの場合、空の結果が返ることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = search_endpoints("nonexistent")

        assert result["count"] == 0
        assert result["results"] == []


class TestSearchEndpointsError:
    """search_endpoints の異常系テスト"""

    def test_empty_keyword(self):
        """空文字列のキーワードでバリデーションエラーになることを確認"""
        result = search_endpoints("")

        assert "error" in result
        assert result["error_type"] == "ValidationError"

    @patch("j_quants_doc_mcp.tools.search._load_endpoints")
    def test_internal_error(self, mock_load):
        """内部エラーが適切にハンドリングされることを確認"""
        mock_load.side_effect = Exception("Test error")

        result = search_endpoints("equities")

        assert "error" in result
        assert result["error_type"] == "InternalError"
