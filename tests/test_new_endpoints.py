"""新規追加エンドポイントのユニットテスト

フェーズ2-4で追加されたエンドポイントの動作確認テスト:
- 前場四本値 (/equities/bars/daily/am)
- 市場情報関連エンドポイント
- デリバティブ関連エンドポイント
"""

from j_quants_doc_mcp.resources.specifications import load_endpoints


class TestNewEndpointsDataIntegrity:
    """新規エンドポイントのデータ整合性テスト"""

    def test_eq_bars_daily_am_endpoint_exists(self):
        """前場四本値エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        eq_bars_daily_am = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-daily-am"), None
        )

        assert eq_bars_daily_am is not None
        assert eq_bars_daily_am.path == "/equities/bars/daily/am"
        assert eq_bars_daily_am.method == "GET"
        assert eq_bars_daily_am.description
        assert eq_bars_daily_am.auth_required is True

    def test_eq_investor_types_endpoint_exists(self):
        """投資部門別情報エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        eq_investor_types = next(
            (e for e in endpoints.endpoints if e.name == "eq-investor-types"), None
        )

        assert eq_investor_types is not None
        assert eq_investor_types.path == "/equities/investor-types"
        assert eq_investor_types.method == "GET"
        assert eq_investor_types.description
        assert eq_investor_types.auth_required is True

    def test_mkt_margin_int_endpoint_exists(self):
        """信用取引週末残高エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        mkt_margin_int = next(
            (e for e in endpoints.endpoints if e.name == "mkt-margin-int"),
            None,
        )

        assert mkt_margin_int is not None
        assert mkt_margin_int.path == "/markets/margin-interest"
        assert mkt_margin_int.method == "GET"
        assert mkt_margin_int.description
        assert mkt_margin_int.auth_required is True

    def test_mkt_short_ratio_endpoint_exists(self):
        """業種別空売り比率エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        mkt_short_ratio = next(
            (e for e in endpoints.endpoints if e.name == "mkt-short-ratio"), None
        )

        assert mkt_short_ratio is not None
        assert mkt_short_ratio.path == "/markets/short-ratio"
        assert mkt_short_ratio.method == "GET"
        assert mkt_short_ratio.description
        assert mkt_short_ratio.auth_required is True

    def test_mkt_short_sale_endpoint_exists(self):
        """空売り残高報告エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        mkt_short_sale = next(
            (e for e in endpoints.endpoints if e.name == "mkt-short-sale"),
            None,
        )

        assert mkt_short_sale is not None
        assert mkt_short_sale.path == "/markets/short-sale-report"
        assert mkt_short_sale.method == "GET"
        assert mkt_short_sale.description
        assert mkt_short_sale.auth_required is True

    def test_mkt_margin_alert_endpoint_exists(self):
        """日々公表信用取引残高エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        mkt_margin_alert = next(
            (e for e in endpoints.endpoints if e.name == "mkt-margin-alert"),
            None,
        )

        assert mkt_margin_alert is not None
        assert mkt_margin_alert.path == "/markets/margin-alert"
        assert mkt_margin_alert.method == "GET"
        assert mkt_margin_alert.description
        assert mkt_margin_alert.auth_required is True

    def test_eq_bars_minute_endpoint_exists(self):
        """株価分足エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        eq_bars_minute = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-minute"), None
        )

        assert eq_bars_minute is not None
        assert eq_bars_minute.path == "/equities/bars/minute"
        assert eq_bars_minute.method == "GET"
        assert eq_bars_minute.description
        assert eq_bars_minute.auth_required is True

    def test_bulk_list_endpoint_exists(self):
        """/bulk/list エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        bulk_list = next(
            (e for e in endpoints.endpoints if e.name == "bulk-list"), None
        )

        assert bulk_list is not None
        assert bulk_list.path == "/bulk/list"
        assert bulk_list.method == "GET"
        assert bulk_list.description
        assert bulk_list.auth_required is True

    def test_bulk_get_endpoint_exists(self):
        """/bulk/get エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        bulk_get = next((e for e in endpoints.endpoints if e.name == "bulk-get"), None)

        assert bulk_get is not None
        assert bulk_get.path == "/bulk/get"
        assert bulk_get.method == "GET"
        assert bulk_get.description
        assert bulk_get.auth_required is True

    def test_breakdown_endpoint_exists(self):
        """売買内訳データエンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        breakdown = next(
            (e for e in endpoints.endpoints if e.name == "mkt-breakdown"), None
        )

        assert breakdown is not None
        assert breakdown.path == "/markets/breakdown"
        assert breakdown.method == "GET"
        assert breakdown.description
        assert breakdown.auth_required is True

    def test_mkt_cal_endpoint_exists(self):
        """取引カレンダーエンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        mkt_cal = next((e for e in endpoints.endpoints if e.name == "mkt-cal"), None)

        assert mkt_cal is not None
        assert mkt_cal.path == "/markets/calendar"
        assert mkt_cal.method == "GET"
        assert mkt_cal.description
        assert mkt_cal.auth_required is True

    def test_idx_bars_daily_endpoint_exists(self):
        """指数四本値エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        idx_bars_daily = next(
            (e for e in endpoints.endpoints if e.name == "idx-bars-daily"), None
        )

        assert idx_bars_daily is not None
        assert idx_bars_daily.path == "/indices/bars/daily"
        assert idx_bars_daily.method == "GET"
        assert idx_bars_daily.description
        assert idx_bars_daily.auth_required is True

    def test_idx_bars_daily_topix_endpoint_exists(self):
        """TOPIX指数四本値エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        idx_bars_daily_topix = next(
            (e for e in endpoints.endpoints if e.name == "idx-bars-daily-topix"), None
        )

        assert idx_bars_daily_topix is not None
        assert idx_bars_daily_topix.path == "/indices/bars/daily/topix"
        assert idx_bars_daily_topix.method == "GET"
        assert idx_bars_daily_topix.description
        assert idx_bars_daily_topix.auth_required is True

    def test_fin_details_endpoint_exists(self):
        """貸借対照表・損益計算書エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        fin_details = next(
            (e for e in endpoints.endpoints if e.name == "fin-details"), None
        )

        assert fin_details is not None
        assert fin_details.path == "/fins/details"
        assert fin_details.method == "GET"
        assert fin_details.description
        assert fin_details.auth_required is True

    def test_fin_dividend_endpoint_exists(self):
        """配当情報エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        fin_dividend = next(
            (e for e in endpoints.endpoints if e.name == "fin-dividend"), None
        )

        assert fin_dividend is not None
        assert fin_dividend.path == "/fins/dividend"
        assert fin_dividend.method == "GET"
        assert fin_dividend.description
        assert fin_dividend.auth_required is True

    def test_eq_earnings_cal_endpoint_exists(self):
        """決算発表予定エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        eq_earnings_cal = next(
            (e for e in endpoints.endpoints if e.name == "eq-earnings-cal"), None
        )

        assert eq_earnings_cal is not None
        assert eq_earnings_cal.path == "/equities/earnings-calendar"
        assert eq_earnings_cal.method == "GET"
        assert eq_earnings_cal.description
        assert eq_earnings_cal.auth_required is True

    def test_drv_bars_daily_opt_225_endpoint_exists(self):
        """日経225オプション四本値エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        drv_bars_daily_opt_225 = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-opt-225"), None
        )

        assert drv_bars_daily_opt_225 is not None
        assert drv_bars_daily_opt_225.path == "/derivatives/bars/daily/options/225"
        assert drv_bars_daily_opt_225.method == "GET"
        assert drv_bars_daily_opt_225.description
        assert drv_bars_daily_opt_225.auth_required is True

    def test_drv_bars_daily_fut_endpoint_exists(self):
        """先物四本値エンドポイントが存在することを確認"""
        endpoints = load_endpoints()
        drv_bars_daily_fut = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-fut"), None
        )

        assert drv_bars_daily_fut is not None
        assert drv_bars_daily_fut.path == "/derivatives/bars/daily/futures"
        assert drv_bars_daily_fut.method == "GET"
        assert drv_bars_daily_fut.description
        assert drv_bars_daily_fut.auth_required is True


class TestNewEndpointsParameters:
    """新規エンドポイントのパラメータ検証テスト"""

    def test_eq_bars_daily_am_parameters(self):
        """前場四本値エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        eq_bars_daily_am = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-daily-am"), None
        )

        assert eq_bars_daily_am is not None
        param_names = [p.name for p in eq_bars_daily_am.parameters]

        # 期待されるパラメータの存在確認
        assert "code" in param_names

        # パラメータの詳細検証
        for param in eq_bars_daily_am.parameters:
            assert param.type
            assert param.location in ["query", "body", "header", "path"]
            assert isinstance(param.required, bool)

    def test_eq_investor_types_parameters(self):
        """投資部門別情報エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        eq_investor_types = next(
            (e for e in endpoints.endpoints if e.name == "eq-investor-types"), None
        )

        assert eq_investor_types is not None
        param_names = [p.name for p in eq_investor_types.parameters]

        # 基本的なパラメータの存在確認
        assert len(param_names) > 0

        # パラメータの詳細検証
        for param in eq_investor_types.parameters:
            assert param.type
            assert param.location in ["query", "body", "header", "path"]
            assert isinstance(param.required, bool)

    def test_drv_bars_daily_opt_225_parameters(self):
        """日経225オプション四本値エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        drv_bars_daily_opt_225 = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-opt-225"), None
        )

        assert drv_bars_daily_opt_225 is not None
        param_names = [p.name for p in drv_bars_daily_opt_225.parameters]

        # 基本的なパラメータの存在確認
        assert len(param_names) > 0

        # パラメータの詳細検証
        for param in drv_bars_daily_opt_225.parameters:
            assert param.type
            assert param.location in ["query", "body", "header", "path"]
            assert isinstance(param.required, bool)

    def test_drv_bars_daily_fut_parameters(self):
        """先物四本値エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        drv_bars_daily_fut = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-fut"), None
        )

        assert drv_bars_daily_fut is not None
        param_names = [p.name for p in drv_bars_daily_fut.parameters]

        # 基本的なパラメータの存在確認
        assert len(param_names) > 0

        # パラメータの詳細検証
        for param in drv_bars_daily_fut.parameters:
            assert param.type
            assert param.location in ["query", "body", "header", "path"]
            assert isinstance(param.required, bool)

    def test_eq_bars_minute_parameters(self):
        """株価分足エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        eq_bars_minute = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-minute"), None
        )

        assert eq_bars_minute is not None
        param_names = [p.name for p in eq_bars_minute.parameters]

        # 期待されるパラメータの存在確認
        for expected in ["code", "date", "from", "to", "pagination_key"]:
            assert expected in param_names

        # パラメータの詳細検証
        for param in eq_bars_minute.parameters:
            assert param.type
            assert param.location in ["query", "body", "header", "path"]
            assert isinstance(param.required, bool)

    def test_bulk_list_parameters(self):
        """/bulk/list エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        bulk_list = next(
            (e for e in endpoints.endpoints if e.name == "bulk-list"), None
        )

        assert bulk_list is not None
        assert len(bulk_list.parameters) == 1
        param = bulk_list.parameters[0]
        assert param.name == "endpoint"
        assert param.type == "String"
        assert param.location == "query"
        assert param.required is True

    def test_bulk_get_parameters(self):
        """/bulk/get エンドポイントのパラメータを検証"""
        endpoints = load_endpoints()
        bulk_get = next((e for e in endpoints.endpoints if e.name == "bulk-get"), None)

        assert bulk_get is not None
        assert len(bulk_get.parameters) == 1
        param = bulk_get.parameters[0]
        assert param.name == "key"
        assert param.type == "String"
        assert param.location == "query"
        assert param.required is True


class TestNewEndpointsResponse:
    """新規エンドポイントのレスポンス構造検証テスト"""

    def test_eq_bars_daily_am_response_structure(self):
        """前場四本値エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        eq_bars_daily_am = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-daily-am"), None
        )

        assert eq_bars_daily_am is not None
        assert eq_bars_daily_am.response
        assert eq_bars_daily_am.response.description
        assert len(eq_bars_daily_am.response.fields) > 0

        # レスポンスフィールドの検証
        field_names = [f.name for f in eq_bars_daily_am.response.fields]
        assert len(field_names) > 0

    def test_eq_investor_types_response_structure(self):
        """投資部門別情報エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        eq_investor_types = next(
            (e for e in endpoints.endpoints if e.name == "eq-investor-types"), None
        )

        assert eq_investor_types is not None
        assert eq_investor_types.response
        assert eq_investor_types.response.description
        assert len(eq_investor_types.response.fields) > 0

    def test_drv_bars_daily_opt_225_response_structure(self):
        """日経225オプション四本値エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        drv_bars_daily_opt_225 = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-opt-225"), None
        )

        assert drv_bars_daily_opt_225 is not None
        assert drv_bars_daily_opt_225.response
        assert drv_bars_daily_opt_225.response.description
        assert len(drv_bars_daily_opt_225.response.fields) > 0

    def test_drv_bars_daily_fut_response_structure(self):
        """先物四本値エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        drv_bars_daily_fut = next(
            (e for e in endpoints.endpoints if e.name == "drv-bars-daily-fut"), None
        )

        assert drv_bars_daily_fut is not None
        assert drv_bars_daily_fut.response
        assert drv_bars_daily_fut.response.description
        assert len(drv_bars_daily_fut.response.fields) > 0

    def test_eq_bars_minute_response_structure(self):
        """株価分足エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        eq_bars_minute = next(
            (e for e in endpoints.endpoints if e.name == "eq-bars-minute"), None
        )

        assert eq_bars_minute is not None
        assert eq_bars_minute.response
        assert eq_bars_minute.response.description
        assert len(eq_bars_minute.response.fields) > 0

        field_names = [f.name for f in eq_bars_minute.response.fields]
        for expected in ["Date", "Time", "Code", "O", "H", "L", "C", "Vo", "Va"]:
            assert expected in field_names

    def test_bulk_list_response_structure(self):
        """/bulk/list エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        bulk_list = next(
            (e for e in endpoints.endpoints if e.name == "bulk-list"), None
        )

        assert bulk_list is not None
        assert bulk_list.response
        assert bulk_list.response.description
        assert len(bulk_list.response.fields) > 0

        field_names = [f.name for f in bulk_list.response.fields]
        for expected in ["Key", "LastModified", "Size"]:
            assert expected in field_names

    def test_bulk_get_response_structure(self):
        """/bulk/get エンドポイントのレスポンス構造を検証"""
        endpoints = load_endpoints()
        bulk_get = next((e for e in endpoints.endpoints if e.name == "bulk-get"), None)

        assert bulk_get is not None
        assert bulk_get.response
        assert bulk_get.response.description
        assert len(bulk_get.response.fields) > 0

        field_names = [f.name for f in bulk_get.response.fields]
        assert "url" in field_names


class TestAllEndpointsCount:
    """全エンドポイント数の確認テスト"""

    def test_total_endpoints_count(self):
        """主要エンドポイントが定義されていることを確認"""
        endpoints = load_endpoints()

        # 期待される全エンドポイント名のリスト
        expected_endpoints = [
            "eq-master",
            "eq-bars-daily",
            "fin-summary",
            "eq-bars-daily-am",
            "eq-investor-types",
            "mkt-margin-int",
            "mkt-short-ratio",
            "mkt-short-sale",
            "mkt-margin-alert",
            "mkt-breakdown",
            "mkt-cal",
            "idx-bars-daily",
            "idx-bars-daily-topix",
            "fin-details",
            "fin-dividend",
            "eq-earnings-cal",
            "drv-bars-daily-opt-225",
            "drv-bars-daily-fut",
            "eq-bars-minute",
            "bulk-list",
            "bulk-get",
        ]

        endpoint_names = [e.name for e in endpoints.endpoints]

        # 全てのエンドポイントが存在することを確認
        for expected in expected_endpoints:
            assert (
                expected in endpoint_names
            ), f"Expected endpoint '{expected}' not found"

        # エンドポイント数の確認
        assert len(endpoints.endpoints) >= len(
            expected_endpoints
        ), f"Expected at least {len(expected_endpoints)} endpoints, found {len(endpoints.endpoints)}"

    def test_endpoint_categories(self):
        """エンドポイントがカテゴリごとに正しく分類されていることを確認"""
        endpoints = load_endpoints()

        # カテゴリごとのエンドポイント数を確認
        equities_endpoints = [
            e for e in endpoints.endpoints if e.path.startswith("/equities/")
        ]
        markets_endpoints = [
            e for e in endpoints.endpoints if e.path.startswith("/markets/")
        ]
        indices_endpoints = [
            e for e in endpoints.endpoints if e.path.startswith("/indices")
        ]
        fins_endpoints = [e for e in endpoints.endpoints if e.path.startswith("/fins/")]
        derivatives_endpoints = [
            e for e in endpoints.endpoints if e.path.startswith("/derivatives/")
        ]

        # 各カテゴリにエンドポイントが存在することを確認
        assert len(equities_endpoints) >= 3, "株式系エンドポイントが不足"
        assert len(markets_endpoints) >= 6, "市場情報系エンドポイントが不足"
        assert len(indices_endpoints) >= 2, "指数系エンドポイントが不足"
        assert len(fins_endpoints) >= 3, "財務系エンドポイントが不足"
        assert len(derivatives_endpoints) >= 2, "デリバティブ系エンドポイントが不足"
