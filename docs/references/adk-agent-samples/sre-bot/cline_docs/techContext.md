# SRE 助理代理的技術脈絡

## 使用的技術

1. **Python 3.10+**：應用程式使用的核心程式語言。

2. **Google 代理開發套件 (ADK)**：用於建置與 Google Gemini 模型對話的代理框架。

3. **Gemini 2.0 Flash**：用於自然語言理解和生成的大型語言模型。

4. **Kubernetes Python 客戶端**：官方的 Kubernetes Python 客戶端函式庫，用於與 Kubernetes 叢集互動。

5. **Python-dateutil**：用於在 Python 中操作日期和時間的函式庫。

## 開發設定

1. **虛擬環境**：專案使用 Python 的虛擬環境進行依賴隔離。

2. **API 金鑰**：需要 Google API 金鑰才能存取 Gemini。

3. **Kubernetes 設定**：使用使用者環境中的預設 Kubernetes 設定。

4. **套件管理**：透過 pip 和 requirements.txt 管理依賴項。

## 技術限制

1. **Kubernetes 存取**：代理需要存取 Kubernetes 叢集並具有執行操作的適當權限。

2. **API 速率限制**：Google Gemini API 有速率限制，在生產使用中需要考慮。

3. **驗證**：代理從其執行環境中繼承 Kubernetes 驗證。

4. **資源需求**：應用程式需要足夠的記憶體來執行 Python 直譯器和處理來自 Gemini 模型的回應。

5. **網路存取**：需要對 Google API 和 Kubernetes API 伺服器的網路存取。

6. **安全性考量**：
   - 代理在存取 Kubernetes 資源時應遵循最小權限原則。
   - API 金鑰和憑證應安全管理。
   - 在公開代理的 API 時應小心謹慎，以防止未經授權的存取。
