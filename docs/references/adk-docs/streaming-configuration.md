# 設定串流行為

您可以為即時（串流）代理程式設定一些組態。

這是由 [RunConfig](https://github.com/google/adk-python/blob/main/src/google/adk/agents/run_config.py) 設定的。您應該將 RunConfig 與您的 [Runner.run_live(...)](https://github.com/google/adk-python/blob/main/src/google/adk/runners.py) 一起使用。

例如，如果您想設定語音組態，您可以利用 speech_config。

```python
voice_config = genai_types.VoiceConfig(
    prebuilt_voice_config=genai_types.PrebuiltVoiceConfigDict(
        voice_name='Aoede'
    )
)
speech_config = genai_types.SpeechConfig(voice_config=voice_config)
run_config = RunConfig(speech_config=speech_config)

runner.run_live(
    ...,
    run_config=run_config,
)
```
