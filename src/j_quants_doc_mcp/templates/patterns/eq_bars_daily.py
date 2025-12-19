# 特定銘柄の直近1ヶ月のデータを取得
response = GET(
    "/equities/bars/daily",
    {"code": "7203", "from": "2025-09-01", "to": "2025-10-01"},  # トヨタ自動車
    headers={"x-api-key": api_key},
)

# レスポンスデータの処理
for data in response["data"]:
    print(f"{data['Date']}: 始値={data['O']}, 終値={data['C']}, 出来高={data['Vo']}")

# ページネーションがある場合
if "pagination_key" in response:
    next_response = GET(
        "/equities/bars/daily",
        {"code": "7203", "pagination_key": response["pagination_key"]},
        headers={"x-api-key": api_key},
    )
