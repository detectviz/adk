# 產物

在 ADK 中，**產物**代表一個關鍵機制，用於管理與特定使用者互動工作階段或跨多個工作階段持續與使用者相關聯的具名、版本化二進位資料。它們讓您的代理和工具能夠處理超出簡單文字字串的資料，從而實現涉及檔案、影像、音訊和其他二進位格式的更豐富的互動。

!!! Note
    原語的特定參數或方法名稱可能會因 SDK 語言而略有不同 (例如，Python 中的 `save_artifact`，Java 中的 `saveArtifact`)。有關詳細資訊，請參閱特定語言的 API 文件。

## 什麼是產物？

*   **定義：** 產物基本上是一段二進位資料 (例如檔案的內容)，由特定範圍 (工作階段或使用者) 內的唯一 `filename` 字串標識。每次您使用相同的檔名儲存產物時，都會建立一個新版本。

*   **表示：** 產物始終使用標準的 `google.genai.types.Part` 物件表示。核心資料通常儲存在 `Part` 的內嵌資料結構中 (透過 `inline_data` 存取)，其本身包含：
    *   `data`：原始二進位內容 (位元組)。
    *   `mime_type`：一個字串，表示資料的類型 (例如 `「image/png」`、`「application/pdf」`)。這對於稍後正確解譯資料至關重要。


=== "Python"

    ```py
    # 產物如何表示為 types.Part 的範例
    import google.genai.types as types

    # 假設 'image_bytes' 包含 PNG 影像的二進位資料
    image_bytes = b'\x89PNG\r\n\x1a\n...' # 實際影像位元組的佔位符

    image_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        )
    )

    # 您也可以使用便利的建構函式：
    # image_artifact_alt = types.Part.from_bytes(data=image_bytes, mime_type="image/png")

    print(f"產物 MIME 類型：{image_artifact.inline_data.mime_type}")
    print(f"產物資料 (前 10 個位元組)：{image_artifact.inline_data.data[:10]}...")
    ```

=== "Java"

    ```java
    import com.google.genai.types.Part;
    import java.nio.charset.StandardCharsets;

    public class ArtifactExample {
        public static void main(String[] args) {
            // 假設 'imageBytes' 包含 PNG 影像的二進位資料
            byte[] imageBytes = {(byte) 0x89, (byte) 0x50, (byte) 0x4E, (byte) 0x47, (byte) 0x0D, (byte) 0x0A, (byte) 0x1A, (byte) 0x0A, (byte) 0x01, (byte) 0x02}; // 實際影像位元組的佔位符

            // 使用 Part.fromBytes 建立影像產物
            Part imageArtifact = Part.fromBytes(imageBytes, "image/png");

            System.out.println("產物 MIME 類型：" + imageArtifact.inlineData().get().mimeType().get());
            System.out.println(
                "產物資料 (前 10 個位元組)："
                    + new String(imageArtifact.inlineData().get().data().get(), 0, 10, StandardCharsets.UTF_8)
                    + "...");
        }
    }
    ```

*   **持續性和管理：** 產物不直接儲存在代理或工作階段狀態中。它們的儲存和擷取由一個專門的**產物服務** (一個 `BaseArtifactService` 的實作，定義在 `google.adk.artifacts` 中) 管理。ADK 提供了各種實作，例如：
    *   一個用於測試或臨時儲存的記憶體內服務 (例如，Python 中的 `InMemoryArtifactService`，定義在 `google.adk.artifacts.in_memory_artifact_service.py` 中)。
    *   一個使用 Google Cloud Storage (GCS) 進行持續性儲存的服務 (例如，Python 中的 `GcsArtifactService`，定義在 `google.adk.artifacts.gcs_artifact_service.py` 中)。
    當您儲存資料時，所選的服務實作會自動處理版本控制。

## 為何使用產物？

雖然工作階段 `state` 適用於儲存小片段的組態或對話上下文 (如字串、數字、布林值或小型字典/列表)，但產物是為涉及二進位或大型資料的場景而設計的：

1. **處理非文字資料：** 輕鬆儲存和擷取影像、音訊片段、視訊片段、PDF、試算表或與您的代理功能相關的任何其他檔案格式。
2. **持續化大型資料：** 工作階段狀態通常不適合儲存大量資料。產物提供了一個專門的機制來持續化較大的 blob，而不會弄亂工作階段狀態。
3. **使用者檔案管理：** 提供使用者上傳檔案 (可另存為產物) 和擷取或下載由代理產生的檔案 (從產物載入) 的功能。
4. **共用輸出：** 讓工具或代理能夠產生二進位輸出 (例如 PDF 報告或產生的影像)，可以透過 `save_artifact` 儲存，稍後由應用程式的其他部分存取，甚至在後續的工作階段中 (如果使用使用者命名空間)。
5. **快取二進位資料：** 將產生二進位資料的計算密集型操作的結果 (例如，呈現複雜的圖表影像) 儲存為產物，以避免在後續請求中重新產生它們。

實質上，每當您的代理需要處理需要持續化、版本化或共用的檔案式二進位資料時，由 `ArtifactService` 管理的產物就是 ADK 中適當的機制。


## 常見使用案例

產物為在您的 ADK 應用程式中處理二進位資料提供了一種靈活的方式。

以下是一些它們證明有價值的典型場景：

* **產生的報告/檔案：**
    * 一個工具或代理產生一份報告 (例如，PDF 分析、CSV 資料匯出、影像圖表)。

* **處理使用者上傳：**

    * 使用者透過前端介面上傳一個檔案 (例如，用於分析的影像、用於摘要的文件)。

* **儲存中間二進位結果：**

    * 一個代理執行一個複雜的多步驟流程，其中一個步驟會產生中間二進位資料 (例如，音訊合成、模擬結果)。

* **持續性使用者資料：**

    * 儲存非簡單鍵值狀態的使用者特定組態或資料。

* **快取產生的二進位內容：**

    * 一個代理根據某些輸入頻繁地產生相同的二進位輸出 (例如，公司標誌影像、標準音訊問候語)。



## 核心概念

理解產物涉及掌握幾個關鍵元件：管理它們的服務、用於保存它們的資料結構，以及它們如何被識別和版本化。

### 產物服務 (`BaseArtifactService`)

* **角色：** 負責產物實際儲存和擷取邏輯的核心元件。它定義了產物*如何*以及*在何處*被持續化。

* **介面：** 由抽象基礎類別 `BaseArtifactService` 定義。任何具體的實作都必須提供以下方法：

    * `Save Artifact`：儲存產物資料並傳回其指派的版本號碼。
    * `Load Artifact`：擷取產物的特定版本 (或最新版本)。
    * `List Artifact keys`：列出給定範圍內產物的唯一檔名。
    * `Delete Artifact`：移除一個產物 (並可能移除其所有版本，具體取決於實作)。
    * `List versions`：列出特定產物檔名的所有可用版本號碼。

* **組態：** 您在初始化 `Runner` 時提供一個產物服務的實例 (例如 `InMemoryArtifactService`、`GcsArtifactService`)。然後 `Runner` 透過 `InvocationContext` 將此服務提供給代理和工具。

=== "Python"

    ```py
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # 或 GcsArtifactService
    from google.adk.agents import LlmAgent # 任何代理
    from google.adk.sessions import InMemorySessionService

    # 範例：使用產物服務設定 Runner
    my_agent = LlmAgent(name="artifact_user_agent", model="gemini-2.0-flash")
    artifact_service = InMemoryArtifactService() # 選擇一個實作
    session_service = InMemorySessionService()

    runner = Runner(
        agent=my_agent,
        app_name="my_artifact_app",
        session_service=session_service,
        artifact_service=artifact_service # 在此處提供服務實例
    )
    # 現在，由此執行器管理的執行中的上下文可以使用產物方法
    ```

=== "Java"
    
    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    import com.google.adk.artifacts.InMemoryArtifactService;
    
    // 範例：使用產物服務設定 Runner
    LlmAgent myAgent =  LlmAgent.builder()
      .name("artifact_user_agent")
      .model("gemini-2.0-flash")
      .build();
    InMemoryArtifactService artifactService = new InMemoryArtifactService(); // 選擇一個實作
    InMemorySessionService sessionService = new InMemorySessionService();

    Runner runner = new Runner(myAgent, "my_artifact_app", artifactService, sessionService); // 在此處提供服務實例
    // 現在，由此執行器管理的執行中的上下文可以使用產物方法
    ```

### 產物資料

* **標準表示：** 產物內容普遍使用 `google.genai.types.Part` 物件表示，與用於 LLM 訊息部分的結構相同。

* **關鍵屬性 (`inline_data`)：** 對於產物，最相關的屬性是 `inline_data`，它是一個 `google.genai.types.Blob` 物件，包含：

    * `data` (`bytes`)：產物的原始二進位內容。
    * `mime_type` (`str`)：一個標準的 MIME 類型字串 (例如 `'application/pdf'`、`'image/png'`、`'audio/mpeg'`)，描述二進位資料的性質。**這對於在載入產物時正確解譯至關重要。**

=== "Python"

    ```python
    import google.genai.types as types

    # 範例：從原始位元組建立產物 Part
    pdf_bytes = b'%PDF-1.4...' # 您的原始 PDF 資料
    pdf_mime_type = "application/pdf"

    # 使用建構函式
    pdf_artifact_py = types.Part(
        inline_data=types.Blob(data=pdf_bytes, mime_type=pdf_mime_type)
    )

    # 使用便利的類別方法 (等效)
    pdf_artifact_alt_py = types.Part.from_bytes(data=pdf_bytes, mime_type=pdf_mime_type)

    print(f"建立的 Python 產物 MIME 類型為：{pdf_artifact_py.inline_data.mime_type}")
    ```
    
=== "Java"

    ```java
    --8<-- "examples/java/snippets/src/main/java/artifacts/ArtifactDataExample.java:full_code"
    ```

### 檔名

* **識別碼：** 一個簡單的字串，用於在其特定命名空間中命名和擷取產物。
* **唯一性：** 檔名在其範圍內 (工作階段或使用者命名空間) 必須是唯一的。
* **最佳實務：** 使用描述性名稱，可能包括副檔名 (例如 `"monthly_report.pdf"`、`"user_avatar.jpg"`)，儘管副檔名本身不決定行為——`mime_type` 才決定。

### 版本控制

* **自動版本控制：** 產物服務會自動處理版本控制。當您呼叫 `save_artifact` 時，服務會為該特定檔名和範圍決定下一個可用的版本號碼 (通常從 0 開始遞增)。
* **由 `save_artifact` 傳回：** `save_artifact` 方法會傳回指派給新儲存產物的整數版本號碼。
* **擷取：**
  * `load_artifact(..., version=None)` (預設)：擷取產物的*最新*可用版本。
  * `load_artifact(..., version=N)`：擷取特定版本 `N`。
* **列出版本：** `list_versions` 方法 (在服務上，而非上下文) 可用於尋找產物的所有現有版本號碼。

### 命名空間 (工作階段與使用者)

* **概念：** 產物可以限定在特定工作階段的範圍內，也可以更廣泛地限定在應用程式中所有工作階段的使用者範圍內。此範圍由 `filename` 格式決定，並由 `ArtifactService` 內部處理。

* **預設 (工作階段範圍)：** 如果您使用像 `"report.pdf"` 這樣的純檔名，產物會與特定的 `app_name`、`user_id` *和* `session_id` 相關聯。它只能在該確切的工作階段上下文中存取。


* **使用者範圍 (`"user:"` 前置詞)：** 如果您在檔名前加上 `"user:"`，例如 `"user:profile.png"`，則產物只會與 `app_name` 和 `user_id` 相關聯。它可以從該應用程式中屬於該使用者的*任何*工作階段存取或更新。


=== "Python"

    ```python
    # 說明命名空間差異的範例 (概念性)

    # 工作階段特定產物檔名
    session_report_filename = "summary.txt"

    # 使用者特定產物檔名
    user_config_filename = "user:settings.json"

    # 透過 context.save_artifact 儲存 'summary.txt' 時，
    # 它會與目前的 app_name、user_id 和 session_id 綁定。

    # 透過 context.save_artifact 儲存 'user:settings.json' 時，
    # ArtifactService 實作應該會辨識 "user:" 前置詞
    # 並將其範圍限定為 app_name 和 user_id，使其可在該使用者的所有工作階段中存取。
    ```

=== "Java"

    ```java
    // 說明命名空間差異的範例 (概念性)
    
    // 工作階段特定產物檔名
    String sessionReportFilename = "summary.txt";
    
    // 使用者特定產物檔名
    String userConfigFilename = "user:settings.json"; // "user:" 前置詞是關鍵
    
    // 透過 context.save_artifact 儲存 'summary.txt' 時，
    # 它會與目前的 app_name、user_id 和 session_id 綁定。
    // artifactService.saveArtifact(appName, userId, sessionId1, sessionReportFilename, someData);
    
    // 透過 context.save_artifact 儲存 'user:settings.json' 時，
    # ArtifactService 實作應該會辨識 "user:" 前置詞
    # 並將其範圍限定為 app_name 和 user_id，使其可在該使用者的所有工作階段中存取。
    // artifactService.saveArtifact(appName, userId, sessionId1, userConfigFilename, someData);
    ```

這些核心概念共同運作，為在 ADK 框架內管理二進位資料提供了一個靈活的系統。

## 與產物互動 (透過上下文物件)

您在代理邏輯中 (特別是在回呼或工具中) 與產物互動的主要方式是透過 `CallbackContext` 和 `ToolContext` 物件提供的方法。這些方法抽象化了由 `ArtifactService` 管理的底層儲存細節。

### 先決條件：設定 `ArtifactService`

在您可以透過上下文物件使用任何產物方法之前，您**必須**在初始化 `Runner` 時提供一個 [`BaseArtifactService` 實作](#available-implementations) (例如 [`InMemoryArtifactService`](#inmemoryartifactservice) 或 [`GcsArtifactService`](#gcsartifactservice)) 的實例。

=== "Python"

    在 Python 中，您在初始化 `Runner` 時提供此實例。

    ```python
    from google.adk.runners import Runner
    from google.adk.artifacts import InMemoryArtifactService # 或 GcsArtifactService
    from google.adk.agents import LlmAgent
    from google.adk.sessions import InMemorySessionService

    # 您的代理定義
    agent = LlmAgent(name="my_agent", model="gemini-2.0-flash")

    # 實例化所需的產物服務
    artifact_service = InMemoryArtifactService()

    # 將其提供給 Runner
    runner = Runner(
        agent=agent,
        app_name="artifact_app",
        session_service=InMemorySessionService(),
        artifact_service=artifact_service # 服務必須在此處提供
    )
    ```
    如果在 `InvocationContext` 中未設定 `artifact_service` (如果未傳遞給 `Runner`，則會發生這種情況)，在上下文物件上呼叫 `save_artifact`、`load_artifact` 或 `list_artifacts` 將會引發 `ValueError`。

=== "Java"

    在 Java 中，您會實例化一個 `BaseArtifactService` 實作，然後確保您的應用程式中管理產物的組件可以存取它。這通常是透過依賴注入或明確傳遞服務實例來完成的。

    ```java
    import com.google.adk.agents.LlmAgent;
    import com.google.adk.artifacts.InMemoryArtifactService; // 或 GcsArtifactService
    import com.google.adk.runner.Runner;
    import com.google.adk.sessions.InMemorySessionService;
    
    public class SampleArtifactAgent {
    
      public static void main(String[] args) {
    
        // 您的代理定義
        LlmAgent agent = LlmAgent.builder()
            .name("my_agent")
            .model("gemini-2.0-flash")
            .build();
    
        // 實例化所需的產物服務
        InMemoryArtifactService artifactService = new InMemoryArtifactService();
    
        // 將其提供給 Runner
        Runner runner = new Runner(agent,
            "APP_NAME",
            artifactService, // 服務必須在此處提供
            new InMemorySessionService());
    
      }
    }
    ```
    在 Java 中，如果在嘗試產物操作時 `ArtifactService` 實例不可用 (例如 `null`)，通常會導致 `NullPointerException` 或自訂錯誤，具體取決於您的應用程式結構。穩健的應用程式通常使用依賴注入框架來管理服務生命週期並確保可用性。


### 存取方法

產物互動方法可直接在 `CallbackContext` (傳遞給代理和模型回呼) 和 `ToolContext` (傳遞給工具回呼) 的實例上使用。請記住，`ToolContext` 繼承自 `CallbackContext`。

*   **程式碼範例：**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # 或 ToolContext

        async def save_generated_report_py(context: CallbackContext, report_bytes: bytes):
            """將產生的 PDF 報告位元組儲存為產物。"""
            report_artifact = types.Part.from_data(
                data=report_bytes,
                mime_type="application/pdf"
            )
            filename = "generated_report.pdf"

            try:
                version = await context.save_artifact(filename=filename, artifact=report_artifact)
                print(f"成功將 Python 產物 '{filename}' 儲存為版本 {version}。")
                # 此回呼後產生的事件將包含：
                # event.actions.artifact_delta == {"generated_report.pdf": version}
            except ValueError as e:
                print(f"儲存 Python 產物時出錯：{e}。Runner 中是否已設定 ArtifactService？")
            except Exception as e:
                # 處理潛在的儲存錯誤 (例如 GCS 權限)
                print(f"儲存 Python 產物時發生意外錯誤：{e}")

        # --- 範例用法概念 (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # 取得上下文
        #   report_data = b'...' # 假設這包含 PDF 位元組
        #   await save_generated_report_py(callback_context, report_data)
        ```

    === "Java"
    
        ```java
        import com.google.adk.agents.CallbackContext;
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;
        import com.google.genai.types.Part;
        import java.nio.charset.StandardCharsets;

        public class SaveArtifactExample {

        public void saveGeneratedReport(CallbackContext callbackContext, byte[] reportBytes) {
        // 將產生的 PDF 報告位元組儲存為產物。
        Part reportArtifact = Part.fromBytes(reportBytes, "application/pdf");
        String filename = "generatedReport.pdf";

            callbackContext.saveArtifact(filename, reportArtifact);
            System.out.println("成功儲存 Java 產物 '" + filename);
            // 此回呼後產生的事件將包含：
            // event().actions().artifactDelta == {"generated_report.pdf": version}
        }

        // --- 範例用法概念 (Java) ---
        public static void main(String[] args) {
            BaseArtifactService service = new InMemoryArtifactService(); // 或 GcsArtifactService
            SaveArtifactExample myTool = new SaveArtifactExample();
            byte[] reportData = "...".getBytes(StandardCharsets.UTF_8); // PDF 位元組
            CallbackContext callbackContext; // ... 從您的應用程式取得回呼上下文
            myTool.saveGeneratedReport(callbackContext, reportData);
            // 由於非同步性質，在真實應用程式中，請確保程式等待或處理完成。
          }
        }
        ```

#### 載入產物

*   **程式碼範例：**

    === "Python"

        ```python
        import google.genai.types as types
        from google.adk.agents.callback_context import CallbackContext # 或 ToolContext

        async def process_latest_report_py(context: CallbackContext):
            """載入最新的報告產物並處理其資料。"""
            filename = "generated_report.pdf"
            try:
                # 載入最新版本
                report_artifact = await context.load_artifact(filename=filename)

                if report_artifact and report_artifact.inline_data:
                    print(f"成功載入最新的 Python 產物 '{filename}'。")
                    print(f"MIME 類型：{report_artifact.inline_data.mime_type}")
                    # 處理 report_artifact.inline_data.data (位元組)
                    pdf_bytes = report_artifact.inline_data.data
                    print(f"報告大小：{len(pdf_bytes)} 位元組。")
                    # ... 進一步處理 ...
                else:
                    print(f"找不到 Python 產物 '{filename}'。")

                # 範例：載入特定版本 (如果版本 0 存在)
                # specific_version_artifact = await context.load_artifact(filename=filename, version=0)
                # if specific_version_artifact:
                #     print(f"已載入 '{filename}' 的版本 0。")

            except ValueError as e:
                print(f"載入 Python 產物時出錯：{e}。是否已設定 ArtifactService？")
            except Exception as e:
                # 處理潛在的儲存錯誤
                print(f"載入 Python 產物時發生意外錯誤：{e}")

        # --- 範例用法概念 (Python) ---
        # async def main_py():
        #   callback_context: CallbackContext = ... # 取得上下文
        #   await process_latest_report_py(callback_context)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.genai.types.Part;
        import io.reactivex.rxjava3.core.MaybeObserver;
        import io.reactivex.rxjava3.disposables.Disposable;
        import java.util.Optional;

        public class MyArtifactLoaderService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactLoaderService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            public void processLatestReportJava(String userId, String sessionId, String filename) {
                // 透過傳遞 Optional.empty() 來載入最新版本
                artifactService
                        .loadArtifact(appName, userId, sessionId, filename, Optional.empty())
                        .subscribe(
                                new MaybeObserver<Part>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // 可選：處理訂閱
                                    }

                                    @Override
                                    public void onSuccess(Part reportArtifact) {
                                        System.out.println(
                                                "成功載入最新的 Java 產物 '" + filename + "'。");
                                        reportArtifact
                                                .inlineData()
                                                .ifPresent(
                                                        blob -> {
                                                            System.out.println(
                                                                    "MIME 類型：" + blob.mimeType().orElse("N/A"));
                                                            byte[] pdfBytes = blob.data().orElse(new byte[0]);
                                                            System.out.println("報告大小：" + pdfBytes.length + " 位元組。");
                                                            // ... 進一步處理 pdfBytes ...
                                                        });
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        // 處理潛在的儲存錯誤或其他例外
                                        System.err.println(
                                                "載入 Java 產物 '"
                                                        + filename
                                                        + "' 時發生錯誤："
                                                        + e.getMessage());
                                    }

                                    @Override
                                    public void onComplete() {
                                        // 如果找不到產物 (最新版本)，則呼叫此方法
                                        System.out.println("找不到 Java 產物 '" + filename + "'。");
                                    }
                                });

                // 範例：載入特定版本 (例如版本 0)
                /*
                artifactService.loadArtifact(appName, userId, sessionId, filename, Optional.of(0))
                    .subscribe(part -> {
                        System.out.println("已載入 Java 產物 '" + filename + "' 的版本 0。");
                    }, throwable -> {
                        System.err.println("載入 '" + filename + "' 的版本 0 時發生錯誤：" + throwable.getMessage());
                    }, () -> {
                        System.out.println("找不到 Java 產物 '" + filename + "' 的版本 0。");
                    });
                */
            }

            // --- 範例用法概念 (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // 或 GcsArtifactService
                // MyArtifactLoaderService loader = new MyArtifactLoaderService(service, "myJavaApp");
                // loader.processLatestReportJava("user123", "sessionABC", "java_report.pdf");
                // 由於非同步性質，在真實應用程式中，請確保程式等待或處理完成。
            }
        }
        ```

#### 列出產物檔名

*   **程式碼範例：**

    === "Python"

        ```python
        from google.adk.tools.tool_context import ToolContext

        def list_user_files_py(tool_context: ToolContext) -> str:
            """列出使用者可用產物的工具。"""
            try:
                available_files = await tool_context.list_artifacts()
                if not available_files:
                    return "您沒有任何已儲存的產物。"
                else:
                    # 為使用者/LLM 格式化列表
                    file_list_str = "\n".join([f"- {fname}" for fname in available_files])
                    return f"以下是您可用的 Python 產物：\n{file_list_str}"
            except ValueError as e:
                print(f"列出 Python 產物時出錯：{e}。是否已設定 ArtifactService？")
                return "錯誤：無法列出 Python 產物。"
            except Exception as e:
                print(f"列出 Python 產物時發生意外錯誤：{e}")
                return "錯誤：列出 Python 產物時發生意外錯誤。"

        # 此函式通常會包裝在 FunctionTool 中
        # from google.adk.tools import FunctionTool
        # list_files_tool = FunctionTool(func=list_user_files_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.ListArtifactsResponse;
        import com.google.common.collect.ImmutableList;
        import io.reactivex.rxjava3.core.SingleObserver;
        import io.reactivex.rxjava3.disposables.Disposable;

        public class MyArtifactListerService {

            private final BaseArtifactService artifactService;
            private final String appName;

            public MyArtifactListerService(BaseArtifactService artifactService, String appName) {
                this.artifactService = artifactService;
                this.appName = appName;
            }

            // 可能由工具或代理邏輯呼叫的範例方法
            public void listUserFilesJava(String userId, String sessionId) {
                artifactService
                        .listArtifactKeys(appName, userId, sessionId)
                        .subscribe(
                                new SingleObserver<ListArtifactsResponse>() {
                                    @Override
                                    public void onSubscribe(Disposable d) {
                                        // 可選：處理訂閱
                                    }

                                    @Override
                                    public void onSuccess(ListArtifactsResponse response) {
                                        ImmutableList<String> availableFiles = response.filenames();
                                        if (availableFiles.isEmpty()) {
                                            System.out.println(
                                                    "使用者 "
                                                            + userId
                                                            + " 在工作階段 "
                                                            + sessionId
                                                            + " 中沒有已儲存的 Java 產物。");
                                        } else {
                                            StringBuilder fileListStr =
                                                    new StringBuilder(
                                                            "以下是使用者 "
                                                                    + userId
                                                                    + " 在工作階段 "
                                                                    + sessionId
                                                                    + " 中可用的 Java 產物：\n");
                                            for (String fname : availableFiles) {
                                                fileListStr.append("- ").append(fname).append("\n");
                                            }
                                            System.out.println(fileListStr.toString());
                                        }
                                    }

                                    @Override
                                    public void onError(Throwable e) {
                                        System.err.println(
                                                "為使用者 "
                                                        + userId
                                                        + " 在工作階段 "
                                                        + sessionId
                                                        + " 中列出 Java 產物時發生錯誤："
                                                        + e.getMessage());
                                        // 在真實應用程式中，您可能會向使用者/LLM 傳回錯誤訊息
                                    }
                                });
            }

            // --- 範例用法概念 (Java) ---
            public static void main(String[] args) {
                // BaseArtifactService service = new InMemoryArtifactService(); // 或 GcsArtifactService
                // MyArtifactListerService lister = new MyArtifactListerService(service, "myJavaApp");
                // lister.listUserFilesJava("user123", "sessionABC");
                // 由於非同步性質，在真實應用程式中，請確保程式等待或處理完成。
            }
        }
        ```

這些用於儲存、載入和列出的方法提供了一種方便且一致的方式來管理 ADK 中的二進位資料持續性，無論是使用 Python 的上下文物件還是在 Java 中直接與 `BaseArtifactService` 互動，都與所選的後端儲存實作無關。

## 可用實作

ADK 提供了 `BaseArtifactService` 介面的具體實作，為各種開發階段和部署需求提供不同的儲存後端。這些實作根據 `app_name`、`user_id`、`session_id` 和 `filename` (包括 `user:` 命名空間前置詞) 處理儲存、版本控制和擷取產物資料的細節。

### InMemoryArtifactService

*   **儲存機制：**
    *   Python：使用保存在應用程式記憶體中的 Python 字典 (`self.artifacts`)。字典鍵代表產物路徑，值是 `types.Part` 的列表，其中每個列表元素都是一個版本。
    *   Java：使用保存在記憶體中的巢狀 `HashMap` 實例 (`private final Map<String, Map<String, Map<String, Map<String, List<Part>>>>> artifacts;`)。每個層級的鍵分別是 `appName`、`userId`、`sessionId` 和 `filename`。最內層的 `List<Part>` 儲存產物的版本，其中列表索引對應於版本號碼。
*   **主要功能：**
    *   **簡單性：** 除了核心 ADK 函式庫外，不需要任何外部設定或相依性。
    *   **速度：** 操作通常非常快，因為它們涉及記憶體內的地圖/字典查詢和列表操作。
    *   **短暫性：** 當應用程式程序終止時，所有儲存的產物都會**遺失**。資料不會在應用程式重新啟動之間持續存在。
*   **使用案例：**
    *   非常適合不需要持續性的本地開發和測試。
    *   適用於短暫的示範或產物資料在單次應用程式執行中純粹是臨時的場景。
*   **實例化：**

    === "Python"

        ```python
        from google.adk.artifacts import InMemoryArtifactService

        # 只需實例化類別
        in_memory_service_py = InMemoryArtifactService()

        # 然後將其傳遞給 Runner
        # runner = Runner(..., artifact_service=in_memory_service_py)
        ```

    === "Java"

        ```java
        import com.google.adk.artifacts.BaseArtifactService;
        import com.google.adk.artifacts.InMemoryArtifactService;

        public class InMemoryServiceSetup {
            public static void main(String[] args) {
                // 只需實例化類別
                BaseArtifactService inMemoryServiceJava = new InMemoryArtifactService();

                System.out.println("InMemoryArtifactService (Java) 已實例化：" + inMemoryServiceJava.getClass().getName());

                // 然後此實例將提供給您的 Runner。
                // Runner runner = new Runner(
                //     /* 其他服務 */,
                //     inMemoryServiceJava
                // );
            }
        }
        ```

### GcsArtifactService


*   **儲存機制：** 利用 Google Cloud Storage (GCS) 進行持續性產物儲存。產物的每個版本都作為一個單獨的物件 (blob) 儲存在指定的 GCS 儲存桶中。
*   **物件命名慣例：** 它使用層級路徑結構建構 GCS 物件名稱 (blob 名稱)。
*   **主要功能：**
    *   **持續性：** 儲存在 GCS 中的產物在應用程式重新啟動和部署之間持續存在。
    *   **可擴展性：** 利用 Google Cloud Storage 的可擴展性和耐用性。
    *   **版本控制：** 明確地將每個版本儲存為一個不同的 GCS 物件。`GcsArtifactService` 中的 `saveArtifact` 方法。
    *   **所需權限：** 應用程式環境需要適當的憑證 (例如，應用程式預設憑證) 和 IAM 權限才能讀取和寫入指定的 GCS 儲存桶。
*   **使用案例：**
    *   需要持續性產物儲存的生產環境。
    *   需要跨不同應用程式實例或服務共用產物的場景 (透過存取同一個 GCS 儲存桶)。
    *   需要長期儲存和擷取使用者或工作階段資料的應用程式。
*   **實例化：**

    === "Python"

        ```python
        from google.adk.artifacts import GcsArtifactService

        # 指定 GCS 儲存桶名稱
        gcs_bucket_name_py = "your-gcs-bucket-for-adk-artifacts" # 用您的儲存桶名稱取代

        try:
            gcs_service_py = GcsArtifactService(bucket_name=gcs_bucket_name_py)
            print(f"已為儲存桶初始化 Python GcsArtifactService：{gcs_bucket_name_py}")
            # 確保您的環境具有存取此儲存桶的憑證。
            # 例如，透過應用程式預設憑證 (ADC)

            # 然後將其傳遞給 Runner
            # runner = Runner(..., artifact_service=gcs_service_py)

        except Exception as e:
            # 捕捉 GCS 用戶端初始化期間的潛在錯誤 (例如，身份驗證問題)
            print(f"初始化 Python GcsArtifactService 時出錯：{e}")
            # 適當地處理錯誤 - 可能會退回到 InMemory 或引發
        ```

    === "Java"

        ```java
        --8<-- "examples/java/snippets/src/main/java/artifacts/GcsServiceSetup.java:full_code"
        ```

選擇適當的 `ArtifactService` 實作取決於您的應用程式對資料持續性、可擴展性和操作環境的需求。

## 最佳實務

為了有效且可維護地使用產物：

* **選擇正確的服務：** 對於快速原型設計、測試以及不需要持續性的場景，請使用 `InMemoryArtifactService`。對於需要資料持續性和可擴展性的生產環境，請使用 `GcsArtifactService` (或為其他後端實作您自己的 `BaseArtifactService`)。
* **有意義的檔名：** 使用清晰、描述性的檔名。包括相關的副檔名 (`.pdf`、`.png`、`.wav`) 有助於人類理解內容，儘管 `mime_type` 決定了程式化的處理方式。為臨時產物與持續性產物名稱建立慣例。
* **指定正確的 MIME 類型：** 在為 `save_artifact` 建立 `types.Part` 時，務必提供準確的 `mime_type`。這對於稍後 `load_artifact` 以正確解譯 `bytes` 資料的應用程式或工具至關重要。盡可能使用標準的 IANA MIME 類型。
* **了解版本控制：** 請記住，不帶特定 `version` 引數的 `load_artifact()` 會擷取*最新*版本。如果您的邏輯依賴於產物的特定歷史版本，請務必在載入時提供整數版本號碼。
* **謹慎使用命名空間 (`user:`)：** 僅當資料真正屬於使用者且應可在其所有工作階段中存取時，才對檔名使用 `"user:"` 前置詞。對於特定於單次對話或工作階段的資料，請使用不帶前置詞的一般檔名。
* **錯誤處理：**
    * 在呼叫上下文方法 (`save_artifact`、`load_artifact`、`list_artifacts`) 之前，務必檢查是否實際設定了 `artifact_service`——如果服務為 `None`，它們將引發 `ValueError`。
    * 檢查 `load_artifact` 的傳回值，如果產物或版本不存在，它將為 `None`。不要假設它總是傳回 `Part`。
    * 準備好處理來自底層儲存服務的例外，特別是使用 `GcsArtifactService` 時 (例如，權限問題的 `google.api_core.exceptions.Forbidden`、儲存桶不存在時的 `NotFound`、網路錯誤)。
* **大小考量：** 產物適用於典型的檔案大小，但要注意極大檔案的潛在成本和效能影響，特別是對於雲端儲存。如果儲存許多大型產物，`InMemoryArtifactService` 可能會消耗大量記憶體。評估非常大的資料是否最好透過直接的 GCS 連結或其他專門的儲存解決方案來處理，而不是在記憶體中傳遞整個位元組陣列。
* **清理策略：** 對於像 `GcsArtifactService` 這樣的持續性儲存，產物會一直保留到明確刪除為止。如果產物代表臨時資料或具有有限的生命週期，請實作清理策略。這可能涉及：
    * 在儲存桶上使用 GCS 生命週期原則。
    * 建構利用 `artifact_service.delete_artifact` 方法的特定工具或管理功能 (注意：為了安全起見，刪除*不會*透過上下文物件公開)。
    * 仔細管理檔名，以便在需要時允許基於模式的刪除。
