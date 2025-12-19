# 特定日の全銘柄データを取得
target_date = "2025-10-01"
all_quotes = []
pagination_key = None

while True:
    params = {"date": target_date}
    if pagination_key:
        params["pagination_key"] = pagination_key

    response = GET("/equities/bars/daily", params, headers={"x-api-key": api_key})

    all_quotes.extend(response["data"])

    if "pagination_key" in response and response["pagination_key"]:
        pagination_key = response["pagination_key"]
        sleep(0.5)
    else:
        break

# 市場統計の計算
total_volume = sum(q["Vo"] for q in all_quotes)
avg_change = sum((q["C"] - q["O"]) / q["O"] for q in all_quotes if q["O"] > 0) / len(
    all_quotes
)
print(f"市場全体の出来高: {total_volume:,}")
print(f"平均変化率: {avg_change * 100:.2f}%")
