# 特定企業の財務情報を取得
response = GET(
    "/fins/summary",
    {"code": "86970"},  # 日揮ホールディングス
    headers={"x-api-key": api_key},
)

# 時系列分析のため複数期のデータを取得
financial_data = []
for statement in response["data"]:
    financial_data.append(
        {
            "date": statement["PubDate"],
            "sales": statement["Sales"],
            "operating_profit": statement["OP"],
            "net_profit": statement["NP"],
            "eps": statement["EPS"],
        }
    )

# 成長率の計算
for i in range(1, len(financial_data)):
    prev = financial_data[i - 1]
    curr = financial_data[i]
    sales_growth = (curr["sales"] - prev["sales"]) / prev["sales"] * 100
    print(f"{curr['date']}: 売上成長率 {sales_growth:.2f}%")
