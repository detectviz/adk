# Google SRE Book 核心原則與實踐

- 原出處：[Google SRE Book](https://sre.google/sre-book/)

本文檔旨在提煉 Google SRE 書籍的核心思想，為 Google Agent Development Kit (ADK) 中的 AI 代理提供站點可靠性工程（Site Reliability Engineering）的最佳實踐與知識基礎。

## 目錄

[https://sre.google/sre-book](https://sre.google/sre-book)

- [第一部分 - 前言](google-sre-book/Part-I-Introduction.md)
- [1. 前言](google-sre-book/Chapter-01-Introduction.md)
- [2. 從 SRE 的角度看 Google 的生產環境](google-sre-book/Chapter-02-The-Production-Environment-at-Googlefrom-the.md)
- [第二部分 - 原則](google-sre-book/Part-II-Principles.md)
- [3. 擁抱風險](google-sre-book/Chapter-03-Embracing-Risk.md)
- [4. 服務水準目標 (Service Level Objectives)](google-sre-book/Chapter-04-Service-Level-Objectives.md)
- [5. 消除瑣務 (Eliminating Toil)](google-sre-book/Chapter-05-Eliminating-Toil.md)
- [6. 監控分散式系統](google-sre-book/Chapter-06-Monitoring-Distributed-Systems.md)
- [7. Google 自動化的演進](google-sre-book/Chapter-07-The-Evolution-of-Automation-at-Google.md)
- [8. 發布工程 (Release Engineering)](google-sre-book/Chapter-08-Release-Engineering.md)
- [9. 簡潔性](google-sre-book/Chapter-09-Simplicity.md)
- [第三部分 - 實踐](google-sre-book/Part-III-Practices.md)
- [10. 實用警報](google-sre-book/Chapter-10-Practical-Alerting.md)
- [11. 值班 (On-Call)](google-sre-book/Chapter-11-Being-On-Call.md)
- [12. 高效的故障排除](google-sre-book/Chapter-12-Effective-Troubleshooting.md)
- [13. 緊急應變](google-sre-book/Chapter-13-Emergency-Response.md)
- [14. 事件管理](google-sre-book/Chapter-14-Managing-Incidents.md)
- [15. 事後檢討文化：從失敗中學習](google-sre-book/Chapter-15-Postmortem-CultureLearning-from-Failure.md)
- [16. 追蹤服務中斷](google-sre-book/Chapter-16-Tracking-Outages.md)
- [17. 可靠性測試](google-sre-book/Chapter-17-Testing-for-Reliability.md)
- [18. SRE 中的軟體工程](google-sre-book/Chapter-18-Software-Engineering-in-SRE.md)
- [19. 前端負載平衡](google-sre-book/Chapter-19-Load-Balancing-at-the-Frontend.md)
- [20. 資料中心的負載平衡](google-sre-book/Chapter-20-Load-Balancing-in-the-Datacenter.md)
- [21. 處理過載](google-sre-book/Chapter-21-Handling-Overload.md)
- [22. 解決連鎖故障](google-sre-book/Chapter-22-Addressing-Cascading-Failures.md)
- [23. 管理關鍵狀態：為可靠性而生的分散式共識](google-sre-book/Chapter-23-Managing-Critical-StateDistributed-Consensu.md)
- [24. 使用 Cron 進行分散式定期排程](google-sre-book/Chapter-24-Distributed-Periodic-Scheduling-with-Cron.md)
- [25. 資料處理管線](google-sre-book/Chapter-25-Data-Processing-Pipelines.md)
- [26. 資料完整性：所讀即所寫](google-sre-book/Chapter-26-Data-IntegrityWhat-You-Read-Is-What-You-Wro.md)
- [27. 可靠的大規模產品發布](google-sre-book/Chapter-27-Reliable-Product-Launches-at-Scale.md)
- [第四部分 - 管理](google-sre-book/Part-IV-Management.md)
- [28. 加速 SRE 的值班與後續發展](google-sre-book/Chapter-28-Accelerating-SREs-to-On-Call-and-Beyond.md)
- [29. 處理中斷](google-sre-book/Chapter-29-Dealing-with-Interrupts.md)
- [30. 嵌入 SRE 以從運營過載中恢復](google-sre-book/Chapter-30-Embedding-an-SRE-to-Recover-from-Operational.md)
- [31. SRE 中的溝通與協作](google-sre-book/Chapter-31-Communication-and-Collaboration-in-SRE.md)
- [32. 不斷演進的 SRE 參與模型](google-sre-book/Chapter-32-The-Evolving-SRE-Engagement-Model.md)
- [第五部分 - 結論](google-sre-book/Part-V-Conclusions.md)
- [33. 從其他行業學到的教訓](google-sre-book/Chapter-33-Lessons-Learned-from-Other-Industries.md)
- [34. 結論](google-sre-book/Chapter-34-Conclusion.md)
- [附錄 A. 可用性表格](google-sre-book/Appendix-A-Availability-Table.md)
- [附錄 B. 生產服務最佳實踐集合](google-sre-book/Appendix-B-A-Collection-of-Best-Practices-for-Production.md)
- [附錄 C. 事件狀態文件範例](google-sre-book/Appendix-C-Example-Incident-State-Document.md)
- [附錄 D. 事後檢討範例](google-sre-book/Appendix-D-Example-Postmortem.md)
- [附錄 E. 發布協調清單](google-sre-book/Appendix-E-Launch-Coordination-Checklist.md)
- [附錄 F. 生產會議記錄範例](google-sre-book/Appendix-F-Example-Production-Meeting-Minutes.md)

---

## 1. [SRE 量化指標](docs/references/google-sre-book/Chapter-04-Service-Level-Objectives.md)

SRE 依靠數據驅動決策，以下是其核心的量化指標：

-   **服務水平指標 (SLI - Service Level Indicator)**
    -   **定義**：對服務某個方面性能的量化測量。它是關於「什麼是好的」的直接證據。
    -   **範例**：請求延遲（Request Latency）、錯誤率（Error Rate）、系統吞吐量（Throughput）、可用性（Availability）。
    -   **實踐**：應使用百分位數（如 99% 或 99.9%）來測量，而非平均值，因為平均值會掩蓋影響用戶體驗的長尾效應。

-   **服務水平目標 (SLO - Service Level Objective)**
    -   **定義**：為 SLI 設定的目標值或範圍。這是 SRE 團隊承諾達成的可靠性目標。
    -   **範例**：`99.9% 的請求延遲 < 100ms`。
    -   **作用**：SLO 是內部驅動開發和運維工作的核心，它直接決定了錯誤預算。

-   **服務水平協議 (SLA - Service Level Agreement)**
    -   **定義**：與用戶簽訂的正式合約，通常包含未達到 SLO 時的後果（如賠償）。SLA 是業務和法律層面的承諾。

-   [錯誤預算 (Error Budget)](docs/references/google-sre-book/Appendix-B-A-Collection-of-Best-Practices-for-Production.md)
    -   **定義**：`1 - SLO`。這是服務在不違反 SLO 的前提下，可以容忍的「不可靠」程度。
    -   **作用**：它是一個數據化的決策工具。只要錯誤預算未用盡，開發團隊就可以自由發布新功能；一旦預算耗盡，則凍結所有非緊急的變更，專注於提升系統穩定性。

-   **平均故障間隔 (MTBF - Mean Time Between Failures)**
    -   **定義**：系統可以無故障運行的平均時間。

-   **平均修復時間 (MTTR - Mean Time To Repair)**
    -   **定義**：從檢測到故障到完全修復所需的平均時間。SRE 更關注最小化 MTTR，因為故障不可避免，但快速恢復是維持高可用性的關鍵。

---

## 2. 關鍵原則

- [消除瑣事 (Eliminating Toil)](docs/references/google-sre-book/Chapter-05-Eliminating-Toil.md)：瑣事（Toil）指那些手動的、重複的、可被自動化的、戰術性的、缺乏長期價值的工作。它是工程師時間的殺手，過多的瑣事會導致團隊停滯不前。SRE 的目標是透過工程手段將其消除。
-   **工程優先於手動操作**：SRE 的核心是自動化。任何重複的、無創造性的手動工作（Toil）都應被視為工程問題，並透過開發工具或重構系統來解決。
-   **以錯誤預算平衡創新與穩定**：錯誤預算是一個數據驅動的決策框架，它消除了開發與運維之間的對立。它允許團隊在不犧牲用戶體驗的前提下，承擔經過計算的風險以加速創新。
- [確保構建過程的密封性 (Hermetic Builds)](docs/references/google-sre-book/Chapter-08-Release-Engineering.md)：構建過程必須是自包含且可重現的，不應依賴於主機環境中安裝的函式庫或工具。這確保了在任何地方、任何時間構建同一個原始碼版本，都會得到完全相同的結果。

---

## 3. 根本原因分析 (Postmortem & 5 Whys)

-   [無指責的事後檢討 (Blame-free Postmortem)](docs/references/google-sre-book/Chapter-15-Postmortem-CultureLearning-from-Failure.md)：
    -   **目的**：從失敗中學習，而不是追究個人責任。焦點應放在改進系統、流程和工具上。
    -   [五個為什麼 (5 Whys)」根本原因分析模板](docs/references/google-sre-book/Appendix-D-Example-Postmortem.md)：
        1.  **問題：** *[清晰、高層次地描述問題。例如：服務 X 的錯誤率在 Y 時間點超過了 SLO。]*
            -   **為什麼會發生？**
        2.  **第一個為什麼：** *[直接原因。例如：後端數據庫因請求過多而超時。]*
            -   **為什麼會這樣？**
        3.  **第二個為什麼：** *[更深層次的原因。例如：一個新發布的功能在特定條件下會觸發 N+1 查詢。]*
            -   **為什麼會這樣？**
        4.  **第三個為什麼：** *[再深一層的原因。例如：該功能的程式碼審查未能識別出 N+1 查詢的風險。]*
            -   **為什麼會這樣？**
        5.  **第四個為什麼：** *[流程或系統設計上的原因。例如：我們的自動化測試套件沒有覆蓋這種特定數據模式的集成測試。]*
            -   **為什麼會這樣？**
        6.  **第五個為什麼 (根本原因)：** *[根本的、可預防的系統性問題。例如：我們缺乏一個標準化的性能測試流程來作為發布前的門禁。]*

---

## 4. 人工介入審批流程 (HITL)

-   [為人工介入 (Human-in-the-Loop, HITL) 審批流程建立測試](docs/references/google-sre-book/Chapter-17-Testing-for-Reliability.md)：
    -   **核心思想**：不直接測試「人」，而是測試支撐「人」做出正確決策的系統和流程。
    -   **測試方法**：
        1.  **配置測試 (Configuration Tests)**：編寫自動化測試，持續驗證生產環境中的實時配置與版本控制系統中的預期配置是否一致，以捕捉未經授權或錯誤的手動變更。
        2.  **對審批工具進行測試**：為人工審批所依賴的工具（如部署儀表板、回滾腳本）建立完善的單元測試和集成測試。
        3.  **“打破玻璃”機制的測試**：緊急手動操作（Break-Glass）應被設計為一個“有噪音”的事件。該操作應自動觸發告警、記錄審計日誌、並創建一個高優先級的事後跟進工單。測試應確保這些後續動作被正確觸發。
        4.  **災難恢復演練 (Disaster Recovery Testing, DiRT)**：定期舉行大規模演習，在真實生產環境中測試整個應急響應流程，包括人的決策和溝通協作。

---

## 5. 變更管理

-   **自動化、漸進式的變更管理**：
    -   **發布流程**：所有變更都應被自動化管理。發布應從主幹（mainline）創建分支，修復則以 cherry-pick 的方式合入，確保發布內容的純淨。
    -   **漸進式部署 (Progressive Rollouts)**：絕不一次性將變更推向所有用戶。應分階段、分區域地進行部署（金絲雀發布），在每個階段密切監控系統指標。
    -   **自動回滾**：一旦發現異常，立即自動回滾，先恢復服務再進行問題診斷。

-   [解耦配置與二進制文件](docs/references/google-sre-book/Chapter-08-Release-Engineering.md)：配置文件的變更和二進制文件的發布應作為獨立的單元進行管理和部署。這提供了更高的靈活性，允許在不重新構建整個服務的情況下快速修改配置。