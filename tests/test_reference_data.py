"""Tests for reference data (market codes, sector codes, index codes)."""

from j_quants_doc_mcp.resources.specifications import load_reference_data


def test_load_reference_data():
    """参照データを正常に読み込めることを確認"""
    data = load_reference_data()

    assert "reference_data" in data
    assert len(data["reference_data"]) == 11

    names = [cm["name"] for cm in data["reference_data"]]
    # 基本参照データ
    assert "market_codes" in names
    assert "market_names" in names
    assert "sector17_codes" in names
    assert "sector33_codes" in names
    assert "index_codes" in names
    # 先物・オプション
    assert "futures_product_codes" in names
    assert "option_product_codes" in names
    # 開示・カレンダー・規制
    assert "disclosure_document_types" in names
    assert "holiday_division" in names
    assert "margin_regulation_codes" in names
    assert "publication_reasons" in names


def test_market_codes_structure():
    """市場区分コードの構造を確認"""
    data = load_reference_data()
    market_codes = next(
        cm for cm in data["reference_data"] if cm["name"] == "market_codes"
    )

    assert market_codes["name"] == "market_codes"
    assert "description" in market_codes
    assert "fields" in market_codes
    assert "related_properties" in market_codes
    assert "reference_data" in market_codes

    # フィールドの確認
    field_names = [f["name"] for f in market_codes["fields"]]
    assert "MarketCode" in field_names
    assert "MarketCodeName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in market_codes["related_properties"]]
    assert "eq-master" in endpoints

    # 参照データの確認
    assert len(market_codes["reference_data"]) > 0
    first_item = market_codes["reference_data"][0]
    assert "MarketCode" in first_item
    assert "MarketCodeName" in first_item


def test_sector17_codes_structure():
    """17業種コードの構造を確認"""
    data = load_reference_data()
    sector17 = next(
        cm for cm in data["reference_data"] if cm["name"] == "sector17_codes"
    )

    assert sector17["name"] == "sector17_codes"
    assert "description" in sector17

    # フィールドの確認
    field_names = [f["name"] for f in sector17["fields"]]
    assert "Sector17Code" in field_names
    assert "Sector17CodeName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in sector17["related_properties"]]
    assert "eq-master" in endpoints

    # 参照データの確認（18業種: 1-17 + 99）
    assert len(sector17["reference_data"]) == 18


def test_sector33_codes_structure():
    """33業種コードの構造を確認"""
    data = load_reference_data()
    sector33 = next(
        cm for cm in data["reference_data"] if cm["name"] == "sector33_codes"
    )

    assert sector33["name"] == "sector33_codes"
    assert "description" in sector33

    # フィールドの確認
    field_names = [f["name"] for f in sector33["fields"]]
    assert "Sector33Code" in field_names
    assert "Sector33CodeName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in sector33["related_properties"]]
    assert "eq-master" in endpoints

    # 参照データの確認（34業種）
    assert len(sector33["reference_data"]) == 34


def test_index_codes_structure():
    """指数コードの構造を確認"""
    data = load_reference_data()
    index_codes = next(
        cm for cm in data["reference_data"] if cm["name"] == "index_codes"
    )

    assert index_codes["name"] == "index_codes"
    assert "description" in index_codes

    # フィールドの確認
    field_names = [f["name"] for f in index_codes["fields"]]
    assert "Code" in field_names
    assert "IndexName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in index_codes["related_properties"]]
    assert "idx-bars-daily" in endpoints

    # 参照データの確認
    assert len(index_codes["reference_data"]) > 0
    # TOPIXが存在することを確認
    index_names = [item["IndexName"] for item in index_codes["reference_data"]]
    assert "TOPIX" in index_names


def test_futures_product_codes_structure():
    """先物商品区分コードの構造を確認"""
    data = load_reference_data()
    futures = next(
        cm for cm in data["reference_data"] if cm["name"] == "futures_product_codes"
    )

    assert futures["name"] == "futures_product_codes"
    assert "description" in futures

    # フィールドの確認
    field_names = [f["name"] for f in futures["fields"]]
    assert "ProductCode" in field_names
    assert "ProductName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in futures["related_properties"]]
    assert "drv-bars-daily-futures" in endpoints

    # 参照データの確認（13種類）
    assert len(futures["reference_data"]) == 13
    # 日経225先物が存在することを確認
    product_names = [item["ProductName"] for item in futures["reference_data"]]
    assert "日経225先物" in product_names


def test_option_product_codes_structure():
    """オプション商品区分コードの構造を確認"""
    data = load_reference_data()
    options = next(
        cm for cm in data["reference_data"] if cm["name"] == "option_product_codes"
    )

    assert options["name"] == "option_product_codes"
    assert "description" in options

    # フィールドの確認
    field_names = [f["name"] for f in options["fields"]]
    assert "ProductCode" in field_names
    assert "ProductName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in options["related_properties"]]
    assert "drv-bars-daily-opt" in endpoints

    # 参照データの確認（5種類）
    assert len(options["reference_data"]) == 5
    # 日経225オプションが存在することを確認
    product_names = [item["ProductName"] for item in options["reference_data"]]
    assert "日経225オプション" in product_names


def test_disclosure_document_types_structure():
    """開示書類種別の構造を確認"""
    data = load_reference_data()
    disclosure = next(
        cm for cm in data["reference_data"] if cm["name"] == "disclosure_document_types"
    )

    assert disclosure["name"] == "disclosure_document_types"
    assert "description" in disclosure

    # フィールドの確認
    field_names = [f["name"] for f in disclosure["fields"]]
    assert "DocumentType" in field_names
    assert "DocumentTypeJP" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in disclosure["related_properties"]]
    assert "fin-summary" in endpoints

    # 参照データの確認（45種類）
    assert len(disclosure["reference_data"]) == 45
    # 決算短信（連結・日本基準）が存在することを確認
    doc_types = [item["DocumentType"] for item in disclosure["reference_data"]]
    assert "FYFinancialStatements_Consolidated_JP" in doc_types


def test_holiday_division_structure():
    """休日区分の構造を確認"""
    data = load_reference_data()
    holiday = next(
        cm for cm in data["reference_data"] if cm["name"] == "holiday_division"
    )

    assert holiday["name"] == "holiday_division"
    assert "description" in holiday

    # フィールドの確認
    field_names = [f["name"] for f in holiday["fields"]]
    assert "HolidayCode" in field_names
    assert "HolidayName" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in holiday["related_properties"]]
    assert "mkt-cal" in endpoints

    # 参照データの確認（4種類: 0-3）
    assert len(holiday["reference_data"]) == 4
    # 営業日が存在することを確認
    holiday_names = [item["HolidayName"] for item in holiday["reference_data"]]
    assert "営業日" in holiday_names


def test_margin_regulation_codes_structure():
    """東証信用貸借規制区分の構造を確認"""
    data = load_reference_data()
    margin = next(
        cm for cm in data["reference_data"] if cm["name"] == "margin_regulation_codes"
    )

    assert margin["name"] == "margin_regulation_codes"
    assert "description" in margin

    # フィールドの確認
    field_names = [f["name"] for f in margin["fields"]]
    assert "RegulationCode" in field_names
    assert "RegulationDescription" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in margin["related_properties"]]
    assert "mkt-margin-alert" in endpoints

    # 参照データの確認（8種類）
    assert len(margin["reference_data"]) == 8
    # 規制コード001が存在することを確認
    codes = [item["RegulationCode"] for item in margin["reference_data"]]
    assert "001" in codes


def test_publication_reasons_structure():
    """公表の理由の構造を確認"""
    data = load_reference_data()
    publication = next(
        cm for cm in data["reference_data"] if cm["name"] == "publication_reasons"
    )

    assert publication["name"] == "publication_reasons"
    assert "description" in publication

    # フィールドの確認
    field_names = [f["name"] for f in publication["fields"]]
    assert "FlagName" in field_names
    assert "FlagDescription" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in publication["related_properties"]]
    assert "mkt-margin-alert" in endpoints

    # 参照データの確認（6種類）
    assert len(publication["reference_data"]) == 6
    # Restrictedフラグが存在することを確認
    flag_names = [item["FlagName"] for item in publication["reference_data"]]
    assert "Restricted" in flag_names


def test_market_names_structure():
    """市場名の構造を確認"""
    data = load_reference_data()
    market_names = next(
        cm for cm in data["reference_data"] if cm["name"] == "market_names"
    )

    assert market_names["name"] == "market_names"
    assert "description" in market_names

    # フィールドの確認
    field_names = [f["name"] for f in market_names["fields"]]
    assert "MarketName" in field_names
    assert "MarketNameJP" in field_names

    # 関連プロパティの確認
    endpoints = [rp["endpoint"] for rp in market_names["related_properties"]]
    assert "eq-investor-types" in endpoints

    # 参照データの確認（8種類）
    assert len(market_names["reference_data"]) == 8
    # プライム市場が存在することを確認
    names = [item["MarketName"] for item in market_names["reference_data"]]
    assert "TSEPrime" in names
