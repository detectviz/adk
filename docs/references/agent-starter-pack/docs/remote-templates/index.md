# 遠端模板

遠端模板能將您的代理原型轉變為一個可用於生產的入門套件。遠端模板是一個 Git 儲存庫，包含您自訂的代理邏輯、依賴項和基礎設施定義 (Terraform)。`agent-starter-pack` CLI 使用它來產生一個完整、可部署的應用程式，方法是自動為測試和多目標部署 (例如 Cloud Run、Agent Engine) 新增生產級的樣板檔案。

## 選擇您的路徑

### 🚀 使用遠端模板
**為想要使用現有模板的開發者**

使用任何 Git 儲存庫作為模板，立即建立可用於生產的代理。非常適合快速入門或使用社群建立的模板。

**[👉 前往使用遠端模板指南](./using-remote-templates.md)**

快速範例：
```bash
uvx agent-starter-pack create my-agent -a adk@gemini-fullstack
```

---

### 🛠️ 建立遠端模板
**為想要分享自己模板的開發者**

將您自訂的代理邏輯、依賴項和基礎設施打包成可重複使用的模板，供他人使用。非常適合分享最佳實踐和建立標準化的代理模式。

**[👉 前往建立遠端模板指南](./creating-remote-templates.md)**

快速範例：
```bash
# 建立您的模板儲存庫後
uvx agent-starter-pack create test-agent -a https://github.com/you/your-template
```

---

## 總覽

遠端模板的運作方式如下：
1. **擷取** 來自 Git 的模板儲存庫
2. **應用** 基於儲存庫結構的智慧預設值
3. **合併** 模板檔案與基礎代理基礎設施
4. **產生** 完整、可用於生產的代理專案

任何 Git 儲存庫都可以成為模板——系統會自動處理複雜性。

## 相關文件

- **[使用遠端模板](./using-remote-templates.md)** - 為模板使用者提供的完整指南
- **[建立遠端模板](./creating-remote-templates.md)** - 為模板作者提供的完整指南
- **[模板設定參考](../guide/template-config-reference.md)** - 所有可用的設定選項
- **[create CLI](../cli/create.md)** - 用於建立代理的命令列參考
- **[enhance CLI](../cli/enhance.md)** - 用於增強專案的命令列參考