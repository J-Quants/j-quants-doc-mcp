"""E2Eテスト: MCPクライアント経由でのツール連携動作確認。

MCPクライアント経由でJ-Quants MCPサーバとやり取りできることを確認する。
"""

import json

import pytest
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client


class TestMCPClientE2E:
    """MCPクライアント経由でのE2Eテスト。"""

    @pytest.mark.asyncio
    async def test_server_startup_and_initialization(self):
        """サーバが起動し、初期化できることを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # サーバを初期化
                await session.initialize()

                # 初期化が成功したことを確認
                assert session is not None

    @pytest.mark.asyncio
    async def test_list_tools(self):
        """tools/list リクエストでツール一覧が取得できることを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # ツール一覧を取得
                result = await session.list_tools()

                # 期待されるツールが含まれることを確認
                tool_names = [tool.name for tool in result.tools]
                assert "search_endpoints" in tool_names
                assert "describe_endpoint" in tool_names
                assert "generate_sample_code" in tool_names
                assert "answer_question" in tool_names

    @pytest.mark.asyncio
    async def test_search_endpoints_tool(self):
        """search_endpoints ツールが正常に動作することを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # tools/call で search_endpoints を実行
                result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": "equities"},
                )

                # レスポンスの検証
                assert len(result.content) > 0
                assert result.content[0].type == "text"

                # text をJSONとしてパース
                text_data = json.loads(result.content[0].text)

                # 結果の検証
                assert "count" in text_data
                assert "results" in text_data
                assert text_data["count"] > 0
                assert len(text_data["results"]) > 0

    @pytest.mark.asyncio
    async def test_describe_endpoint_tool(self):
        """describe_endpoint ツールが正常に動作することを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # tools/call で describe_endpoint を実行
                result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": "eq-master"},
                )

                # レスポンスの検証
                assert len(result.content) > 0
                assert result.content[0].type == "text"

                text_data = json.loads(result.content[0].text)

                # エンドポイント情報の検証
                assert "name" in text_data
                assert "path" in text_data
                assert "method" in text_data
                assert text_data["name"] == "eq-master"

    @pytest.mark.asyncio
    async def test_generate_sample_code_tool(self):
        """generate_sample_code ツールが正常に動作することを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # tools/call で generate_sample_code を実行
                result = await session.call_tool(
                    "generate_sample_code",
                    arguments={
                        "endpoint_name": "eq-master",
                        "language": "python",
                    },
                )

                # レスポンスの検証
                assert len(result.content) > 0
                assert result.content[0].type == "text"

                code = result.content[0].text

                # コードの検証
                assert isinstance(code, str)
                assert len(code) > 0
                assert "import httpx" in code or "def " in code

    @pytest.mark.asyncio
    async def test_full_workflow_search_describe_codegen(self):
        """完全なワークフロー: search → describe → codegen を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 1. search_endpoints でエンドポイントを検索
                search_result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": "equities"},
                )

                search_data = json.loads(search_result.content[0].text)
                assert search_data["count"] > 0

                # 最初の結果のエンドポイント名を取得
                endpoint_name = search_data["results"][0]["name"]

                # 2. describe_endpoint で詳細を取得
                describe_result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": endpoint_name},
                )

                describe_data = json.loads(describe_result.content[0].text)
                assert describe_data["name"] == endpoint_name

                # 3. generate_sample_code でコード生成
                codegen_result = await session.call_tool(
                    "generate_sample_code",
                    arguments={
                        "endpoint_name": endpoint_name,
                        "language": "python",
                    },
                )

                code = codegen_result.content[0].text
                assert isinstance(code, str)
                assert len(code) > 0


class TestMCPClientErrorHandling:
    """MCPクライアント経由でのエラーハンドリングE2Eテスト。"""

    @pytest.mark.asyncio
    async def test_validation_error_response_format(self):
        """バリデーションエラー時のレスポンス形式を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 空のキーワードで search_endpoints を実行
                result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": ""},
                )

                # レスポンスの検証
                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エラー情報の検証
                assert text_data["error"] is True
                assert text_data["error_type"] == "ValidationError"
                assert "message" in text_data
                assert "details" in text_data

    @pytest.mark.asyncio
    async def test_not_found_error_response_format(self):
        """未検出エラー時のレスポンス形式を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 存在しないエンドポイント名で describe_endpoint を実行
                result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": "nonexistent_endpoint"},
                )

                # レスポンスの検証
                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エラー情報の検証
                assert text_data["error"] is True
                assert text_data["error_type"] == "NotFoundError"
                assert "message" in text_data
                assert "nonexistent_endpoint" in text_data["message"]

    @pytest.mark.asyncio
    async def test_unsupported_language_error(self):
        """サポートされていない言語指定時のエラーを確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # サポートされていない言語で generate_sample_code を実行
                result = await session.call_tool(
                    "generate_sample_code",
                    arguments={
                        "endpoint_name": "eq-master",
                        "language": "javascript",
                    },
                )

                # レスポンスの検証
                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エラー情報の検証
                assert text_data["error"] is True
                assert text_data["error_type"] == "ValidationError"
                assert "サポートされていません" in text_data["message"]


class TestNewEndpointsE2E:
    """新規エンドポイント用の統合E2Eテスト。"""

    @pytest.mark.asyncio
    async def test_search_eq_bars_daily_am_endpoint(self):
        """前場四本値エンドポイントの検索動作を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 前場四本値エンドポイントを検索
                result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": "前場"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # 検索結果に前場四本値が含まれることを確認
                assert text_data["count"] > 0
                endpoint_names = [r["name"] for r in text_data["results"]]
                assert "eq-bars-daily-am" in endpoint_names

    @pytest.mark.asyncio
    async def test_describe_eq_investor_types_endpoint(self):
        """投資部門別情報エンドポイントの詳細取得を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 投資部門別情報エンドポイントの詳細を取得
                result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": "eq-investor-types"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エンドポイント情報の検証
                assert text_data["name"] == "eq-investor-types"
                assert text_data["path"] == "/equities/investor-types"
                assert text_data["method"] == "GET"
                assert "description" in text_data

    @pytest.mark.asyncio
    async def test_describe_drv_bars_daily_opt_225_endpoint(self):
        """日経225オプション四本値エンドポイントの詳細取得を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 日経225オプション四本値エンドポイントの詳細を取得
                result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": "drv-bars-daily-opt-225"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エンドポイント情報の検証
                assert text_data["name"] == "drv-bars-daily-opt-225"
                assert text_data["path"] == "/derivatives/bars/daily/options/225"
                assert text_data["method"] == "GET"
                assert "description" in text_data

    @pytest.mark.asyncio
    async def test_describe_drv_bars_daily_fut_endpoint(self):
        """先物四本値エンドポイントの詳細取得を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 先物四本値エンドポイントの詳細を取得
                result = await session.call_tool(
                    "describe_endpoint",
                    arguments={"endpoint_name": "drv-bars-daily-fut"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # エンドポイント情報の検証
                assert text_data["name"] == "drv-bars-daily-fut"
                assert text_data["path"] == "/derivatives/bars/daily/futures"
                assert text_data["method"] == "GET"
                assert "description" in text_data

    @pytest.mark.asyncio
    async def test_generate_code_for_eq_bars_daily_am(self):
        """前場四本値エンドポイントのコード生成を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 前場四本値エンドポイントのサンプルコードを生成
                result = await session.call_tool(
                    "generate_sample_code",
                    arguments={
                        "endpoint_name": "eq-bars-daily-am",
                        "language": "python",
                    },
                )

                assert len(result.content) > 0
                code = result.content[0].text

                # コードの基本的な検証
                assert isinstance(code, str)
                assert len(code) > 0
                assert "eq-bars-daily-am" in code or "/equities/bars/daily/am" in code

    @pytest.mark.asyncio
    async def test_generate_code_for_drv_bars_daily_opt_225(self):
        """日経225オプション四本値エンドポイントのコード生成を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 日経225オプション四本値エンドポイントのサンプルコードを生成
                result = await session.call_tool(
                    "generate_sample_code",
                    arguments={
                        "endpoint_name": "drv-bars-daily-opt-225",
                        "language": "python",
                    },
                )

                assert len(result.content) > 0
                code = result.content[0].text

                # コードの基本的な検証
                assert isinstance(code, str)
                assert len(code) > 0
                assert (
                    "drv-bars-daily-opt-225" in code
                    or "/derivatives/bars/daily/options/225" in code
                )

    @pytest.mark.asyncio
    async def test_search_market_endpoints(self):
        """市場関連エンドポイントの検索を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # 市場関連エンドポイントを検索
                result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": "markets"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # 検索結果に複数の市場関連エンドポイントが含まれることを確認
                assert text_data["count"] >= 6
                endpoint_names = [r["name"] for r in text_data["results"]]

                # 期待される市場関連エンドポイント
                expected_market_endpoints = [
                    "mkt-margin-int",
                    "mkt-short-ratio",
                    "mkt-short-sale",
                    "mkt-margin-alert",
                    "mkt-breakdown",
                    "mkt-cal",
                ]

                # 少なくとも一部の市場関連エンドポイントが検索結果に含まれることを確認
                found_count = sum(
                    1 for ep in expected_market_endpoints if ep in endpoint_names
                )
                assert (
                    found_count >= 3
                ), f"Expected at least 3 market endpoints, found {found_count}"

    @pytest.mark.asyncio
    async def test_search_derivatives_endpoints(self):
        """デリバティブ関連エンドポイントの検索を確認。"""
        server_params = StdioServerParameters(
            command="uv",
            args=["run", "j-quants-doc-mcp"],
        )

        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # デリバティブ関連エンドポイントを検索
                result = await session.call_tool(
                    "search_endpoints",
                    arguments={"keyword": "先物"},
                )

                assert len(result.content) > 0
                text_data = json.loads(result.content[0].text)

                # 検索結果にデリバティブ関連エンドポイントが含まれることを確認
                assert text_data["count"] > 0
                endpoint_names = [r["name"] for r in text_data["results"]]

                # 期待されるデリバティブ関連エンドポイント
                expected_derivatives = ["drv-bars-daily-fut", "drv-bars-daily-opt-225"]

                # 少なくとも1つのデリバティブエンドポイントが検索結果に含まれることを確認
                found_count = sum(
                    1 for ep in expected_derivatives if ep in endpoint_names
                )
                assert (
                    found_count >= 1
                ), f"Expected at least 1 derivatives endpoint, found {found_count}"
