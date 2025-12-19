"""Tests for generate_sample_code tool."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from j_quants_doc_mcp.server import generate_sample_code


# フィクスチャ: テスト用エンドポイントデータ
@pytest.fixture
def mock_endpoints_data():
    """テスト用のエンドポイントデータを返す"""
    fixture_path = Path(__file__).parent / "fixtures" / "test_endpoints.json"
    with open(fixture_path, encoding="utf-8") as f:
        return json.load(f)


class TestGenerateSampleCodeSuccess:
    """generate_sample_code の正常系テスト"""

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    @patch("j_quants_doc_mcp.tools.codegen.Environment")
    def test_generate_eq_master_code(
        self, mock_env_class, mock_find, mock_endpoints_data
    ):
        """eq-masterのサンプルコードが生成できることを確認"""
        endpoint = mock_endpoints_data["endpoints"][0]
        mock_find.return_value = endpoint

        mock_template = MagicMock()
        mock_template.render.return_value = "# Generated code for eq-master"
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        result = generate_sample_code("eq-master")

        assert isinstance(result, str)
        assert "eq-master" in result

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    @patch("j_quants_doc_mcp.tools.codegen.Environment")
    def test_default_language_is_python(
        self, mock_env_class, mock_find, mock_endpoints_data
    ):
        """デフォルト言語がPythonであることを確認"""
        endpoint = mock_endpoints_data["endpoints"][0]
        mock_find.return_value = endpoint

        mock_template = MagicMock()
        mock_template.render.return_value = "# Python code"
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        # 言語を指定しない場合
        result = generate_sample_code("eq-master")

        assert isinstance(result, str)
        # Pythonテンプレートが使われていることを確認
        mock_env.get_template.assert_called_with("python_httpx.jinja2")

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    @patch("j_quants_doc_mcp.tools.codegen.Environment")
    def test_template_receives_correct_params(
        self, mock_env_class, mock_find, mock_endpoints_data
    ):
        """テンプレートに正しいパラメータが渡されることを確認"""
        endpoint = mock_endpoints_data["endpoints"][0]
        mock_find.return_value = endpoint

        mock_template = MagicMock()
        mock_template.render.return_value = "# Code"
        mock_env = MagicMock()
        mock_env.get_template.return_value = mock_template
        mock_env_class.return_value = mock_env

        generate_sample_code("eq-master")

        # renderが呼ばれた際の引数を確認
        call_kwargs = mock_template.render.call_args.kwargs
        assert "endpoint_name" in call_kwargs
        assert "method" in call_kwargs
        assert "path" in call_kwargs
        assert call_kwargs["endpoint_name"] == "eq-master"
        assert call_kwargs["method"] == "GET"
        assert call_kwargs["path"] == "/equities/master"


class TestGenerateSampleCodeError:
    """generate_sample_code の異常系テスト"""

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    def test_endpoint_not_found(self, mock_find):
        """存在しないエンドポイント名でエラーが返ることを確認"""
        mock_find.return_value = None

        result = generate_sample_code("nonexistent_endpoint")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error_type"] == "NotFoundError"
        assert "nonexistent_endpoint" in result["message"]

    def test_unsupported_language(self):
        """サポートされていない言語でバリデーションエラーになることを確認"""
        result = generate_sample_code("eq-master", language="javascript")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error_type"] == "ValidationError"

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    def test_empty_endpoint_name(self, mock_find):
        """空文字列のエンドポイント名でエラーになることを確認"""
        mock_find.return_value = None

        result = generate_sample_code("")

        assert isinstance(result, dict)
        assert "error" in result

    @patch("j_quants_doc_mcp.tools.codegen._find_endpoint")
    @patch("j_quants_doc_mcp.tools.codegen.Environment")
    def test_template_error(self, mock_env_class, mock_find, mock_endpoints_data):
        """テンプレートエラーが適切にハンドリングされることを確認"""
        endpoint = mock_endpoints_data["endpoints"][0]
        mock_find.return_value = endpoint

        # テンプレートエラーを発生させる
        mock_env = MagicMock()
        mock_env.get_template.side_effect = Exception("Template error")
        mock_env_class.return_value = mock_env

        result = generate_sample_code("eq-master")

        assert isinstance(result, dict)
        assert "error" in result
        assert result["error_type"] == "InternalError"
