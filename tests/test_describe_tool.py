"""Tests for describe_endpoint tool."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest
from j_quants_doc_mcp.server import describe_endpoint


# フィクスチャ: テスト用エンドポイントデータ
@pytest.fixture
def mock_endpoints_data():
    """テスト用のエンドポイントデータを返す"""
    fixture_path = Path(__file__).parent / "fixtures" / "test_endpoints.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


class TestDescribeEndpointSuccess:
    """describe_endpoint の正常系テスト"""

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_describe_eq_master(self, mock_load, mock_endpoints_data):
        """eq-masterエンドポイントの詳細情報を取得できることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("eq-master")

        assert result["name"] == "eq-master"
        assert result["path"] == "/equities/master"
        assert result["method"] == "GET"
        assert result["auth_required"] is True

        # 日本語名・英語名の確認
        assert result["name_ja"] == "上場銘柄一覧"
        assert result["name_en"] == "Listed Issue Information"

        # 任意パラメータの確認
        assert len(result["parameters"]["optional"]) == 2
        optional_param_names = [p["name"] for p in result["parameters"]["optional"]]
        assert "code" in optional_param_names
        assert "date" in optional_param_names

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_parameters_structure(self, mock_load, mock_endpoints_data):
        """パラメータの構造が正しいことを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("eq-master")

        # パラメータの構造確認
        for param in result["parameters"]["required"]:
            assert "name" in param
            assert "type" in param
            assert "description" in param
            assert "location" in param

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_response_structure(self, mock_load, mock_endpoints_data):
        """レスポンスの構造が正しいことを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("eq-master")

        assert "response" in result
        assert "description" in result["response"]
        assert "fields" in result["response"]
        assert len(result["response"]["fields"]) > 0

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_data_update_with_notes(self, mock_load, mock_endpoints_data):
        """data_updateフィールド（留意事項あり）が正しく返却されることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("eq-master")

        assert "data_update" in result
        assert result["data_update"]["frequency"] == "日次"
        assert result["data_update"]["time"] == "17:30頃 / 翌営業日8:00頃"
        assert "notes" in result["data_update"]
        assert "翌営業日時点" in result["data_update"]["notes"]

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_data_update_without_notes(self, mock_load, mock_endpoints_data):
        """data_updateフィールド（留意事項なし）が正しく返却されることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("eq-bars-daily")

        assert "data_update" in result
        assert result["data_update"]["frequency"] == "日次"
        assert result["data_update"]["time"] == "16:30頃"
        assert "notes" not in result["data_update"]


class TestDescribeEndpointError:
    """describe_endpoint の異常系テスト"""

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_endpoint_not_found(self, mock_load, mock_endpoints_data):
        """存在しないエンドポイント名でエラーが返ることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("nonexistent_endpoint")

        assert "error" in result
        assert result["error_type"] == "NotFoundError"
        assert "nonexistent_endpoint" in result["message"]

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_empty_endpoint_name(self, mock_load, mock_endpoints_data):
        """空文字列のエンドポイント名でバリデーションエラーになることを確認"""
        mock_load.return_value = mock_endpoints_data

        result = describe_endpoint("")

        assert "error" in result
        # 空文字列はバリデーションエラーになる
        assert result["error_type"] == "ValidationError"

    @patch("j_quants_doc_mcp.tools.describe._load_endpoints")
    def test_internal_error(self, mock_load):
        """内部エラーが適切にハンドリングされることを確認"""
        mock_load.side_effect = Exception("Test error")

        result = describe_endpoint("eq-master")

        assert "error" in result
        assert result["error_type"] == "InternalError"
