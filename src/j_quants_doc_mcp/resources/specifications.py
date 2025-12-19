"""API specifications resource for J-Quants."""

import json
import logging
from pathlib import Path

from pydantic import ValidationError

from j_quants_doc_mcp.models.endpoint import EndpointCollection
from j_quants_doc_mcp.models.pattern import PatternCollection

# ロガーの設定
logger = logging.getLogger(__name__)


class DataLoadError(Exception):
    """データ読み込みエラー用の例外クラス"""

    pass


def get_data_directory() -> Path:
    """データディレクトリのパスを取得"""
    return Path(__file__).parent.parent / "data"


def get_templates_directory() -> Path:
    """テンプレートディレクトリのパスを取得"""
    return Path(__file__).parent.parent / "templates"


def load_sample_code(sample_code_path: str) -> str:
    """
    サンプルコードファイルを読み込む。

    Args:
        sample_code_path: templates配下からの相対パス

    Returns:
        str: サンプルコードの内容

    Raises:
        DataLoadError: ファイルの読み込みに失敗した場合
    """
    templates_dir = get_templates_directory()
    file_path = templates_dir / sample_code_path

    try:
        if not file_path.exists():
            raise DataLoadError(f"Sample code file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        if isinstance(e, DataLoadError):
            raise
        error_msg = f"Error loading sample code from {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e


def load_endpoints(file_path: Path | None = None) -> EndpointCollection:
    """
    endpoints.jsonを読み込み、pydanticで検証されたEndpointCollectionを返す。

    Args:
        file_path: JSONファイルのパス。指定しない場合はデフォルトのパスを使用。

    Returns:
        EndpointCollection: 検証済みのエンドポイントコレクション

    Raises:
        DataLoadError: ファイルの読み込みまたは検証に失敗した場合
    """
    if file_path is None:
        file_path = get_data_directory() / "endpoints.json"

    try:
        logger.info(f"Loading endpoints from: {file_path}")

        if not file_path.exists():
            raise DataLoadError(f"Endpoints file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Pydanticで検証
        endpoint_collection = EndpointCollection(**data)

        logger.info(
            f"Successfully loaded {len(endpoint_collection.endpoints)} endpoints"
        )
        return endpoint_collection

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e

    except ValidationError as e:
        error_msg = f"Data validation failed for {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error loading endpoints from {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e


def load_patterns(file_path: Path | None = None) -> PatternCollection:
    """
    patterns.jsonを読み込み、pydanticで検証されたPatternCollectionを返す。

    Args:
        file_path: JSONファイルのパス。指定しない場合はデフォルトのパスを使用。

    Returns:
        PatternCollection: 検証済みのパターンコレクション

    Raises:
        DataLoadError: ファイルの読み込みまたは検証に失敗した場合
    """
    if file_path is None:
        file_path = get_data_directory() / "patterns.json"

    try:
        logger.info(f"Loading patterns from: {file_path}")

        if not file_path.exists():
            raise DataLoadError(f"Patterns file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        # Pydanticで検証
        pattern_collection = PatternCollection(**data)

        logger.info(f"Successfully loaded {len(pattern_collection.patterns)} patterns")
        return pattern_collection

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e

    except ValidationError as e:
        error_msg = f"Data validation failed for {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e

    except Exception as e:
        error_msg = f"Unexpected error loading patterns from {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e


def load_reference_data(file_path: Path | None = None) -> dict:
    """
    reference_data.jsonを読み込む。

    市場区分コード、業種コード、指数コードなどの参照データを定義する。

    Args:
        file_path: JSONファイルのパス。指定しない場合はデフォルトのパスを使用。

    Returns:
        dict: 参照データ

    Raises:
        DataLoadError: ファイルの読み込みに失敗した場合
    """
    if file_path is None:
        file_path = get_data_directory() / "reference_data.json"

    try:
        logger.info(f"Loading reference data from: {file_path}")

        if not file_path.exists():
            raise DataLoadError(f"Reference data file not found: {file_path}")

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)

        logger.info(
            f"Successfully loaded {len(data.get('reference_data', []))} reference data entries"
        )
        return data

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format in {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e

    except Exception as e:
        if isinstance(e, DataLoadError):
            raise
        error_msg = f"Unexpected error loading reference data from {file_path}: {e}"
        logger.error(error_msg)
        raise DataLoadError(error_msg) from e
