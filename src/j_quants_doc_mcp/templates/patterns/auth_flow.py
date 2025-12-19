# 1. APIキーの取得
api_key = os.getenv("JQUANTS_API_KEY")

# 2. APIリクエスト時にAPIキーを使用
headers = {"x-api-key": api_key}
data = GET("/equities/master", headers=headers)
