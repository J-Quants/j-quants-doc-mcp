"""Tests for lookup_property tool."""

from j_quants_doc_mcp.tools.lookup import lookup_property


def test_lookup_property_found_market_code():
    """市場コード(Mkt)の参照データが見つかることを確認"""
    result = lookup_property("Mkt")

    assert result["found"] is True
    assert result["property_name"] == "Mkt"
    assert result["property_exists"] is True
    assert result["reference_data"]["name"] == "market_codes"


def test_lookup_property_found_sector17():
    """17業種コード(S17)の参照データが見つかることを確認"""
    result = lookup_property("S17")

    assert result["found"] is True
    assert result["property_name"] == "S17"
    assert result["reference_data"]["name"] == "sector17_codes"


def test_lookup_property_found_sector33():
    """33業種コード(S33)の参照データが見つかることを確認"""
    result = lookup_property("S33")

    assert result["found"] is True
    assert result["property_name"] == "S33"
    assert result["reference_data"]["name"] == "sector33_codes"


def test_lookup_property_found_holiday_division():
    """休日区分(HolDiv)の参照データが見つかることを確認"""
    result = lookup_property("HolDiv")

    assert result["found"] is True
    assert result["property_name"] == "HolDiv"
    assert result["reference_data"]["name"] == "holiday_division"


def test_lookup_property_found_product_category():
    """商品区分(ProdCat)の参照データが見つかることを確認"""
    result = lookup_property("ProdCat")

    assert result["found"] is True
    assert result["property_name"] == "ProdCat"
    assert result["reference_data"]["name"] in [
        "futures_product_codes",
        "option_product_codes",
    ]


def test_lookup_property_case_insensitive():
    """大文字小文字を区別しない検索ができることを確認"""
    result_lower = lookup_property("mkt")
    result_upper = lookup_property("MKT")
    result_mixed = lookup_property("Mkt")

    assert result_lower["found"] is True
    assert result_upper["found"] is True
    assert result_mixed["found"] is True


def test_lookup_property_not_found_no_reference_data():
    """参照データがないプロパティの場合、自由値として扱われることを確認"""
    # Dateはエンドポイントに存在するが参照データには紐づいていない
    result = lookup_property("Date")

    assert result["found"] is False
    assert result["property_name"] == "Date"
    assert result["property_exists"] is True
    assert result["reference_data"] is None
    assert "自由に値を格納できます" in result["message"]


def test_lookup_property_not_exist():
    """存在しないプロパティ名の場合、property_existsがFalseになることを確認"""
    result = lookup_property("NonExistentProperty12345")

    assert result["found"] is False
    assert result["property_name"] == "NonExistentProperty12345"
    assert result["property_exists"] is False
    assert result["reference_data"] is None
    assert "存在しないパラメータです" in result["message"]


def test_lookup_property_returns_values():
    """参照データが見つかった場合、valuesが含まれることを確認"""
    result = lookup_property("Mkt")

    assert result["found"] is True
    assert result["reference_data"] is not None
    assert "values" in result["reference_data"]
    assert len(result["reference_data"]["values"]) > 0


def test_lookup_property_returns_direction():
    """参照データにdirectionが含まれることを確認"""
    result = lookup_property("hol_div")

    assert result["found"] is True
    assert result["reference_data"] is not None
    assert "direction" in result["reference_data"]
    assert result["reference_data"]["direction"] in ["request", "response"]


def test_lookup_property_doc_type():
    """開示書類種別(DocType)の参照データが見つかることを確認"""
    result = lookup_property("DocType")

    assert result["found"] is True
    assert result["property_name"] == "DocType"
    assert result["reference_data"]["name"] == "disclosure_document_types"


def test_lookup_property_tse_margin_reg():
    """東証信用貸借規制区分(TSEMrgnRegCls)の参照データが見つかることを確認"""
    result = lookup_property("TSEMrgnRegCls")

    assert result["found"] is True
    assert result["reference_data"]["name"] == "margin_regulation_codes"


# endpoint_name パラメータのテスト


def test_lookup_property_with_endpoint_name_found():
    """endpoint_name指定時、該当エンドポイントにプロパティが存在する場合"""
    result = lookup_property("Mkt", endpoint_name="eq-master")

    assert result["found"] is True
    assert result["property_name"] == "Mkt"
    assert result["endpoint_name"] == "eq-master"
    assert result["property_exists"] is True
    assert result["reference_data"]["name"] == "market_codes"


def test_lookup_property_with_endpoint_name_not_exist():
    """endpoint_name指定時、該当エンドポイントにプロパティが存在しない場合"""
    result = lookup_property("Mkt", endpoint_name="mkt-cal")

    assert result["found"] is False
    assert result["property_name"] == "Mkt"
    assert result["endpoint_name"] == "mkt-cal"
    assert result["property_exists"] is False
    assert result["reference_data"] is None
    assert "存在しないパラメータです" in result["message"]


def test_lookup_property_with_endpoint_name_free_value():
    """endpoint_name指定時、プロパティは存在するが参照データがない場合"""
    result = lookup_property("Date", endpoint_name="eq-master")

    assert result["found"] is False
    assert result["property_name"] == "Date"
    assert result["endpoint_name"] == "eq-master"
    assert result["property_exists"] is True
    assert result["reference_data"] is None
    assert "自由に値を格納できます" in result["message"]


def test_lookup_property_with_endpoint_name_response_field():
    """endpoint_name指定時、レスポンスフィールドも検索対象になることを確認"""
    result = lookup_property("HolDiv", endpoint_name="mkt-cal")

    assert result["found"] is True
    assert result["property_name"] == "HolDiv"
    assert result["endpoint_name"] == "mkt-cal"
    assert result["property_exists"] is True
    assert result["reference_data"]["name"] == "holiday_division"
