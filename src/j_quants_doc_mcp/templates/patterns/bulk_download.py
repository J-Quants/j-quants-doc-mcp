#!/usr/bin/env python

# Bulk APIを使用したデータ一括取得
# 用途: 全銘柄データを効率的に一括ダウンロード
# BulkListでファイル一覧を取得し、BulkGetで各ファイルをダウンロード

target_endpoint = "/markets/margin-alert"  # 日々公表信用取引残高を例とする

# ファイル一覧を取得
list_response = GET(
    "/bulk/list",
    {"endpoint": target_endpoint},
    headers={"x-api-key": api_key},
)

files = list_response["data"]
print(f"利用可能なファイル: {len(files)}件")

# ファイルのフィルタリング（必要に応じて）
# 例1: historical（月次）のみ取得したい場合
# files = [f for f in files if "historical" in f["Key"]]
# 例2: live（日次）のみ取得したい場合
# files = [f for f in files if "live" in f["Key"]]
# 例3: 最新の1件のみ取得したい場合
# files = [files[-1]]  # bulk-listは昇順（古い順）で返される
# 例4: 最新から遡って取得したい場合
# files = reversed(files)

# 各ファイルをダウンロード
for file_info in files:
    key = file_info["Key"]
    # 例: markets/margin-alert/historical/2023/markets_margin-alert_202312.csv.gz
    # 例: markets/margin-alert/live/2024/markets_margin-alert_20240115.csv.gz
    
    # 署名付きURLを取得
    url_response = GET(
        "/bulk/get",
        {"key": key},
        headers={"x-api-key": api_key},
    )
    
    download_url = url_response["url"]
    # URLの有効期限は約5分なので、すぐにダウンロードする
    csv_bytes = HTTP_GET_BINARY(download_url)
    
    output_path = f"./{key.split('/')[-1]}"
    save_to_disk(output_path, csv_bytes)
    print(f"保存: {output_path}")
