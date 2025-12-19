# j-quants-doc-mcp

J-Quants APIのドキュメントを提供するMCPサーバー。Claude DesktopなどのMCPクライアントから、J-Quants APIのエンドポイント検索、詳細情報の取得、実行可能なサンプルコード生成、FAQ回答などの機能を利用できます。

## インストール

### 必須要件

- Python 3.10以上
- [uv](https://github.com/astral-sh/uv) (推奨) または pip

### uv toolを使用する場合(推奨)

```bash
# GitHubから直接インストール
uv tool install git+https://github.com/J-Quants/j-quants-doc-mcp.git

# またはローカルから
git clone https://github.com/J-Quants/j-quants-doc-mcp.git
cd j-quants-doc-mcp
uv tool install .
```

### pipを使用する場合

```bash
# GitHubから直接インストール
pip install git+https://github.com/J-Quants/j-quants-doc-mcp.git

# またはローカルから
git clone https://github.com/J-Quants/j-quants-doc-mcp.git
cd j-quants-doc-mcp
pip install .
```

## 起動方法

### スタンドアロンで起動

```bash
# uv toolでインストールした場合
uvx j-quants-doc-mcp

# pipでインストールした場合
j-quants-doc-mcp
```

### Claude Desktopから使用

`claude_desktop_config.json`に以下を追加:

```json
{
  "mcpServers": {
    "j-quants-doc-mcp": {
      "command": "uvx",
      "args": ["j-quants-doc-mcp"]
    }
  }
}
```

pipでインストールした場合は、`j-quants-doc-mcp` コマンドを直接指定します:
```json
{
  "mcpServers": {
    "j-quants-doc-mcp": {
      "command": "j-quants-doc-mcp",
      "args": []
    }
  }
}
```

設定ファイルの場所:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`

### Cursorから使用

メニューバー「Cursor」→「Preferences」→「Cursor Settings」を開き、\
左のメニュー「Tools & MCP」を選択し、「New MCP Server」をクリック。\
開かれたJSONファイル(`~/.cursor/mcp.json`)に以下を追加:

```json
{
  "mcpServers": {
    "j-quants-doc-mcp": {
      "command": "uvx",
      "args": ["j-quants-doc-mcp"]
    }
  }
}
```

pipでインストールした場合は、`j-quants-doc-mcp` コマンドを直接指定します:
```json
{
  "mcpServers": {
    "j-quants-doc-mcp": {
      "command": "j-quants-doc-mcp",
      "args": []
    }
  }
}
```

以上の設定で、AIクライアントにてMCPサーバーを利用する準備が完了しました。

## トラブルシューティング

### Claude Desktopで認識されない

1. 設定ファイルのJSONが正しいか確認
2. Claude Desktopを再起動
3. MCPサーバーのログを確認

### 生成されたコードが実行できない

1. 必要な依存関係をインストール: `pip install httpx python-dotenv`
2. 環境変数が設定されているか確認


## 関連リンク

- [J-Quants API公式ドキュメント](https://jpx.gitbook.io/j-quants-api)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Claude Desktop](https://claude.ai/download)
- [Cursor](https://cursor.com/ja)
