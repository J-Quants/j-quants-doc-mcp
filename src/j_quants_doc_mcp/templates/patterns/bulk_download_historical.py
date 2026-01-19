#!/usr/bin/env python

# 過去の月次データ（historical）を一括取得
# 用途: 過去の全データを一括でダウンロードしたい場合
# 特徴: 月単位でまとめられた大容量ファイル

target_endpoint = "/markets/margin-alert"  # 日々公表信用取引残高を例とする

# ファイル一覧を取得
list_response = GET(
    "/bulk/list",
    {"endpoint": target_endpoint},
    headers={"x-api-key": api_key},
)

files = list_response["data"]

# historicalファイル（月次データ）のみをフィルタリング
historical_files = [f for f in files if "historical" in f["Key"]]
# 最新から取得したい場合: historical_files = reversed(historical_files)

print(f"過去の月次データファイル: {len(historical_files)}件")

# 各月次ファイルをダウンロード（古い順に処理される）
for file_info in historical_files:
    key = file_info["Key"]
    # 例: markets/margin-alert/historical/2023/markets_margin-alert_202312.csv.gz
    
    # 署名付きURLを取得
    url_response = GET(
        "/bulk/get",
        {"key": key},
        headers={"x-api-key": api_key},
    )
    
    download_url = url_response["url"]
    csv_bytes = HTTP_GET_BINARY(download_url)
    
    output_path = f"./{key.split('/')[-1]}"
    save_to_disk(output_path, csv_bytes)
    print(f"保存: {output_path}")

