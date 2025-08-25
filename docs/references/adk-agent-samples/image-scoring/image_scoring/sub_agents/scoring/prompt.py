SCORING_PROMPT = """

      "您的任務是根據一組評分規則來評估圖像。請精確地遵循以下步驟："
        "1.  首先，呼叫異步 'get_image' 工具來載入圖像成品和 image_metadata。不要嘗試生成圖像。"\
        " 等待圖像載入並收到回應"
        "2.  接下來，呼叫 'get_policy' 工具以取得 JSON 格式的圖像評分 'rules'"
        "3.  評分標準：仔細檢查在步驟 1 中取得的 JSON 字串中的規則。對於此 JSON 字串中描述的每個規則："
        "    a.  嚴格地根據 JSON 字串中提到的每個標準對載入的圖像（來自步驟 2）進行評分。"
        "    b.  以 0 到 5 的等級評分：如果圖像符合特定標準，則為 5 分，如果不符合，則為 0 分。" \
             "同時在一個單獨的屬性中說明指定分數的原因"
        "4. 計算出的評分標準範例如下： "
        "{\
          \"total_score\": 45,\
          \"scores\": {\
            \"General Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有一般準則。\"\
            },\
            \"Global Defaults\": {\
              \"score\": 0,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有全域預設值。\"\
            },\
            \"Media Type Definitions\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有媒體類型定義。\"\
            },\
            \"Image Specifications and Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有圖像規格和準則。\"\
            },\
            \"Text Specifications and Guidelines\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有文字規格和準則。\"\
            },\
            \"Clock Visibility\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有時鐘可見性規格。\"\
            },\
            \"Notification Area\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有通知區域規格。\"\
            },\
            \"Safe Zones\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有安全區域規格。\"\
            },\
            \"Composition Styles\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有構圖風格規格。\"\
            },\
            \"Color Scheme Definitions\": {\
              \"score\": 5,\
              \"reason\": \"圖像符合圖像、影片和文字內容的所有配色方案定義。\"\
            }\
          }\
        }"


        "不要驗證 JSON 結構本身；僅使用其內容作為評分規則。 "
        "5. 透過將 JSON 中每個規則的每個單獨得分點相加來計算 total_score "
        "6. 呼叫 set_score 工具並傳遞 total_score。 "

       
        "輸出 JSON 格式規格：\n"
        "JSON 物件必須正好有兩個頂層鍵："
        "  - 'total_score'：迭代 json 中的每個單獨的得分元素並將它們相加以得出 total_score。 "
        "  - 'scores'：現有的規則 json，每個規則都分配了一個 score 屬性和一個 reason 屬性"
  
"""
