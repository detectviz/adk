# 自訂

## 新增 BigQuery 表格權限的說明

本文件提供如何授與使用者存取由 `brand_search_optimization/bq_populate_data.py` 指令碼建立和填入的 BigQuery 表格權限的說明。您可以使用 Google Cloud Console、`bq` 命令列工具或 BigQuery API 來管理這些權限。

### 1. 使用 Google Cloud Console：

1.  前往 Google Cloud Console：[https://console.cloud.google.com/bigquery](https://console.cloud.google.com/bigquery)
2.  在「瀏覽器」面板 (左側) 中，展開您的專案，然後展開您的資料集。
3.  按一下您的表格名稱。
4.  在「表格詳細資料」頁面上，按一下「權限」分頁。
5.  按一下「新增主體」按鈕。
6.  在「新增主體」欄位中，輸入您要授與權限的使用者 (或群組/服務帳戶) 的電子郵件地址或識別碼。
7.  在「選取角色」下拉式選單中，選擇適當的角色。存取 BigQuery 表格的一些常見角色包括：
    * **BigQuery 資料檢視者：** 允許使用者查詢和檢視表格資料。
    * **BigQuery 資料編輯者：** 允許使用者修改表格資料 (插入、更新、刪除)。
    * **BigQuery 管理員：** 提供對表格的完整控制權。
    * **BigQuery 使用者：** 授與在專案內執行查詢和執行其他 BigQuery 動作的基本權限。
8.  按一下「儲存」。

### 2. 使用 `bq` 命令列工具：

1.  確定您已安裝並設定 Google Cloud CLI (`gcloud`)。
2.  開啟您的終端機或命令提示字元。
3.  搭配適當的角色和成員使用 `bq add-iam-policy` 命令。

    例如，若要將 BigQuery 資料檢視者角色授與使用者 `user@example.com` 到您的表格 (假設您的專案 ID 為 `your-project-id`、您的資料集 ID 為 `your_dataset_id`，以及您的表格 ID 為 `products`)：

    ```bash
    bq add-iam-policy --member=user:user@example.com --role=roles/bigquery.dataViewer your-project-id:your_dataset_id.products
    ```

    取代：
    * `your-project-id` 為您實際的 Google Cloud 專案 ID。
    * `your_dataset_id` 為您的 BigQuery 資料集名稱。
    * `products` 為您的 BigQuery 表格名稱 (如果您變更了預設值)。

    您可以在 BigQuery 文件中找到可用角色的清單。

### 3. 以程式設計方式使用 BigQuery API：

您可以在 Python 指令碼或其他程式設計語言中使用 BigQuery API 來管理表格權限。這涉及到與 `Table` 資源及其 `iamPolicy` 屬性互動。以下是使用 `google-cloud-bigquery` 函式庫的基本 Python 範例：

```python
from google.cloud import bigquery

# 以您的實際詳細資料取代
PROJECT_ID = "your-project-id"
DATASET_ID = "your_dataset_id"
TABLE_ID = "products"
USER_EMAIL = "user@example.com"
ROLE = "roles/bigquery.dataViewer"

client = bigquery.Client(project=PROJECT_ID)
table_ref = client.dataset(DATASET_ID).table(TABLE_ID)
table = client.get_table(table_ref)  # 取得目前的表格中繼資料

policy = table.iam_policy
policy.bindings.append({"role": ROLE, "members": [f"user:{USER_EMAIL}"]})
table.iam_policy = policy

table = client.update_table(table)  # 更新表格的 IAM 政策

print(f"Granted role '{ROLE}' to user '{USER_EMAIL}' on table '{table.full_table_id}'.")
```