#!/usr/bin/env python

# CSVバルクファイル一覧から最新ファイルを取得し、署名付きURLでダウンロードする例

target_endpoint = "/equities/bars/daily"  # 株価四本値を例とする

# 1. ダウンロード可能ファイル一覧を取得
list_response = GET(
    "/bulk/list",
    {"endpoint": target_endpoint},
    headers={"x-api-key": api_key},
)

files = list_response["data"]
if not files:
    raise Exception("指定したendpointに対するバルクファイルが見つかりません")

# 一般的には先頭要素が最新ファイル
latest_file = files[0]
key = latest_file["Key"]
size = latest_file["Size"]
last_modified = latest_file["LastModified"]

print(f"最新ファイル: {key} ({size} bytes, LastModified={last_modified})")

# 2. ファイルダウンロード用の署名付きURLを取得
url_response = GET(
    "/bulk/get",
    {"key": key},
    headers={"x-api-key": api_key},
)

download_url = url_response["url"]
print(f"Download URL: {download_url}")

# 3. 署名付きURLを使って実際にCSVファイルをダウンロード
#    この部分は一般的なHTTPクライアントでのGETを想定した擬似コード
csv_bytes = HTTP_GET_BINARY(download_url)  # 例: requests.get(url).content

output_path = f"./{key.split('/')[-1]}"
save_to_disk(output_path, csv_bytes)  # 例: with open(output_path, "wb") as f: f.write(csv_bytes)

print(f"ファイルを保存しました: {output_path}")


