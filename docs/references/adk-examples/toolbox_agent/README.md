# 工具箱代理

此代理程式利用 [MCP toolbox for database](https://googleapis.github.io/genai-toolbox/getting-started/introduction/) 來根據儲存在資料庫中的資訊協助使用者。

請按照以下步驟執行此代理程式。

## 先決條件

開始之前，請確保您的系統上已安裝 Python。

## 安裝步驟

### 1. 安裝工具箱

執行以下指令以下載並安裝工具箱：

```bash
export OS="linux/amd64" # one of linux/amd64, darwin/arm64, darwin/amd64, or windows/amd64
curl -O https://storage.googleapis.com/genai-toolbox/v0.5.0/$OS/toolbox
chmod +x toolbox
```

### 2. 安裝 SQLite

從 [https://sqlite.org/](https://sqlite.org/) 安裝 SQLite

### 3. 安裝必要的 Python 相依性

**重要**：ADK 的 `ToolboxToolset` 類別需要 `toolbox-core` 套件，該套件不會隨 ADK 自動安裝。請使用以下指令安裝：

```bash
pip install toolbox-core
```

### 4. 建立資料庫（可選）

*注意：專案資料夾中已包含資料庫執行個體。如果您想使用現有的資料庫，請跳過此步驟。*

若要建立新資料庫：

```bash
sqlite3 tool_box.db
```

執行以下 SQL 指令來設定 hotels 資料表：

```sql
CREATE TABLE hotels(
  id            INTEGER NOT NULL PRIMARY KEY,
  name          VARCHAR NOT NULL,
  location      VARCHAR NOT NULL,
  price_tier    VARCHAR NOT NULL,
  checkin_date  DATE    NOT NULL,
  checkout_date DATE    NOT NULL,
  booked        BIT     NOT NULL
);

INSERT INTO hotels(id, name, location, price_tier, checkin_date, checkout_date, booked)
VALUES 
  (1, 'Hilton Basel', 'Basel', 'Luxury', '2024-04-22', '2024-04-20', 0),
  (2, 'Marriott Zurich', 'Zurich', 'Upscale', '2024-04-14', '2024-04-21', 0),
  (3, 'Hyatt Regency Basel', 'Basel', 'Upper Upscale', '2024-04-02', '2024-04-20', 0),
  (4, 'Radisson Blu Lucerne', 'Lucerne', 'Midscale', '2024-04-24', '2024-04-05', 0),
  (5, 'Best Western Bern', 'Bern', 'Upper Midscale', '2024-04-23', '2024-04-01', 0),
  (6, 'InterContinental Geneva', 'Geneva', 'Luxury', '2024-04-23', '2024-04-28', 0),
  (7, 'Sheraton Zurich', 'Zurich', 'Upper Upscale', '2024-04-27', '2024-04-02', 0),
  (8, 'Holiday Inn Basel', 'Basel', 'Upper Midscale', '2024-04-24', '2024-04-09', 0),
  (9, 'Courtyard Zurich', 'Zurich', 'Upscale', '2024-04-03', '2024-04-13', 0),
  (10, 'Comfort Inn Bern', 'Bern', 'Midscale', '2024-04-04', '2024-04-16', 0);
```

### 5. 建立工具設定

建立一個名為 `tools.yaml` 的 YAML 檔案。有關內容，請參閱代理程式資料夾。

### 6. 啟動工具箱伺服器

在代理程式資料夾中執行以下指令：

```bash
toolbox --tools-file "tools.yaml"
```

伺服器預設會在 `http://127.0.0.1:5000` 啟動。

### 7. 啟動 ADK Web UI

請按照 ADK 文件啟動 Web 使用者介面。

## 測試代理程式

設定完成後，您可以使用以下範例查詢來測試代理程式：

- **查詢 1**：「你能為我做什麼？」
- **查詢 2**：「你能告訴我關於「巴塞爾希爾頓」飯店的資訊嗎？」
