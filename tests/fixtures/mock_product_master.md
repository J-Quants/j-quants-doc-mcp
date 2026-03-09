# Product Master (/products/master)

`GET`    /v1/products/master

## Overview

Retrieve product information for past, current, and future dates.\
Note that future data becomes available after 18:00 on the previous business day.

### Attention

> **Info**
>
> - If you specify a date before the data start date (Jan 1, 2015), data from Jan 1, 2015 will be returned.
> - For non-business days, the next business day's data will be returned.
> - CategoryCode field is available for Standard and Premium plans only.

> **Note**
>
> Due to system changes in 2022, some products may have different categorization.

## Retrieve product master data

`GET` `https://api.example.com/v1/products/master`

You can specify product code or date parameters.\
Parameter combinations and their results:

- code: –, date: – → All products as of today. (\*1)

- code: ✓, date: – → Specified product as of today. (\*1)

- code: –, date: ✓ → All products as of specified date. (\*2)

- code: ✓, date: ✓ → Specified product as of specified date. (\*2)

\*1 On non-business days, next business day data is returned.\
\*2 For paid plans, next business day data is available.

### Requests

### Headers

| Parameter | Type   | Required | Description |
| --------- | ------ | -------- | ----------- |
| x-api-key | string | Required | API Key     |

### Query Parameters

| Parameter | Type   | Required | Description                                              |
| --------- | ------ | -------- | -------------------------------------------------------- |
| code      | string | Optional | Product code (e.g. PROD001 or 001)                       |
| date      | string | Optional | Date (e.g. 20230501 or 2023-05-01)                       |

### Sample Code

/v1/products/master

**cURL**

```bash
curl -G https://api.example.com/v1/products/master \
-H "x-api-key: {{apiKey}}" \
-d code="{{code}}" \
-d date="{{date}}"
```

**JavaScript**

```javascript
import axios from 'axios'

const client = axios.create({
  baseURL: 'https://api.example.com',
  headers: { 'x-api-key': '{{apiKey}}' },
})

await client.get('/v1/products/master', {
  params: {
    code: '{{code}}',
    date: '{{date}}',
  },
})
```

**Python**

```python
import requests

headers = {"x-api-key": "{{apiKey}}"}
resp = requests.get(
    "https://api.example.com/v1/products/master",
    params={"code": "{{code}}", "date": "{{date}}"},
    headers=headers,
)
print(resp.json())
```

### Responses

### Data Item

| Parameter | Type   | Required | Description                                                   |
| --------- | ------ | -------- | ------------------------------------------------------------- |
| Date      | string | Required | Date of data (YYYY-MM-DD)                                     |
| Code      | string | Required | Product code                                                  |
| Name      | string | Required | Product name                                                  |
| NameEn    | string | Required | Product name (English)                                        |
| Cat       | string | Required | Category code (See [Category codes](/spec/product-master/categories)) |
| CatName   | string | Required | Category name (See [Category codes](/spec/product-master/categories)) |
| Status    | string | Required | Status (1: Active / 2: Inactive / 3: Pending)                |

### Response Sample

```bash {{ title: "200:OK" }}
{
    "data": [
        {
            "Date": "2023-05-15",
            "Code": "PROD001",
            "Name": "サンプル商品A",
            "NameEn": "Sample Product A",
            "Cat": "CAT01",
            "CatName": "電子機器",
            "Status": "1"
        }
    ]
}
```
