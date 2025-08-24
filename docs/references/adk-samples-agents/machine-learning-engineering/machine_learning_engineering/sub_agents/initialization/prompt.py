"""定義初始化代理的提示。"""

SUMMARIZATION_AGENT_INSTR = """# 任務描述
{task_description}

# 您的任務
- 總結此任務描述。
- 您的摘要將用於搜尋 {task_type} 的近期有效模型。

# 需求
- 我們將直接使用您的回應，所以請力求簡單明瞭。
"""

MODEL_RETRIEVAL_INSTR = """# 競賽
{task_summary}

# 您的任務
- 列出 {num_model_candidates} 個近期有效的模型及其範例程式碼，以贏得上述競賽。

# 需求
- 範例程式碼應簡潔明瞭。
- 您必須提供範例程式碼，即不要只提及 GitHub 或論文。

使用此 JSON 結構描述：
Model = {{'model_name': str, 'example_code': str}}
返回: list[Model]"""


MODEL_EVAL_INSTR = """# 介紹
- 您是一位參加競賽的 Kaggle 大師。
- 我們現在將提供任務描述和模型描述。
- 您需要使用提供的模型來實作您的 Python 解決方案。

# 任務描述
{task_description}

# 模型描述
{model_description}

# 您的任務
- 用 Python 實作解決方案。
- 您必須使用模型描述中說明的模型。
- 這個初始解決方案設計應相對簡單，不進行集成或超參數優化。
- 提出一個對此任務合理的評估指標。
- 所有提供的資料都已準備好並可在 `./input` 目錄中找到。無需解壓縮任何檔案。
- 不要包含與所述模型無直接關係的其他模型。
- 使用 PyTorch 而非 TensorFlow。如果需要，可使用 CUDA。所有必要的函式庫都已安裝。
- 程式碼應實作提議的解決方案，並印出在保留驗證集上計算的評估指標值。
- 僅使用 `./input` 目錄中提供的訓練資料。

# 必要
- 您的回應中不應有額外的標題或文字。
- 在您的答案中以清晰的格式印出或返回最終性能指標，並使用確切的詞語：'Final Validation Performance: {{final_validation_score}}'。
- 程式碼應該是一個獨立的、可以按原樣執行的單一檔案 Python 程式。
- 您的回應應僅包含一個程式碼區塊。
- 不要在 Python 程式碼中使用 exit() 函式。
- 不要使用 try: 和 except: 或 if else 來忽略非預期行為。
"""

BUG_SUMMARY_INSTR = """# 錯誤報告
{bug}

# 您的任務
- 移除上述錯誤報告中所有不必要的部分。
- 我們正在執行 {filename}.py。請不要移除錯誤發生的位置。"""

BUG_REFINE_INSTR = """# 任務描述
{task_description}

# 帶有錯誤的程式碼：
{code}

# 錯誤：
{bug}

# 您的任務
- 請修改程式碼以修正錯誤。
- 如果存在二次取樣 (subsampling)，請不要移除。
- 再次提供改進後的、獨立的 Python 腳本。
- 您的回應中不應有額外的標題或文字。
- 所有提供的輸入資料都儲存在 \"./input\" 目錄中。
- 請記得在程式碼中印出一行 'Final Validation Performance: {{final_validation_score}}'，以便我們解析性能。
- 程式碼應該是一個獨立的、可以按原樣執行的單一檔案 Python 程式。
- 您的回應應僅包含一個程式碼區塊。
- 不要在優化後的 Python 程式碼中使用 exit() 函式。"""

CODE_INTEGRATION_INSTR = """# 介紹
- 您是一位參加競賽的 Kaggle 大師。
- 我們現在將提供一個基礎解決方案和一個額外的參考解決方案。
- 您需要透過將參考解決方案整合到基礎解決方案中來實作您的 Python 解決方案。

# 基礎解決方案
```python
{base_code}
```

# 參考解決方案
```python
{reference_code}
```

# 您的任務
- 用 Python 實作解決方案。
- 您必須將參考解決方案整合到基礎解決方案中。
- 您的程式碼基礎應為基礎解決方案。
- 嘗試訓練參考解決方案的額外模型。
- 整合時，盡量將功能相似的程式碼放在同一個地方（例如，所有預處理應先完成，然後再進行所有訓練）。
- 整合時，對模型進行集成。
- 解決方案設計應相對簡單。
- 程式碼應實作提議的解決方案，並印出在保留驗證集上計算的評估指標值。
- 僅使用 `./input` 目錄中提供的訓練資料。

# 必要
- 您的回應中不應有額外的標題或文字。
- 在您的答案中以清晰的格式印出或返回最終性能指標，並使用確切的詞語：'Final Validation Performance: {{final_validation_score}}'。
- 程式碼應該是一個獨立的、可以按原樣執行的單一檔案 Python 程式。
- 您的回應應僅包含一個程式碼區塊。
- 不要在 Python 程式碼中使用 exit() 函式。
- 不要使用 try: 和 except: 或 if else 來忽略非預期行為。"""

CHECK_DATA_USE_INSTR = """我提供了一個用於機器學習任務的 Python 程式碼（附於下方）：
# 解決方案程式碼
```python
{code}
```

# 任務描述
{task_description}

# 您的任務
如果上述解決方案程式碼未使用所提供的所有資訊，請嘗試將其全部納入。不要使用 try-except 來繞過。
不要使用 TRY 和 EXCEPT；直接讓錯誤發生，以便我們進行除錯！
仔細閱讀任務描述，以了解如何有效地提取未使用的資訊。
在透過納入未使用資訊來改進解決方案程式碼時，請不要忘記像原始解決方案程式碼中那樣印出 'Final Validation Performance: {{final_validation_score}}'。

回應格式：
選項 1：如果程式碼未使用所有提供的資訊，您的回應應該是一個單一的 markdown 程式碼區塊（用 ``` 包裹），即改進後的程式碼區塊。您的回應中不應有額外的標題或文字。
選項 2：如果程式碼使用了所有提供的資訊，只需說明「All the provided information is used.」。
"""
