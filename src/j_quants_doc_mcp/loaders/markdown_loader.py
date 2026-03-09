"""Markdown loader for J-Quants specification documentation."""

import json
import logging
import os
import time
from pathlib import Path
from typing import Any
from urllib import request
from urllib.error import HTTPError, URLError

logger = logging.getLogger(__name__)

# 設定ファイルのパス
CONFIG_PATH = Path(__file__).parent.parent / "data" / "spec_config.json"

# キャッシュ
_cache: dict[str, dict[str, Any]] = {}


def _load_config() -> dict[str, Any]:
    """設定ファイルを読み込む。
    
    環境変数JQUANTS_BASE_URLが設定されている場合は、
    設定ファイルのbase_urlを上書きする。

    Returns:
        設定情報を含む辞書
    """
    with open(CONFIG_PATH, encoding="utf-8") as f:
        config = json.load(f)
    
    # 環境変数でbase_urlを上書き
    if "JQUANTS_BASE_URL" in os.environ:
        config["base_url"] = os.environ["JQUANTS_BASE_URL"]
        logger.info(f"Using base_url from environment variable: {config['base_url']}")
    
    return config


def _is_cache_valid(cache_key: str, ttl: int) -> bool:
    """キャッシュが有効かどうかを確認する。

    Args:
        cache_key: キャッシュキー
        ttl: TTL（秒）

    Returns:
        キャッシュが有効な場合True
    """
    if cache_key not in _cache:
        return False

    cached_time = _cache[cache_key].get("timestamp", 0)
    current_time = time.time()

    return (current_time - cached_time) < ttl


def _fetch_markdown(url: str) -> str:
    """指定されたURLからMarkdownを取得する。

    Args:
        url: MarkdownファイルのURL

    Returns:
        Markdownテキスト

    Raises:
        HTTPError: HTTPエラーが発生した場合
        URLError: ネットワークエラーが発生した場合
    """
    logger.info(f"Fetching markdown from: {url}")

    try:
        req = request.Request(url, headers={"User-Agent": "J-Quants-Doc-MCP/1.0"})
        with request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except HTTPError as e:
        logger.error(f"HTTP error fetching {url}: {e.code} {e.reason}")
        raise
    except URLError as e:
        logger.error(f"URL error fetching {url}: {e.reason}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        raise


def load_endpoint_list(language: str | None = None) -> dict[str, Any]:
    """エンドポイント一覧ページのMarkdownを取得する。

    Args:
        language: 言語コード（デフォルトは設定ファイルの値）

    Returns:
        以下のキーを含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - cached: キャッシュから取得したかどうか
    """
    config = _load_config()
    lang = language or config.get("default_language", "ja")
    base_url = config.get("base_url", "http://localhost:3000")
    list_page = config.get("endpoints", {}).get("list_page", "/spec/data-spec")
    ttl = config.get("cache_ttl_seconds", 300)

    # URLを構築
    fetch_url = f"{base_url}/{lang}{list_page}.md"  # 取得用（.md付き）
    user_url = f"{base_url}/{lang}{list_page}"  # ユーザー表示用（.mdなし）
    cache_key = f"list_{lang}"

    # キャッシュチェック
    if _is_cache_valid(cache_key, ttl):
        logger.info(f"Using cached endpoint list for language: {lang}")
        return {
            "content": _cache[cache_key]["content"],
            "source_url": user_url,
            "cached": True,
        }

    # Markdownを取得
    try:
        content = _fetch_markdown(fetch_url)

        # キャッシュに保存
        _cache[cache_key] = {"content": content, "timestamp": time.time()}

        return {"content": content, "source_url": user_url, "cached": False}

    except (HTTPError, URLError) as e:
        logger.error(f"Failed to load endpoint list from {fetch_url}: {e}")
        raise RuntimeError(
            f"エンドポイント一覧の取得に失敗しました。URLを確認してください: {user_url}\n"
            f"エラー詳細: {e}\n"
            f"後ほど再度お試しください。"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error loading endpoint list: {e}")
        raise RuntimeError(
            f"エンドポイント一覧の取得中に予期しないエラーが発生しました: {e}\n"
            f"後ほど再度お試しください。"
        ) from e


def load_spec_page(path: str, language: str | None = None) -> dict[str, Any]:
    """指定されたパスのSpecificationページのMarkdownを取得する（汎用関数）。

    Args:
        path: Specificationページのパス（例: /spec/eq-master, /spec/mkt-cal/holiday-division）
        language: 言語コード（デフォルトは設定ファイルの値）

    Returns:
        以下のキーを含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - path: リクエストされたパス
        - cached: キャッシュから取得したかどうか
    """
    config = _load_config()
    lang = language or config.get("default_language", "ja")
    base_url = config.get("base_url", "http://localhost:3000")
    ttl = config.get("cache_ttl_seconds", 300)

    # パスの正規化（先頭の/を削除）
    normalized_path = path.lstrip("/")

    # URLを構築
    fetch_url = f"{base_url}/{lang}/{normalized_path}.md"  # 取得用（.md付き）
    user_url = f"{base_url}/{lang}/{normalized_path}"  # ユーザー表示用（.mdなし）
    cache_key = f"spec_{lang}_{normalized_path.replace('/', '_')}"

    # キャッシュチェック
    if _is_cache_valid(cache_key, ttl):
        logger.info(f"Using cached spec page for: {path}")
        return {
            "content": _cache[cache_key]["content"],
            "source_url": user_url,
            "path": path,
            "cached": True,
        }

    # Markdownを取得
    try:
        content = _fetch_markdown(fetch_url)

        # キャッシュに保存
        _cache[cache_key] = {"content": content, "timestamp": time.time()}

        return {
            "content": content,
            "source_url": user_url,
            "path": path,
            "cached": False,
        }

    except HTTPError as e:
        if e.code == 404:
            logger.warning(f"Spec page not found: {path}")
            raise FileNotFoundError(
                f"Specificationページ '{path}' が見つかりませんでした。\n"
                f"URL: {user_url}\n"
                f"パスが正しいか確認してください。"
            ) from e
        else:
            logger.error(f"HTTP error loading spec page: {e}")
            raise RuntimeError(
                f"Specificationページの取得に失敗しました: {e}\n"
                f"後ほど再度お試しください。"
            ) from e
    except URLError as e:
        logger.error(f"URL error loading spec page: {e}")
        raise RuntimeError(
            f"Specificationページの取得中にネットワークエラーが発生しました: {e}\n"
            f"サーバーが起動しているか確認してください。\n"
            f"後ほど再度お試しください。"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error loading spec page: {e}")
        raise RuntimeError(
            f"Specificationページの取得中に予期しないエラーが発生しました: {e}\n"
            f"後ほど再度お試しください。"
        ) from e


def load_endpoint_detail(
    endpoint_name: str, language: str | None = None
) -> dict[str, Any]:
    """指定されたエンドポイントの詳細ページのMarkdownを取得する。

    Args:
        endpoint_name: エンドポイント名（例: eq-master）
        language: 言語コード（デフォルトは設定ファイルの値）

    Returns:
        以下のキーを含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - endpoint_name: エンドポイント名
        - cached: キャッシュから取得したかどうか
    """
    try:
        result = load_spec_page(f"/spec/{endpoint_name}", language)
        # endpoint_nameキーを追加
        result["endpoint_name"] = endpoint_name
        return result
    except FileNotFoundError as e:
        # エンドポイント用のエラーメッセージに変換
        raise FileNotFoundError(
            f"エンドポイント '{endpoint_name}' の詳細ページが見つかりませんでした。\n"
            f"エンドポイント名が正しいか確認してください。"
        ) from e


def _get_v1_config() -> dict[str, Any]:
    """V1 API用の設定を取得する。

    Returns:
        V1の設定辞書（base_url, endpoints等）

    Raises:
        ValueError: V1設定が存在しない場合
    """
    config = _load_config()
    v1_config = config.get("v1")
    if not v1_config:
        raise ValueError("spec_config.json に v1 設定が存在しません")
    return v1_config


def load_v1_endpoint_list() -> dict[str, Any]:
    """V1 APIのエンドポイント一覧ページのMarkdownを取得する。

    Returns:
        以下のキーを含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - cached: キャッシュから取得したかどうか
    """
    config = _load_config()
    v1_config = _get_v1_config()
    v1_base_url = v1_config.get("base_url", "")
    list_page = v1_config.get("endpoints", {}).get("list_page", "/api-reference")
    ttl = config.get("cache_ttl_seconds", 300)

    fetch_url = f"{v1_base_url}{list_page}.md"
    user_url = f"{v1_base_url}{list_page}"
    cache_key = "v1_list"

    if _is_cache_valid(cache_key, ttl):
        logger.info("Using cached V1 endpoint list")
        return {
            "content": _cache[cache_key]["content"],
            "source_url": user_url,
            "cached": True,
        }

    try:
        content = _fetch_markdown(fetch_url)
        _cache[cache_key] = {"content": content, "timestamp": time.time()}
        return {"content": content, "source_url": user_url, "cached": False}
    except (HTTPError, URLError) as e:
        logger.error(f"Failed to load V1 endpoint list from {fetch_url}: {e}")
        raise RuntimeError(
            f"V1エンドポイント一覧の取得に失敗しました。URL: {user_url}\n"
            f"エラー詳細: {e}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error loading V1 endpoint list: {e}")
        raise RuntimeError(
            f"V1エンドポイント一覧の取得中に予期しないエラーが発生しました: {e}"
        ) from e


def load_v1_endpoint_detail(endpoint_name: str) -> dict[str, Any]:
    """V1 APIの指定エンドポイントの詳細ページのMarkdownを取得する。

    Args:
        endpoint_name: V1エンドポイント名（例: daily_quotes, listed_info等）

    Returns:
        以下のキーを含む辞書:
        - content: Markdownテキスト
        - source_url: 取得元URL
        - endpoint_name: エンドポイント名
        - cached: キャッシュから取得したかどうか
    """
    config = _load_config()
    v1_config = _get_v1_config()
    v1_base_url = v1_config.get("base_url", "")
    list_page = v1_config.get("endpoints", {}).get("list_page", "/api-reference")
    ttl = config.get("cache_ttl_seconds", 300)

    normalized_name = endpoint_name.lstrip("/")
    fetch_url = f"{v1_base_url}{list_page}/{normalized_name}.md"
    user_url = f"{v1_base_url}{list_page}/{normalized_name}"
    cache_key = f"v1_spec_{normalized_name.replace('/', '_')}"

    if _is_cache_valid(cache_key, ttl):
        logger.info(f"Using cached V1 endpoint detail for: {endpoint_name}")
        return {
            "content": _cache[cache_key]["content"],
            "source_url": user_url,
            "endpoint_name": endpoint_name,
            "cached": True,
        }

    try:
        content = _fetch_markdown(fetch_url)
        _cache[cache_key] = {"content": content, "timestamp": time.time()}
        return {
            "content": content,
            "source_url": user_url,
            "endpoint_name": endpoint_name,
            "cached": False,
        }
    except HTTPError as e:
        if e.code == 404:
            logger.warning(f"V1 endpoint not found: {endpoint_name}")
            raise FileNotFoundError(
                f"V1エンドポイント '{endpoint_name}' の詳細ページが見つかりませんでした。\n"
                f"URL: {user_url}"
            ) from e
        logger.error(f"HTTP error loading V1 endpoint detail: {e}")
        raise RuntimeError(
            f"V1エンドポイント詳細の取得に失敗しました: {e}"
        ) from e
    except URLError as e:
        logger.error(f"URL error loading V1 endpoint detail: {e}")
        raise RuntimeError(
            f"V1エンドポイント詳細の取得中にネットワークエラーが発生しました: {e}"
        ) from e
    except Exception as e:
        logger.error(f"Unexpected error loading V1 endpoint detail: {e}")
        raise RuntimeError(
            f"V1エンドポイント詳細の取得中に予期しないエラーが発生しました: {e}"
        ) from e


def get_external_links(language: str | None = None) -> dict[str, str]:
    """外部リンク情報を取得する。

    Args:
        language: 言語コード（デフォルトは設定ファイルの値）

    Returns:
        外部リンクの辞書（キー: リンク種別、値: 完全なURL）
    """
    config = _load_config()
    lang = language or config.get("default_language", "ja")
    base_url = config.get("base_url", "http://localhost:3000")
    external_links = config.get("external_links", {})

    # 完全なURLを構築
    return {
        key: f"{base_url}/{lang}{path}"
        for key, path in external_links.items()
    }


def clear_cache() -> None:
    """キャッシュをクリアする。"""
    global _cache
    _cache.clear()
    logger.info("Cache cleared")
