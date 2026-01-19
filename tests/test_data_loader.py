"""データローダのユニットテスト"""

import json

import pytest
from j_quants_doc_mcp.models.endpoint import EndpointCollection
from j_quants_doc_mcp.models.pattern import PatternCollection
from j_quants_doc_mcp.resources.specifications import (
    DataLoadError,
    get_data_directory,
    load_endpoints,
    load_patterns,
)


class TestDataLoader:
    """データローダのテストクラス"""

    def test_get_data_directory(self):
        """データディレクトリのパス取得テスト"""
        data_dir = get_data_directory()
        assert data_dir.exists()
        assert data_dir.is_dir()
        assert (data_dir / "endpoints.json").exists()
        assert (data_dir / "patterns.json").exists()

    def test_load_endpoints_default_path(self):
        """デフォルトパスでendpoints.jsonを読み込むテスト"""
        result = load_endpoints()
        assert isinstance(result, EndpointCollection)
        assert len(result.endpoints) > 0

        # 最初のエンドポイントの基本的な検証
        first_endpoint = result.endpoints[0]
        assert hasattr(first_endpoint, "name")
        assert hasattr(first_endpoint, "path")
        assert hasattr(first_endpoint, "method")
        assert hasattr(first_endpoint, "description")

    def test_load_patterns_default_path(self):
        """デフォルトパスでpatterns.jsonを読み込むテスト"""
        result = load_patterns()
        assert isinstance(result, PatternCollection)
        assert len(result.patterns) > 0

        # 最初のパターンの基本的な検証
        first_pattern = result.patterns[0]
        assert hasattr(first_pattern, "pattern_name")
        assert hasattr(first_pattern, "description")
        assert hasattr(first_pattern, "related_endpoints")

    def test_load_endpoints_custom_path(self, tmp_path):
        """カスタムパスでendpoints.jsonを読み込むテスト"""
        # テスト用の有効なJSONファイルを作成
        test_file = tmp_path / "test_endpoints.json"
        test_data = {
            "endpoints": [
                {
                    "name": "test_endpoint",
                    "name_ja": "テストエンドポイント",
                    "name_en": "Test Endpoint",
                    "path": "/test",
                    "path_old": "/old/test",
                    "method": "GET",
                    "description": "Test endpoint",
                    "api_available": True,
                    "bulk_available": False,
                    "parameters": [],
                    "response": {
                        "description": "Test response",
                        "fields": [],
                    },
                    "auth_required": True,
                    "response_data_key": "data",
                    "plan": ["Free", "Light", "Standard", "Premium"],
                    "data_update": {
                        "frequency": "日次",
                        "time": "17:00頃",
                    },
                    "parameter_patterns": [],
                }
            ]
        }
        test_file.write_text(json.dumps(test_data, ensure_ascii=False))

        result = load_endpoints(test_file)
        assert isinstance(result, EndpointCollection)
        assert len(result.endpoints) == 1
        assert result.endpoints[0].name == "test_endpoint"

    def test_load_patterns_custom_path(self, tmp_path):
        """カスタムパスでpatterns.jsonを読み込むテスト"""
        # テスト用の有効なJSONファイルを作成
        test_file = tmp_path / "test_patterns.json"
        test_data = {
            "patterns": [
                {
                    "pattern_name": "test_pattern",
                    "description": "Test pattern description",
                    "related_endpoints": ["/test"],
                    "notes": ["note1"],
                }
            ]
        }
        test_file.write_text(json.dumps(test_data, ensure_ascii=False))

        result = load_patterns(test_file)
        assert isinstance(result, PatternCollection)
        assert len(result.patterns) == 1
        assert result.patterns[0].pattern_name == "test_pattern"

    def test_load_endpoints_file_not_found(self, tmp_path):
        """存在しないファイルを読み込む場合のエラーテスト"""
        non_existent_file = tmp_path / "non_existent.json"
        with pytest.raises(DataLoadError, match="not found"):
            load_endpoints(non_existent_file)

    def test_load_patterns_file_not_found(self, tmp_path):
        """存在しないファイルを読み込む場合のエラーテスト"""
        non_existent_file = tmp_path / "non_existent.json"
        with pytest.raises(DataLoadError, match="not found"):
            load_patterns(non_existent_file)

    def test_load_endpoints_invalid_json(self, tmp_path):
        """不正なJSON形式のファイルを読み込む場合のエラーテスト"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        with pytest.raises(DataLoadError, match="Invalid JSON format"):
            load_endpoints(invalid_file)

    def test_load_patterns_invalid_json(self, tmp_path):
        """不正なJSON形式のファイルを読み込む場合のエラーテスト"""
        invalid_file = tmp_path / "invalid.json"
        invalid_file.write_text("{ invalid json }")

        with pytest.raises(DataLoadError, match="Invalid JSON format"):
            load_patterns(invalid_file)

    def test_load_endpoints_validation_error(self, tmp_path):
        """バリデーションエラーが発生する場合のテスト"""
        invalid_data_file = tmp_path / "invalid_data.json"
        # 必須フィールドが欠けているデータ
        invalid_data = {"endpoints": [{"name": "test"}]}  # path, method等が欠けている
        invalid_data_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError, match="Data validation failed"):
            load_endpoints(invalid_data_file)

    def test_load_patterns_validation_error(self, tmp_path):
        """バリデーションエラーが発生する場合のテスト"""
        invalid_data_file = tmp_path / "invalid_data.json"
        # 必須フィールドが欠けているデータ
        invalid_data = {
            "patterns": [{"pattern_name": "test"}]
        }  # descriptionが欠けている
        invalid_data_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError, match="Data validation failed"):
            load_patterns(invalid_data_file)

    def test_endpoints_data_integrity(self):
        """実際のendpoints.jsonのデータ整合性テスト"""
        endpoints = load_endpoints()

        # 各エンドポイントの検証
        for endpoint in endpoints.endpoints:
            # 必須フィールドの存在確認
            assert endpoint.name
            assert endpoint.path
            assert endpoint.method in ["GET", "POST", "PUT", "DELETE", "PATCH"]
            assert endpoint.description

            # パラメータの検証
            for param in endpoint.parameters:
                assert param.name
                assert param.type
                assert param.location in ["query", "body", "header", "path"]
                assert isinstance(param.required, bool)

            # レスポンスの検証
            assert endpoint.response
            assert endpoint.response.description

    def test_patterns_data_integrity(self):
        """実際のpatterns.jsonのデータ整合性テスト"""
        patterns = load_patterns()

        # 各パターンの検証
        for pattern in patterns.patterns:
            # 必須フィールドの存在確認
            assert pattern.pattern_name
            assert pattern.description
            assert isinstance(pattern.related_endpoints, list)
            assert isinstance(pattern.notes, list)

    def test_load_endpoints_type_mismatch(self, tmp_path):
        """型不一致のバリデーションエラーテスト"""
        invalid_file = tmp_path / "type_mismatch.json"
        # auth_requiredがdict(変換不可能な型)
        invalid_data = {
            "endpoints": [
                {
                    "name": "test_endpoint",
                    "name_ja": "テスト",
                    "name_en": "Test",
                    "path": "/test",
                    "path_old": "/old/test",
                    "method": "GET",
                    "description": "Test",
                    "parameters": [],
                    "response": {"description": "Test", "fields": []},
                    "auth_required": {"value": "yes"},  # 型不一致: booleanであるべき
                    "response_data_key": "data",
                    "plan": ["Free"],
                    "data_update": {"frequency": "日次", "time": "17:00"},
                    "parameter_patterns": [],
                }
            ]
        }
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError, match="Data validation failed"):
            load_endpoints(invalid_file)

    def test_load_endpoints_parameter_type_mismatch(self, tmp_path):
        """パラメータの型不一致テスト"""
        invalid_file = tmp_path / "param_type_mismatch.json"
        # requiredがdict(変換不可能な型)
        invalid_data = {
            "endpoints": [
                {
                    "name": "test_endpoint",
                    "name_ja": "テスト",
                    "name_en": "Test",
                    "path": "/test",
                    "path_old": "/old/test",
                    "method": "GET",
                    "description": "Test",
                    "parameters": [
                        {
                            "name": "param1",
                            "type": "String",
                            "required": {"value": True},  # 型不一致: booleanであるべき
                            "description": "Test param",
                            "location": "query",
                        }
                    ],
                    "response": {"description": "Test", "fields": []},
                    "auth_required": True,
                    "response_data_key": "data",
                    "plan": ["Free"],
                    "data_update": {"frequency": "日次", "time": "17:00"},
                    "parameter_patterns": [],
                }
            ]
        }
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError, match="Data validation failed"):
            load_endpoints(invalid_file)

    def test_load_patterns_type_mismatch(self, tmp_path):
        """パターンの型不一致テスト"""
        invalid_file = tmp_path / "pattern_type_mismatch.json"
        # related_endpointsがlistではなくstring
        invalid_data = {
            "patterns": [
                {
                    "pattern_name": "test_pattern",
                    "description": "Test pattern",
                    "related_endpoints": "/test",  # 型不一致: listであるべき
                    "notes": ["note1"],
                }
            ]
        }
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError, match="Data validation failed"):
            load_patterns(invalid_file)

    def test_validation_error_message_missing_fields(self, tmp_path):
        """必須フィールド欠落時の詳細なエラーメッセージ検証"""
        invalid_file = tmp_path / "missing_fields.json"
        invalid_data = {"endpoints": [{"name": "test"}]}
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError) as exc_info:
            load_endpoints(invalid_file)

        error_message = str(exc_info.value)
        # 必須フィールドが欠けていることが明記されている
        assert "path" in error_message
        assert "method" in error_message
        assert "description" in error_message
        assert "response" in error_message
        assert "Field required" in error_message

    def test_validation_error_message_type_mismatch(self, tmp_path):
        """型不一致時の詳細なエラーメッセージ検証"""
        invalid_file = tmp_path / "type_error.json"
        invalid_data = {
            "endpoints": [
                {
                    "name": "test",
                    "name_ja": "テスト",
                    "name_en": "Test",
                    "path": "/test",
                    "path_old": "/old/test",
                    "method": "GET",
                    "description": "Test",
                    "parameters": [],
                    "response": {"description": "Test", "fields": []},
                    "auth_required": {"invalid": "type"},
                    "response_data_key": "data",
                    "plan": ["Free"],
                    "data_update": {"frequency": "日次", "time": "17:00"},
                    "parameter_patterns": [],
                }
            ]
        }
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError) as exc_info:
            load_endpoints(invalid_file)

        error_message = str(exc_info.value)
        # 型エラーが明記されている
        assert "auth_required" in error_message
        assert "bool" in error_message.lower()

    def test_validation_error_message_patterns(self, tmp_path):
        """パターンのバリデーションエラーメッセージ検証"""
        invalid_file = tmp_path / "pattern_error.json"
        # descriptionが欠けている
        invalid_data = {"patterns": [{"pattern_name": "test"}]}
        invalid_file.write_text(json.dumps(invalid_data))

        with pytest.raises(DataLoadError) as exc_info:
            load_patterns(invalid_file)

        error_message = str(exc_info.value)
        # 必須フィールドが欠けていることが明記されている
        assert "description" in error_message
        assert "Field required" in error_message
