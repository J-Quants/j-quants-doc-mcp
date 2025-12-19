"""Tests for describe_endpoint tool."""

from j_quants_doc_mcp.server import describe_endpoint


def test_describe_eq_master():
    """eq-masterエンドポイントの詳細情報を取得できることを確認"""
    result = describe_endpoint("eq-master")

    assert result["name"] == "eq-master"
    assert result["path"] == "/equities/master"
    assert result["method"] == "GET"
    assert result["auth_required"] is True

    # 日本語名・英語名の確認
    assert result["name_ja"] == "上場銘柄一覧"
    assert result["name_en"] == "Listed Issue Information"

    # 任意パラメータの確認
    optional_param_names = [p["name"] for p in result["parameters"]["optional"]]
    assert "code" in optional_param_names
    assert "date" in optional_param_names

    # レスポンスフィールドの確認
    response_field_names = [f["name"] for f in result["response"]["fields"]]
    assert "Code" in response_field_names
    assert "CoName" in response_field_names

    # レスポンスデータキーの確認
    assert "response_data_key" in result
    assert result["response_data_key"] == "data"

    # プラン情報の確認
    assert "plan" in result
    assert isinstance(result["plan"], list)
    assert "Free" in result["plan"]


def test_describe_eq_bars_daily():
    """eq-bars-dailyエンドポイントの詳細情報を取得できることを確認"""
    result = describe_endpoint("eq-bars-daily")

    assert result["name"] == "eq-bars-daily"
    assert result["path"] == "/equities/bars/daily"
    assert result["method"] == "GET"
    assert result["auth_required"] is True

    # 任意パラメータの確認(codeとdateはどちらかが必須だが、JSONスキーマではoptional)
    optional_param_names = [p["name"] for p in result["parameters"]["optional"]]
    assert "code" in optional_param_names
    assert "date" in optional_param_names
    assert "from" in optional_param_names
    assert "to" in optional_param_names

    # レスポンスフィールドの確認
    response_field_names = [f["name"] for f in result["response"]["fields"]]
    assert "O" in response_field_names
    assert "H" in response_field_names
    assert "L" in response_field_names
    assert "C" in response_field_names


def test_describe_fin_summary():
    """fin-summaryエンドポイントの詳細情報を取得できることを確認"""
    result = describe_endpoint("fin-summary")

    assert result["name"] == "fin-summary"
    assert result["path"] == "/fins/summary"
    assert result["method"] == "GET"
    assert result["auth_required"] is True

    # 任意パラメータの確認
    optional_param_names = [p["name"] for p in result["parameters"]["optional"]]
    assert "code" in optional_param_names
    assert "date" in optional_param_names

    # レスポンスフィールドの確認
    response_field_names = [f["name"] for f in result["response"]["fields"]]
    assert "Sales" in response_field_names
    assert "OP" in response_field_names
    assert "EPS" in response_field_names


def test_describe_endpoint_not_found():
    """存在しないエンドポイント名でエラーが返ることを確認"""
    result = describe_endpoint("nonexistent_endpoint")

    assert "error" in result
    assert result["error_type"] == "NotFoundError"
    assert "nonexistent_endpoint" in result["message"]


def test_describe_endpoint_empty_string():
    """空文字列のエンドポイント名でエラーが返ることを確認"""
    result = describe_endpoint("")

    assert "error" in result
    # 空文字列はバリデーションエラーになる
    assert result["error_type"] == "ValidationError"


def test_describe_endpoint_data_update_with_notes():
    """data_updateフィールド（留意事項あり）が正しく返却されることを確認"""
    result = describe_endpoint("eq-master")

    assert "data_update" in result
    assert result["data_update"]["frequency"] == "日次"
    assert "17:30" in result["data_update"]["time"]
    assert "notes" in result["data_update"]
    assert len(result["data_update"]["notes"]) > 0


def test_describe_endpoint_data_update_without_notes():
    """data_updateフィールド（留意事項なし）が正しく返却されることを確認"""
    result = describe_endpoint("eq-bars-daily")

    assert "data_update" in result
    assert result["data_update"]["frequency"] == "日次"
    assert result["data_update"]["time"] == "16:30頃"
    assert "notes" not in result["data_update"]


def test_describe_endpoint_data_update_weekly():
    """週次更新のdata_updateフィールドが正しく返却されることを確認"""
    result = describe_endpoint("eq-investor-types")

    assert "data_update" in result
    assert "週次" in result["data_update"]["frequency"]
    assert result["data_update"]["time"] == "18:00頃"
    assert "notes" in result["data_update"]


def test_describe_endpoint_data_update_irregular():
    """不定期更新のdata_updateフィールドが正しく返却されることを確認"""
    result = describe_endpoint("mkt-cal")

    assert "data_update" in result
    assert result["data_update"]["frequency"] == "不定期"
    assert result["data_update"]["time"] == "不定期"
    assert "notes" in result["data_update"]
