# 全データを取得するループ処理
all_data = []
pagination_key = None

while True:
    params = {"date": "2025-10-01"}
    if pagination_key:
        params["pagination_key"] = pagination_key

    response = GET("/equities/bars/daily", params, headers={"x-api-key": api_key})

    all_data.extend(response["data"])

    # 次のページがあるかチェック
    if "pagination_key" in response and response["pagination_key"]:
        pagination_key = response["pagination_key"]
        sleep(0.5)  # レート制限対策
    else:
        break  # 最終ページに到達

print(f"取得件数: {len(all_data)}")
