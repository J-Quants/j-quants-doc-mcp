"""V1 API対応および移行ガイドツールのテスト。"""

from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest
from pydantic import ValidationError

from j_quants_doc_mcp.schemas import (
    DescribeEndpointInput,
    MigrateV1ToV2Input,
    SearchEndpointsInput,
)
from j_quants_doc_mcp.tools.describe import describe_endpoint
from j_quants_doc_mcp.tools.migrate import migrate_v1_to_v2
from j_quants_doc_mcp.tools.info import get_info
from j_quants_doc_mcp.tools.search import search_endpoints

FIXTURES_DIR = Path(__file__).parent / "fixtures"

MOCK_V1_CONFIG = {
    "base_url": "http://localhost:3000",
    "default_language": "ja",
    "endpoints": {"list_page": "/spec/data-spec"},
    "cache_ttl_seconds": 300,
    "external_links": {
        "spec_docs": "/spec",
        "help": "/help",
        "migration_v1_v2": "/spec/migration-v1-v2",
    },
    "v1": {
        "base_url": "http://v1.example.com",
        "endpoints": {"list_page": "/api-reference"},
    },
}


def _read_fixture(name: str) -> str:
    return (FIXTURES_DIR / name).read_text()


def _http_response_mock(content: str) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = content.encode("utf-8")
    mock.status = 200
    mock.__enter__.return_value = mock
    mock.__exit__.return_value = False
    return mock


# =========================================================
# Schema validation
# =========================================================
class TestApiVersionSchema:
    """api_version パラメータのバリデーション。"""

    def test_search_default_v2(self) -> None:
        inp = SearchEndpointsInput(keyword="株価")
        assert inp.api_version == "v2"

    def test_search_accepts_v1(self) -> None:
        inp = SearchEndpointsInput(keyword="株価", api_version="v1")
        assert inp.api_version == "v1"

    def test_search_rejects_invalid_version(self) -> None:
        with pytest.raises(ValidationError):
            SearchEndpointsInput(keyword="株価", api_version="v3")

    def test_describe_default_v2(self) -> None:
        inp = DescribeEndpointInput(endpoint_name="eq-bars-daily")
        assert inp.api_version == "v2"

    def test_describe_accepts_v1(self) -> None:
        inp = DescribeEndpointInput(endpoint_name="daily_quotes", api_version="v1")
        assert inp.api_version == "v1"

    def test_describe_rejects_invalid_version(self) -> None:
        with pytest.raises(ValidationError):
            DescribeEndpointInput(endpoint_name="eq-bars-daily", api_version="v0")


class TestMigrateV1ToV2Schema:
    """MigrateV1ToV2Input のバリデーション。"""

    def test_none_v1_endpoint(self) -> None:
        inp = MigrateV1ToV2Input()
        assert inp.v1_endpoint is None

    def test_valid_v1_endpoint(self) -> None:
        inp = MigrateV1ToV2Input(v1_endpoint="/v1/prices/daily_quotes")
        assert inp.v1_endpoint == "/v1/prices/daily_quotes"

    def test_whitespace_only_rejected(self) -> None:
        with pytest.raises(ValidationError):
            MigrateV1ToV2Input(v1_endpoint="   ")


# =========================================================
# search_endpoints with api_version="v1"
# =========================================================
class TestSearchEndpointsV1:
    """search_endpoints の V1 対応テスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_search_success(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_v1_api_reference.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = search_endpoints(keyword="daily_quotes", api_version="v1")

        assert "error" not in result or result.get("error") is not True
        assert result["api_version"] == "v1"
        assert "content" in result
        assert "daily_quotes" in result["content"]
        assert "V1 API" in result["instruction"]
        assert "V2" in result["instruction"]
        assert "migrate_v1_to_v2" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_search_network_error(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        mock_urlopen.side_effect = URLError("Connection refused")

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = search_endpoints(keyword="daily_quotes", api_version="v1")

        assert result["error"] is True
        assert result["error_type"] == "NetworkError"

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v2_search_still_works(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """api_version 追加後も V2 がデフォルトで動作することを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_data_spec.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = search_endpoints(keyword="product")

        assert "error" not in result or result.get("error") is not True
        assert result["api_version"] == "v2"


# =========================================================
# describe_endpoint with api_version="v1"
# =========================================================
class TestDescribeEndpointV1:
    """describe_endpoint の V1 対応テスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_describe_success(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_v1_daily_quotes.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = describe_endpoint(endpoint_name="daily_quotes", api_version="v1")

        assert "error" not in result or result.get("error") is not True
        assert result["api_version"] == "v1"
        assert result["endpoint_name"] == "daily_quotes"
        assert "daily_quotes" in result["content"]
        assert "V1 API" in result["instruction"]
        assert "V2" in result["instruction"]
        assert "migrate_v1_to_v2" in result["instruction"]
        assert result["source_url"] == "http://v1.example.com/api-reference/daily_quotes"

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_describe_not_found(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        mock_urlopen.side_effect = HTTPError(
            "http://v1.example.com/api-reference/nonexistent.md",
            404, "Not Found", {}, None,
        )

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = describe_endpoint(endpoint_name="nonexistent", api_version="v1")

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"
        assert "V1" in result["message"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v2_describe_still_works(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """api_version 追加後も V2 がデフォルトで動作することを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_product_master.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = describe_endpoint(endpoint_name="product-master")

        assert "error" not in result or result.get("error") is not True
        assert result["api_version"] == "v2"


# =========================================================
# migrate_v1_to_v2
# =========================================================
class TestMigrateV1ToV2:
    """migrate_v1_to_v2 ツールのテスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_migrate_without_endpoint(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """v1_endpoint 未指定で移行ガイド全体を返す。"""
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_migration_v1_v2.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = migrate_v1_to_v2()

        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "V1 API から V2 API" in result["content"]
        assert "instruction" in result
        assert "認証方式" in result["instruction"]
        assert "describe_endpoint" in result["instruction"] or "V2" in result["instruction"]
        assert "移行ガイド全文" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_migrate_with_endpoint(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """v1_endpoint 指定で該当エンドポイントの移行案内を返す。"""
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_migration_v1_v2.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = migrate_v1_to_v2(v1_endpoint="/v1/prices/daily_quotes")

        assert "error" not in result or result.get("error") is not True
        assert "content" in result
        assert "instruction" in result
        assert "/v1/prices/daily_quotes" in result["instruction"]
        assert "describe_endpoint" in result["instruction"]

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_migrate_page_not_found(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """移行ガイドページが見つからない場合のエラー処理。"""
        mock_config.return_value = MOCK_V1_CONFIG
        mock_urlopen.side_effect = HTTPError(
            "http://localhost:3000/ja/spec/migration-v1-v2.md",
            404, "Not Found", {}, None,
        )

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = migrate_v1_to_v2()

        assert result["error"] is True
        assert result["error_type"] == "NotFoundError"

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_migrate_network_error(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        """ネットワークエラー時のエラー処理。"""
        mock_config.return_value = MOCK_V1_CONFIG
        mock_urlopen.side_effect = URLError("Connection refused")

        from j_quants_doc_mcp.loaders.markdown_loader import _cache
        _cache.clear()

        result = migrate_v1_to_v2()

        assert result["error"] is True
        assert result["error_type"] == "NetworkError"


# =========================================================
# V1 config edge cases
# =========================================================
class TestV1ConfigEdgeCases:
    """V1設定が存在しない場合のエッジケース。"""

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_missing_v1_config(self, mock_config: MagicMock) -> None:
        """v1設定がない場合にValueErrorが発生する。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }

        from j_quants_doc_mcp.loaders.markdown_loader import _get_v1_config

        with pytest.raises(ValueError, match="v1 設定が存在しません"):
            _get_v1_config()

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_missing_migration_path(self, mock_config: MagicMock) -> None:
        """external_links に migration_v1_v2 がない場合にValueErrorが発生する。"""
        mock_config.return_value = {
            "base_url": "http://localhost:3000",
            "default_language": "ja",
            "endpoints": {"list_page": "/spec/data-spec"},
            "cache_ttl_seconds": 300,
            "external_links": {"spec_docs": "/spec", "help": "/help"},
        }

        from j_quants_doc_mcp.tools.migrate import _get_migration_path

        with pytest.raises(ValueError, match="migration_v1_v2"):
            _get_migration_path()


# =========================================================
# V1 loader caching
# =========================================================
class TestV1Caching:
    """V1ローダーのキャッシュ動作テスト。"""

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_endpoint_list_caching(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_v1_api_reference.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache, load_v1_endpoint_list
        _cache.clear()

        result1 = load_v1_endpoint_list()
        assert result1["cached"] is False
        assert mock_urlopen.call_count == 1

        result2 = load_v1_endpoint_list()
        assert result2["cached"] is True
        assert mock_urlopen.call_count == 1

    @patch("urllib.request.urlopen")
    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_v1_endpoint_detail_caching(
        self, mock_config: MagicMock, mock_urlopen: MagicMock
    ) -> None:
        mock_config.return_value = MOCK_V1_CONFIG
        content = _read_fixture("mock_v1_daily_quotes.md")
        mock_urlopen.return_value = _http_response_mock(content)

        from j_quants_doc_mcp.loaders.markdown_loader import _cache, load_v1_endpoint_detail
        _cache.clear()

        result1 = load_v1_endpoint_detail("daily_quotes")
        assert result1["cached"] is False
        assert mock_urlopen.call_count == 1

        result2 = load_v1_endpoint_detail("daily_quotes")
        assert result2["cached"] is True
        assert mock_urlopen.call_count == 1


# =========================================================
# get_plan_info
# =========================================================
class TestGetInfo:
    """get_info ツールのテスト。"""

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_returns_external_links(self, mock_config: MagicMock) -> None:
        """公式ページへのリンクが返されることを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG

        result = get_info(query="Premiumプランの料金は？")

        assert result["error"] is False
        assert "external_links" in result
        assert "spec_docs" in result["external_links"]
        assert "help" in result["external_links"]

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_instruction_warns_not_to_guess(self, mock_config: MagicMock) -> None:
        """instructionにプラン情報を推測しないよう指示が含まれることを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG

        result = get_info(query="Freeプランで取得できるデータは？")

        assert "instruction" in result
        assert "推測" in result["instruction"]
        assert "公式ページ" in result["instruction"]

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_query_is_preserved(self, mock_config: MagicMock) -> None:
        """queryがレスポンスに保持されることを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG

        result = get_info(query="プラン変更したい")

        assert result["query"] == "プラン変更したい"

    @patch("j_quants_doc_mcp.loaders.markdown_loader._load_config")
    def test_works_without_query(self, mock_config: MagicMock) -> None:
        """query未指定でも正常に動作することを確認。"""
        mock_config.return_value = MOCK_V1_CONFIG

        result = get_info()

        assert result["error"] is False
        assert result["query"] is None
        assert "external_links" in result
