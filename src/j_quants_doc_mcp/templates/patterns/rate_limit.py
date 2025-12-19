# リトライ処理付きのリクエスト関数
MAX_RETRIES = 3
BASE_WAIT_TIME = 1  # 秒

for attempt in range(MAX_RETRIES):
    try:
        response = GET(
            "/equities/bars/daily", {"code": "7203"}, headers={"x-api-key": api_key}
        )

        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            # レート制限エラー
            wait_time = response.headers.get(
                "Retry-After", BASE_WAIT_TIME * (2**attempt)
            )
            print(f"レート制限。{wait_time}秒待機します")
            sleep(float(wait_time))
        else:
            raise Exception(f"エラー: {response.status_code}")
    except Exception as e:
        if attempt == MAX_RETRIES - 1:
            raise  # 最終試行で失敗した場合は例外を投げる
        sleep(BASE_WAIT_TIME * (2**attempt))

# 複数リクエストの場合は間隔を空ける
codes = ["7203", "6758", "9984"]
for code in codes:
    data = request_with_retry("/equities/bars/daily", {"code": code})
    process_data(data)
    sleep(0.5)  # 次のリクエストまで待機
