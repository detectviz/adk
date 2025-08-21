"""定義用於除錯的提示。"""

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
- 如果錯誤是 'module not found' (找不到模組) 錯誤，則安裝必要的模組。您可以使用 `pip install <module>`，其中 `<module>` 是要安裝的模組名稱。
- 如果存在二次取樣 (subsampling)，請不要移除。
- 再次提供改進後的、獨立的 Python 腳本。
- 您的回應中不應有額外的標題或文字。
- 所有提供的輸入資料都儲存在 \"./input\" 目錄中。
- 請記得在程式碼中印出一行 'Final Validation Performance: {{final_validation_score}}'，以便我們解析性能。
- 程式碼應該是一個獨立的、可以按原樣執行的單一檔案 Python 程式。
- 您的回應應僅包含一個程式碼區塊。
- 不要在優化後的 Python 程式碼中使用 exit() 函式。"""
