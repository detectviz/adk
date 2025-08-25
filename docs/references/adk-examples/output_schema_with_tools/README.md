# 帶有工具的輸出結構 (Output Schema) 範例代理

此範例示範如何在 ADK 代理中將結構化輸出 (`output_schema`) 與其他工具一起使用。以前不允許這種組合，但現在透過處理互動的特殊處理器支援這種組合。

## 運作方式

代理結合了：
- **工具**：用於收集資訊的 `search_wikipedia` 和 `get_current_year`
- **結構化輸出 (Structured Output)**：`PersonInfo` 結構 (schema) 以確保一致的回應格式

當同時指定 `output_schema` 和 `tools` 時：
1. ADK 會自動新增一個特殊的 `set_model_response` 工具
2. 模型可以使用常規工具進行資訊收集
3. 對於最終回應，模型會使用帶有結構化資料的 `set_model_response`
4. ADK 會擷取並驗證結構化回應

## 預期回應格式

對於使用者查詢「告訴我關於愛因斯坦的資訊」，代理將以此結構化格式傳回資訊：

```json
{
  "name": "Albert Einstein",
  "age": 76,
  "occupation": "Theoretical Physicist",
  "location": "Princeton, New Jersey, USA",
  "biography": "German-born theoretical physicist who developed the theory of relativity..."
}
```

## 主要功能展示

1. **工具使用**：代理可以搜尋維基百科並取得目前年份
2. **結構化輸出 (Structured Output)**：回應遵循嚴格的 PersonInfo 結構 (schema)
3. **驗證**：ADK 會驗證回應是否符合結構 (schema)
4. **靈活性**：適用於任何工具和輸出結構 (schema) 的組合
