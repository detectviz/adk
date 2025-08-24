---
hide:
  - toc
---

<div style="text-align: center;">
  <div class="centered-logo-text-group">
    ![代理開發套件 (Agent Development Kit) Logo](assets/agent-development-kit.png){ width="100" }
    # 代理開發套件 (Agent Development Kit)
  </div>
</div>

## 代理開發套件 (Agent Development Kit) 是什麼？

代理開發套件 (Agent Development Kit, ADK) 是一個彈性且模組化的框架，用於**開發和部署 AI 代理**。雖然 ADK 針對 Gemini 和 Google 生態系統進行了優化，但它**模型無關 (model-agnostic)**、**部署無關 (deployment-agnostic)**，並且旨在**與其他框架相容**。ADK 的設計旨在讓代理開發更貼近軟體開發，使開發人員能更容易地創建、部署和協調從簡單任務到複雜工作流程的代理架構。

<div id="centered-install-tabs" class="install-command-container" markdown="1">

<div style="text-align: center;">快速入門：</div>

=== "Python"

    <div style="text-align: center;">
    `pip install google-adk`
    </div>

=== "Java"

    ```xml title="pom.xml"
    <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.1.0</version>
    </dependency>
    ```

    ```gradle title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.1.0'
    }
    ```
</div>


<div style="text-align:center;">
[快速入門](get-started-quickstart.md){: .md-button }
[教學](tutorials.md){: .md-button }
[範例代理](http://github.com/google/adk-samples){: .md-button target="_blank" }
[API 參考](api-reference.md){: .md-button }
[貢獻 ❤️](contributing-guide.md){: .md-button }
</div>

---

## 了解更多

[:fontawesome-brands-youtube:{.youtube-red-icon} 觀看「代理開發套件 (Agent Development Kit) 介紹」！](https://www.youtube.com/watch?v=zgrOwow_uTQ target="_blank" rel="noopener noreferrer")

<div class="grid cards" markdown>

-   :material-transit-connection-variant: **彈性的協調 (Flexible Orchestration)**

    ---

    使用工作流程代理 (`Sequential`、`Parallel`、`Loop`) 定義可預測的工作流程，或利用大型語言模型 (LLM) 驅動的動態路由 (`LlmAgent` 轉移) 來實現適應性行為。

    [**了解代理**](agents.md)

-   :material-graph: **多代理架構 (Multi-Agent Architecture)**

    ---

    透過在層次結構中組合多個專業代理來建構模組化且可擴展的應用程式。實現複雜的協調和委派。

    [**探索多代理系統**](agents-multi-agents.md)

-   :material-toolbox-outline: **豐富的工具生態系 (Rich Tool Ecosystem)**

    ---

    為代理配備多樣化的功能：使用預先建置的工具 (搜尋、程式碼執行)、建立自訂函式、整合第三方函式庫 (LangChain、CrewAI)，甚至將其他代理當作工具使用。

    [**瀏覽工具**](tools.md)

-   :material-rocket-launch-outline: **可隨時部署 (Deployment Ready)**

    ---

    將您的代理容器化並部署到任何地方——在本地運行、使用 Vertex AI 代理引擎 (Agent Engine) 進行擴展，或使用 Cloud Run 或 Docker 整合到自訂基礎設施中。

    [**部署代理**](deploy.md)

-   :material-clipboard-check-outline: **內建評估 (Built-in Evaluation)**

    ---

    透過評估最終回應品質和針對預定義測試案例的逐步執行軌跡，系統性地評估代理性能。

    [**評估代理**](evaluate.md)

-   :material-console-line: **建構安全可靠的代理**

    ---

    了解如何透過在代理設計中實施安全模式和最佳實踐來建構強大且值得信賴的代理。

    [**安全與保障**](safety.md)

</div>
