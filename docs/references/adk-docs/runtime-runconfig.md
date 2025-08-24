# 執行階段設定 (Runtime Configuration)

`RunConfig` 定義了 ADK 中代理程式的執行階段行為和選項。它控制語音和串流設定、函式呼叫、產物儲存以及對大型語言模型 (LLM) 呼叫的限制。

在建構代理程式執行時，您可以傳遞一個 `RunConfig` 來自訂代理程式如何與模型互動、處理音訊和串流回應。預設情況下，不會啟用任何串流，且輸入不會保留為產物。請使用 `RunConfig` 來覆寫這些預設值。

## 類別定義

`RunConfig` 類別持有代理程式執行階段行為的設定參數。

- Python ADK 使用 Pydantic 進行此驗證。

- Java ADK 通常使用不可變的資料類別。

=== "Python"

    ```python
    class RunConfig(BaseModel):
        """代理程式執行階段行為的設定。"""
    
        model_config = ConfigDict(
            extra='forbid',
        )
    
        speech_config: Optional[types.SpeechConfig] = None
        response_modalities: Optional[list[str]] = None
        save_input_blobs_as_artifacts: bool = False
        support_cfc: bool = False
        streaming_mode: StreamingMode = StreamingMode.NONE
        output_audio_transcription: Optional[types.AudioTranscriptionConfig] = None
        max_llm_calls: int = 500
    ```

=== "Java"

    ```java
    public abstract class RunConfig {
      
      public enum StreamingMode {
        NONE,
        SSE,
        BIDI
      }
      
      public abstract @Nullable SpeechConfig speechConfig();
    
      public abstract ImmutableList<Modality> responseModalities();
    
      public abstract boolean saveInputBlobsAsArtifacts();
      
      public abstract @Nullable AudioTranscriptionConfig outputAudioTranscription();
    
      public abstract int maxLlmCalls();
      
      // ...
    }
    ```

## 執行階段參數

| 參數                       | Python 類型                                  | Java 類型                                             | 預設 (Py / Java)               | 說明                                                                                                                  |
| :------------------------------ | :------------------------------------------- |:------------------------------------------------------|:----------------------------------|:-----------------------------------------------------------------------------------------------------------------------------|
| `speech_config`                 | `Optional[types.SpeechConfig]`               | `SpeechConfig` (可為 null，透過 `@Nullable`)             | `None` / `null`                   | 使用 `SpeechConfig` 類型設定語音合成（語音、語言）。                                                 |
| `response_modalities`           | `Optional[list[str]]`                        | `ImmutableList<Modality>`                             | `None` / 空的 `ImmutableList`    | 所需的輸出模態列表（例如，Python：`["TEXT", "AUDIO"]`；Java：使用結構化的 `Modality` 物件）。             |
| `save_input_blobs_as_artifacts` | `bool`                                       | `boolean`                                             | `False` / `false`                 | 如果為 `true`，則將輸入的 blob（例如，上傳的檔案）儲存為執行產物，以供偵錯/稽核。                                 |
| `streaming_mode`                | `StreamingMode`                              | *目前不支援*                             | `StreamingMode.NONE` / N/A        | 設定串流行為：`NONE`（預設）、`SSE`（伺服器發送事件）或 `BIDI`（雙向）。                        |
| `output_audio_transcription`    | `Optional[types.AudioTranscriptionConfig]`   | `AudioTranscriptionConfig` (可為 null，透過 `@Nullable`) | `None` / `null`                   | 使用 `AudioTranscriptionConfig` 類型設定產生的音訊輸出的轉錄。                                |
| `max_llm_calls`                 | `int`                                        | `int`                                                 | `500` / `500`                     | 限制每次執行的 LLM 呼叫總數。`0` 或負數表示無限制（會發出警告）；`sys.maxsize` 會引發 `ValueError`。                 |
| `support_cfc`                   | `bool`                                       | *目前不支援*                             | `False` / N/A                     | **Python：** 啟用組合式函式呼叫 (Compositional Function Calling)。需要 `streaming_mode=SSE` 並使用 LIVE API。**實驗性功能。**   |

### `speech_config`

!!! Note
    無論語言為何，`SpeechConfig` 的介面或定義都是相同的。

具有音訊功能的即時代理程式的語音設定。`SpeechConfig` 類別具有以下結構：

```python
class SpeechConfig(_common.BaseModel):
    """語音產生設定。"""

    voice_config: Optional[VoiceConfig] = Field(
        default=None,
        description="""要使用的喇叭設定。""",
    )
    language_code: Optional[str] = Field(
        default=None,
        description="""語音合成的語言代碼 (ISO 639，例如 en-US)。
        僅適用於 Live API。""",
    )
```

`voice_config` 參數使用 `VoiceConfig` 類別：

```python
class VoiceConfig(_common.BaseModel):
    """要使用的語音設定。"""

    prebuilt_voice_config: Optional[PrebuiltVoiceConfig] = Field(
        default=None,
        description="""要使用的喇叭設定。""",
    )
```

而 `PrebuiltVoiceConfig` 具有以下結構：

```python
class PrebuiltVoiceConfig(_common.BaseModel):
    """要使用的預建喇叭設定。"""

    voice_name: Optional[str] = Field(
        default=None,
        description="""要使用的預建語音名稱。""",
    )
```

這些巢狀設定類別可讓您指定：

* `voice_config`：要使用的預建語音名稱（在 `PrebuiltVoiceConfig` 中）
* `language_code`：用於語音合成的 ISO 639 語言代碼（例如 "en-US"）

在實作具備語音功能的代理程式時，請設定這些參數以控制代理程式說話時的聲音。

### `response_modalities`

定義代理程式的輸出模態。如果未設定，預設為 AUDIO。回應模態決定了代理程式如何透過各種管道（例如，文字、音訊）與使用者通訊。

### `save_input_blobs_as_artifacts`

啟用後，輸入的 blob 將在代理程式執行期間儲存為產物。這對於偵錯和稽核目的很有用，可讓開發人員檢視代理程式收到的確切資料。

### `support_cfc`

啟用組合式函式呼叫 (Compositional Function Calling, CFC) 支援。僅在使用 StreamingMode.SSE 時適用。啟用後，將調用 LIVE API，因為只有它支援 CFC 功能。

!!! warning

    `support_cfc` 功能是實驗性的，其 API 或行為可能會在未來版本中變更。

### `streaming_mode`

設定代理程式的串流行為。可能的值：

* `StreamingMode.NONE`：無串流；回應以完整單元的形式傳遞
* `StreamingMode.SSE`：伺服器發送事件串流；從伺服器到客戶端的單向串流
* `StreamingMode.BIDI`：雙向串流；雙向同時通訊

串流模式會影響效能和使用者體驗。SSE 串流讓使用者可以在產生部分回應時看到它們，而 BIDI 串流則可實現即時互動體驗。

### `output_audio_transcription`

用於轉錄具有音訊回應功能的即時代理程式的音訊輸出設定。這可以自動轉錄音訊回應，以實現無障礙、記錄保存和多模態應用。

### `max_llm_calls`

設定給定代理程式執行的 LLM 呼叫總數限制。

* 大於 0 且小於 `sys.maxsize` 的值：對 LLM 呼叫強制設定上限
* 小於或等於 0 的值：允許無限制的 LLM 呼叫*（不建議用於生產環境）*

此參數可防止過度的 API 使用和潛在的失控程序。由於 LLM 呼叫通常會產生費用並消耗資源，因此設定適當的限制至關重要。

## 驗證規則

`RunConfig` 類別會驗證其參數以確保代理程式正常運作。雖然 Python ADK 使用 `Pydantic` 進行自動類型驗證，但 Java ADK 依賴其靜態類型，並可能在 RunConfig 的建構中包含明確的檢查。
特別是對於 `max_llm_calls` 參數：

1. 極大的值（如 Python 中的 `sys.maxsize` 或 Java 中的 `Integer.MAX_VALUE`）通常不被允許，以防止問題。

2. 零或更小的值通常會觸發關於無限制 LLM 互動的警告。

## 範例

### 基本執行階段設定

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.NONE,
        max_llm_calls=100
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
            .setStreamingMode(StreamingMode.NONE)
            .setMaxLlmCalls(100)
            .build();
    ```

此設定建立了一個非串流代理程式，LLM 呼叫限制為 100 次，適用於偏好完整回應的簡單任務導向代理程式。

### 啟用串流

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    
    config = RunConfig(
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=200
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    
    RunConfig config = RunConfig.builder()
        .setStreamingMode(StreamingMode.SSE)
        .setMaxLlmCalls(200)
        .build();
    ```

使用 SSE 串流可讓使用者在產生回應時看到它們，為聊天機器人和助理提供更具回應性的感覺。

### 啟用語音支援

=== "Python"

    ```python
    from google.genai.adk import RunConfig, StreamingMode
    from google.genai import types
    
    config = RunConfig(
        speech_config=types.SpeechConfig(
            language_code="en-US",
            voice_config=types.VoiceConfig(
                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                    voice_name="Kore"
                )
            ),
        ),
        response_modalities=["AUDIO", "TEXT"],
        save_input_blobs_as_artifacts=True,
        support_cfc=True,
        streaming_mode=StreamingMode.SSE,
        max_llm_calls=1000,
    )
    ```

=== "Java"

    ```java
    import com.google.adk.agents.RunConfig;
    import com.google.adk.agents.RunConfig.StreamingMode;
    import com.google.common.collect.ImmutableList;
    import com.google.genai.types.Content;
    import com.google.genai.types.Modality;
    import com.google.genai.types.Part;
    import com.google.genai.types.PrebuiltVoiceConfig;
    import com.google.genai.types.SpeechConfig;
    import com.google.genai.types.VoiceConfig;
    
    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(StreamingMode.SSE)
            .setMaxLlmCalls(1000)
            .setSaveInputBlobsAsArtifacts(true)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO"), new Modality("TEXT")))
            .setSpeechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Kore").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();
    ```

這個全面的範例設定了一個具有以下功能的代理程式：

* 使用 "Kore" 語音（美式英語）的語音功能
* 音訊和文字兩種輸出模態
* 為輸入 blob 儲存產物（對偵錯很有用）
* 啟用實驗性 CFC 支援 **(僅限 Python)**
* 用於回應式互動的 SSE 串流
* 1000 次 LLM 呼叫的限制

### 啟用實驗性 CFC 支援

![python_only](https://img.shields.io/badge/Currently_supported_in-Python-blue){ title="此功能目前適用於 Python。Java 支援正在計劃/即將推出。"}

```python
from google.genai.adk import RunConfig, StreamingMode

config = RunConfig(
    streaming_mode=StreamingMode.SSE,
    support_cfc=True,
    max_llm_calls=150
)
```

啟用組合式函式呼叫可建立一個能根據模型輸出動態執行函式的代理程式，這對於需要複雜工作流程的應用程式非常強大。
