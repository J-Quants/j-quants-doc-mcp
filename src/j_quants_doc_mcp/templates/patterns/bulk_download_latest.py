#!/usr/bin/env python

# 最新ファイル（historical/liveを問わず）を1件だけ取得
# 用途: とにかく最新のデータが欲しい場合

target_endpoint = "/equities/bars/daily"  # 株価四本値を例とする

# ファイル一覧を取得
list_response = GET(
    "/bulk/list",
    {"endpoint": target_endpoint},
    headers={"x-api-key": api_key},
)

files = list_response["data"]
if not files:
    raise Exception("指定したendpointに対するバルクファイルが見つかりません")

# bulk-listは昇順（古い順）で返されるため、末尾要素が最新ファイル
latest_file = files[-1]
key = latest_file["Key"]
size = latest_file["Size"]
last_modified = latest_file["LastModified"]

print(f"最新ファイル: {key} ({size} bytes, LastModified={last_modified})")

# 署名付きURLを取得
url_response = GET(
    "/bulk/get",
    {"key": key},
    headers={"x-api-key": api_key},
)

download_url = url_response["url"]
print(f"Download URL: {download_url}")

# ダウンロード
csv_bytes = HTTP_GET_BINARY(download_url)
output_path = f"./{key.split('/')[-1]}"
save_to_disk(output_path, csv_bytes)

print(f"ファイルを保存しました: {output_path}")

