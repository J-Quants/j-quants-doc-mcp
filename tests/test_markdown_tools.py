"""Markdownベースのツールの統合テスト（HTTPモック使用）。"""

import json
import time
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

# テスト対象のツールをインポート
from j_quants_doc_mcp.tools.describe import describe_endpoint
from j_quants_doc_mcp.tools.fetch import fetch_spec_page
from j_quants_doc_mcp.tools.search import search_endpoints


# モックデータの読み込み
@pytest.fixture
def mock_data_spec() -> str:
    """data-spec.md のモックデータ。"""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_data_spec.md"
    return fixture_path.read_text()


@pytest.fixture
def mock_product_master() -> str:
    """product-master.md のモックデータ。"""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_product_master.md"
    return fixture_path.read_text()


@pytest.fixture
def mock_status_codes() -> str:
    """status-codes.md のモックデータ。"""
    fixture_path = Path(__file__).parent / "fixtures" / "mock_status_codes.md"
    return fixture_path.read_text()


@pytest.fixture
def mock_spec_config() -> dict[str, Any]:
    """spec_config.json のモック設定。"""
    return {
        "base_url": "http://localhost:3000",
        "default_language": "ja",
        "endpoints": {"list_page": "/spec/data-spec"},
        "cache_ttl_seconds": 300,
        "external_links": {"spec_docs": "/spec", "help": "/help"},
    }


def create_http_response_mock(content: str, status: int = 200) -> MagicMock:
    """HTTP レスポンスのモックを作成。"""
    mock_response = MagicMock()
    mock_response.read.return_value = content.encode("utf-8")
    mock_response.status = status
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = False
    return mock_response


class TestSearchEndpoints:
    """search_endpoints ツールのテスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_search_success(
        self, mock_config: MagicMock, mock_urlopen: MagicMock, mock_data_spec: str
    ) -> None:
        """正常にdata-spec.mdを取得できることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_data_spec)

        result = search_endpoints(keyword="product")

        # 成功時はerrorキーが含まれない
        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "Product Master" in result["content"]
        assert result["source_url"] == "http://localhost:3000/ja/spec/data-spec"
        assert result["cached"] is False
        assert "instruction" in result
        assert "CSV" in result["instruction"]  # Bulk API の指示が含まれる

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_search_with_category(
        self, mock_config: MagicMock, mock_urlopen: MagicMock, mock_data_spec: str
    ) -> None:
        """カテゴリ指定で検索できることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_data_spec)

        result = search_endpoints(keyword="prices", category="daily")

        # 成功時はerrorキーが含まれない
        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "instruction" in result
        assert "prices" in result["instruction"]
        assert "daily" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_search_caching(
        self, mock_config: MagicMock, mock_urlopen: MagicMock, mock_data_spec: str
    ) -> None:
        """キャッシュが機能することを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_data_spec)

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        # 1回目: キャッシュなし
        result1 = search_endpoints(keyword="product")
        assert result1["cached"] is False
        assert mock_urlopen.call_count == 1

        # 2回目: キャッシュあり
        result2 = search_endpoints(keyword="product")
        assert result2["cached"] is True
        assert result2["content"] == result1["content"]
        assert mock_urlopen.call_count == 1  # 2回目は呼ばれない

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_search_network_error(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """ネットワークエラーを適切に処理することを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }
        mock_urlopen.side_effect = URLError("Connection failed")

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        result = search_endpoints(keyword="product")

        assert result["error"] is True
        assert result["error_type"] == "NetworkError"
        assert "Connection failed" in result["message"]
        assert "instruction" in result
        assert "http://localhost:3000/ja/spec" in result["instruction"]
        assert "http://localhost:3000/ja/help" in result["instruction"]


class TestDescribeEndpoint:
    """describe_endpoint ツールのテスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_describe_success(
        self,
        mock_config: MagicMock,
        mock_urlopen: MagicMock,
        mock_product_master: str,
    ) -> None:
        """正常にエンドポイント詳細を取得できることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_product_master)

        result = describe_endpoint(endpoint_name="product-master")

        # 成功時はerrorキーが含まれない
        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "Product Master" in result["content"]
        assert "GET" in result["content"]
        assert result["source_url"] == "http://localhost:3000/ja/spec/product-master"
        assert result["endpoint_name"] == "product-master"
        assert result["cached"] is False
        assert "instruction" in result
        assert "source_url" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_describe_not_found(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """存在しないエンドポイントで404エラーを処理することを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:3000/ja/spec/nonexistent.md",
            404,
            "Not Found",
            {},
            None,
        )

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        result = describe_endpoint(endpoint_name="nonexistent")

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "nonexistent" in result["message"]
        assert "instruction" in result
        assert "http://localhost:3000/ja/spec" in result["instruction"]
        assert "http://localhost:3000/ja/help" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_describe_uses_default_language(
        self,
        mock_config: MagicMock,
        mock_urlopen: MagicMock,
        mock_product_master: str,
    ) -> None:
        """デフォルト言語でエンドポイント詳細を取得できることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_product_master)

        result = describe_endpoint(endpoint_name="product-master")

        # 成功時はerrorキーが含まれない
        assert "error" not in result or result.get("error") is not True
        assert result["source_url"] == "http://localhost:3000/ja/spec/product-master"


class TestFetchSpecPage:
    """fetch_spec_page ツールのテスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_fetch_success(
        self,
        mock_config: MagicMock,
        mock_urlopen: MagicMock,
        mock_status_codes: str,
    ) -> None:
        """正常に任意のspecページを取得できることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_status_codes)

        result = fetch_spec_page(path="/spec/product-master/status-codes")

        # 成功時はerrorキーが含まれない
        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "Status Codes" in result["content"]
        assert "Active" in result["content"]
        assert result["source_url"] == "http://localhost:3000/ja/spec/product-master/status-codes"
        assert result["path"] == "/spec/product-master/status-codes"
        assert result["cached"] is False

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_fetch_with_leading_slash_removed(
        self,
        mock_config: MagicMock,
        mock_urlopen: MagicMock,
        mock_status_codes: str,
    ) -> None:
        """パスの先頭のスラッシュが適切に処理されることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
        }
        mock_urlopen.return_value = create_http_response_mock(mock_status_codes)

        # 先頭にスラッシュあり
        result1 = fetch_spec_page(path="/spec/product-master/status-codes")
        assert "error" not in result1 or result1.get("error") is not True

        # 先頭にスラッシュなし（両方とも同じURLを生成する）
        result2 = fetch_spec_page(path="spec/product-master/status-codes")
        assert "error" not in result2 or result2.get("error") is not True

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_fetch_not_found(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """存在しないページで404エラーを処理することを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:3000/ja/spec/nonexistent.md",
            404,
            "Not Found",
            {},
            None,
        )

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        result = fetch_spec_page(path="/spec/nonexistent")

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "instruction" in result


class TestCacheBehavior:
    """キャッシュの動作テスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    @patch("j_quants_doc_mcp.loaders.markdown_loader.time.time")
    def test_cache_expiration(
        self,
        mock_time: MagicMock,
        mock_config: MagicMock,
        mock_urlopen: MagicMock,
        mock_product_master: str,
    ) -> None:
        """キャッシュが期限切れで再取得されることを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 10,  # 10秒のTTL
        }
        mock_urlopen.return_value = create_http_response_mock(mock_product_master)

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        # 時刻を固定
        current_time = 1000.0
        mock_time.return_value = current_time

        # 1回目: キャッシュなし
        result1 = describe_endpoint(endpoint_name="product-master")
        assert result1["cached"] is False
        assert mock_urlopen.call_count == 1

        # 5秒後: キャッシュあり（有効期限内）
        mock_time.return_value = current_time + 5
        result2 = describe_endpoint(endpoint_name="product-master")
        assert result2["cached"] is True
        assert mock_urlopen.call_count == 1

        # 15秒後: キャッシュ期限切れ（再取得）
        mock_time.return_value = current_time + 15
        result3 = describe_endpoint(endpoint_name="product-master")
        assert result3["cached"] is False
        assert mock_urlopen.call_count == 2


class TestEnvironmentVariable:
    """環境変数のテスト。"""

    def test_base_url_from_environment_variable(self, monkeypatch) -> None:
        """環境変数JQUANTS_BASE_URLでbase_urlが上書きされることを確認。"""
        # 環境変数を設定
        monkeypatch.setenv("JQUANTS_BASE_URL", "http://test.example.com")

        from j_quants_doc_mcp.loaders.markdown_loader import _load_config

        config = _load_config()

        assert config["base_url"] == "http://test.example.com"

    def test_base_url_default_without_environment_variable(self) -> None:
        """環境変数がない場合はJSONのデフォルト値が使用されることを確認。"""
        # 環境変数が設定されていないことを確認（念のため）
        import os

        if "JQUANTS_BASE_URL" in os.environ:
            del os.environ["JQUANTS_BASE_URL"]

        from j_quants_doc_mcp.loaders.markdown_loader import _load_config

        config = _load_config()

        assert config["base_url"] == "https://jpx-jquants.com"


class TestErrorHandling:
    """エラーハンドリングのテスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_http_500_error(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """500エラーを適切に処理することを確認。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:3000/ja/spec/product-master.md",
            500,
            "Internal Server Error",
            {},
            None,
        )

        # キャッシュをクリア
        from j_quants_doc_mcp.loaders.markdown_loader import _cache

        _cache.clear()

        result = describe_endpoint(endpoint_name="product-master")

        assert result["error"] is True
        assert result["error_type"] == "NetworkError"
        assert "500" in result["message"]

    def test_empty_keyword_validation(self) -> None:
        """空のキーワードでバリデーションエラーになることを確認。"""
        # スキーマレベルでバリデーションされるため、pydanticのValidationErrorが発生する
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            from j_quants_doc_mcp.schemas import SearchEndpointsInput

            SearchEndpointsInput(keyword="")

        assert "keyword" in str(exc_info.value)

    def test_whitespace_keyword_validation(self) -> None:
        """空白のみのキーワードでバリデーションエラーになることを確認。"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            from j_quants_doc_mcp.schemas import SearchEndpointsInput

            SearchEndpointsInput(keyword="   ")

        assert "空白" in str(exc_info.value)

    def test_empty_endpoint_name_validation(self) -> None:
        """空のエンドポイント名でバリデーションエラーになることを確認。"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            from j_quants_doc_mcp.schemas import DescribeEndpointInput

            DescribeEndpointInput(endpoint_name="")

        errors = exc_info.value.errors()
        assert any("endpoint_name" in str(err) for err in errors)

    def test_empty_path_validation(self) -> None:
        """空のパスでバリデーションエラーになることを確認。"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            from j_quants_doc_mcp.schemas import FetchSpecPageInput

            FetchSpecPageInput(path="")

        errors = exc_info.value.errors()
        assert any("path" in str(err) for err in errors)
