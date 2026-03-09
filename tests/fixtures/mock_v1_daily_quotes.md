# 株価四本値 (/v1/prices/daily_quotes)

`GET` /v1/prices/daily_quotes

## 概要

株価四本値（始値・高値・安値・終値）を取得するAPIです。

### リクエスト

| パラメータ | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| code | string | 任意 | 銘柄コード |
| date | string | 任意 | 日付(YYYY-MM-DD) |
| from | string | 任意 | 開始日(YYYY-MM-DD) |
| to | string | 任意 | 終了日(YYYY-MM-DD) |

### レスポンス

| 項目 | 型 | 説明 |
| --- | --- | --- |
| Date | string | 日付 |
| Code | string | 銘柄コード |
| Open | number | 始値 |
| High | number | 高値 |
| Low | number | 安値 |
| Close | number | 終値 |
| Volume | number | 出来高 |
