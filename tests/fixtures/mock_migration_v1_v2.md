# V1 API から V2 API への変更点

## 認証認可

認証方式が「トークン方式」から「APIキー方式」に変更されました。

## エンドポイント・パラメータの変更

| データセット | V1 エンドポイント | V2 エンドポイント |
| --- | --- | --- |
| 株価四本値 | /v1/prices/daily_quotes | /v2/equities/bars/daily |
| 上場銘柄一覧 | /v1/listed/info | /v2/equities/master |
| 財務情報 | /v1/fins/statements | /v2/fins/summary |

## レスポンス形式

レスポンス構造が統一されました。
