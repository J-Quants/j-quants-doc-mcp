#!/usr/bin/env python

# 当月の日次データ（live）を取得
# 用途: 当月分の日次データを取得したい場合（月の上旬には先月分も含む）
# 特徴: 1日単位の小さなファイル

target_endpoint = "/markets/margin-alert"  # 日々公表信用取引残高を例とする

# ファイル一覧を取得
list_response = GET(
    "/bulk/list",
    {"endpoint": target_endpoint},
    headers={"x-api-key": api_key},
)

files = list_response["data"]

# liveファイル（日次データ）のみをフィルタリング
live_files = [f for f in files if "live" in f["Key"]]
# 最新から取得したい場合: live_files = reversed(live_files)

print(f"当月の日次データファイル: {len(live_files)}件")

# 各日次ファイルをダウンロード（古い順に処理される）
for file_info in live_files:
    key = file_info["Key"]
    # 例: markets/margin-alert/live/markets_margin-alert_20240115.csv.gz
    
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

