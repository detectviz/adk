# 快速入門 (串流 / Java) {#adk-streaming-quickstart-java}

本快速入門指南將引導您完成建立基本代理的過程，並利用 Java 的 ADK 串流功能來促進低延遲的雙向語音互動。

您將從設定 Java 和 Maven 環境、建構專案並定義必要的相依性開始。接著，您將建立一個簡單的 `ScienceTeacherAgent`，使用開發者介面測試其基於文字的串流功能，然後進一步啟用即時音訊通訊，將您的代理轉變為互動式語音驅動的應用程式。

## **建立您的第一個代理** {#create-your-first-agent}

### **先決條件**

* 在本入門指南中，您將使用 Java 進行程式設計。請檢查您的機器上是否已安裝 **Java**。理想情況下，您應該使用 Java 17 或更高版本 (您可以透過輸入 **java \-version** 來檢查)

* 您還將使用 Java 的 **Maven** 建置工具。因此，在繼續之前，請確保您的機器上已[安裝 Maven](https://maven.apache.org/install.html) (對於 Cloud Top 或 Cloud Shell 來說是這種情況，但對於您的筆記型電腦則不一定)。

### **準備專案結構**

要開始使用 ADK Java，讓我們建立一個具有以下目錄結構的 Maven 專案：

```
adk-agents/
├── pom.xml
└── src/
    └── main/
        └── java/
            └── agents/
                └── ScienceTeacherAgent.java
```

請依照[安裝](get-started-installation.md)頁面中的說明新增 `pom.xml` 以使用 ADK 套件。

!!! Note
    您可以隨意為專案的根目錄使用任何您喜歡的名稱 (而不是 adk-agents)

### **執行編譯**

讓我們透過執行編譯 (**mvn compile** 指令) 來看看 Maven 是否對此建置感到滿意：

```shell
$ mvn compile
[INFO] Scanning for projects...
[INFO] 
[INFO] --------------------< adk-agents:adk-agents >--------------------
[INFO] Building adk-agents 1.0-SNAPSHOT
[INFO]   from pom.xml
[INFO] --------------------------------[ jar ]---------------------------------
[INFO] 
[INFO] --- resources:3.3.1:resources (default-resources) @ adk-demo ---
[INFO] skip non existing resourceDirectory /home/user/adk-demo/src/main/resources
[INFO] 
[INFO] --- compiler:3.13.0:compile (default-compile) @ adk-demo ---
[INFO] Nothing to compile - all classes are up to date.
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  1.347 s
[INFO] Finished at: 2025-05-06T15:38:08Z
[INFO] ------------------------------------------------------------------------
```

看來專案已正確設定好可以編譯了！

### **建立代理**

在 `src/main/java/agents/` 目錄下建立 **ScienceTeacherAgent.java** 檔案，內容如下：

```java
package samples.liveaudio;

import com.google.adk.agents.BaseAgent;
import com.google.adk.agents.LlmAgent;

/** Science teacher agent. */
public class ScienceTeacherAgent {

  // Field expected by the Dev UI to load the agent dynamically
  // (the agent must be initialized at declaration time)
  public static BaseAgent ROOT_AGENT = initAgent();

  public static BaseAgent initAgent() {
    return LlmAgent.builder()
        .name("science-app")
        .description("Science teacher agent")
        .model("gemini-2.0-flash-exp")
        .instruction("""
            You are a helpful science teacher that explains
            science concepts to kids and teenagers.
            """)
        .build();
  }
}
```

!!!note "疑難排解"

    模型 `gemini-2.0-flash-exp` 未來將被棄用。如果您在使用時遇到任何問題，請嘗試改用 `gemini-2.0-flash-live-001`

我們稍後將使用`開發者介面`來執行此代理。為了讓工具自動辨識代理，其 Java 類別必須遵守以下兩個規則：

* 代理應儲存在一個名為 **ROOT\_AGENT** 的全域 **public static** 變數中，類型為 **BaseAgent**，並在宣告時進行初始化。
* 代理定義必須是一個 **static** 方法，以便動態編譯類別載入器可以在類別初始化期間載入它。

## **使用開發者介面執行代理** {#run-agent-with-adk-web-server}

`開發者介面`是一個 Web 伺服器，您可以在其中快速執行和測試您的代理以進行開發，而無需為代理建立自己的 UI 應用程式。

### **定義環境變數**

要執行伺服器，您需要匯出兩個環境變數：

* 一個您可以[從 AI Studio 取得](https://ai.google.dev/gemini-api/docs/api-key)的 Gemini 金鑰，
* 一個指定我們這次不使用 Vertex AI 的變數。

```shell
export GOOGLE_GENAI_USE_VERTEXAI=FALSE
export GOOGLE_API_KEY=YOUR_API_KEY
```

### **執行開發者介面**

從終端機執行以下指令以啟動開發者介面。

```console title="terminal"
mvn exec:java \
    -Dexec.mainClass="com.google.adk.web.AdkWebServer" \
    -Dexec.args="--adk.agents.source-dir=src/main/java" \
    -Dexec.classpathScope="compile"
```

**步驟 1：** 在瀏覽器中直接開啟提供的 URL (通常是 `http://localhost:8080` 或 `http://127.0.0.1:8080`)。

**步驟 2.** 在 UI 的左上角，您可以在下拉式選單中選擇您的代理。選擇 "science-app"。

!!!note "疑難排解"

    如果您在下拉式選單中沒有看到 "science-app"，請確保您在 Java 原始碼所在的位置 (通常是 `src/main/java`) 執行 `mvn` 指令。

## 使用文字嘗試開發者介面

使用您喜歡的瀏覽器，導覽至：[http://127.0.0.1:8080/](http://127.0.0.1:8080/)

您應該會看到以下介面：

![Dev UI](../../assets/quickstart-streaming-devui.png)

點擊右上角的 `權杖串流` 開關，並向科學老師提出任何問題，例如 `什麼是電子？`。然後您應該會在 UI 上看到串流輸出的文字。

正如我們所見，您不必在代理本身中為文字串流功能編寫任何特定程式碼。它預設作為 ADK 代理功能提供。

### 嘗試使用語音和視訊

要嘗試語音，請重新載入網頁瀏覽器，點擊麥克風按鈕以啟用語音輸入，並用語音提出相同的問題。您將即時聽到語音回答。

要嘗試視訊，請重新載入網頁瀏覽器，點擊攝影機按鈕以啟用視訊輸入，並提出諸如「你看到了什麼？」之類的問題。代理將回答他們在視訊輸入中看到的內容。

### 停止工具

在主控台上按 `Ctrl-C` 停止工具。

## **使用自訂即時音訊應用程式執行代理** {#run-agent-with-live-audio}

現在，讓我們嘗試使用代理和自訂的即時音訊應用程式進行音訊串流。

### **用於即時音訊的 Maven pom.xml 建置檔案**

將您現有的 pom.xml 替換為以下內容。

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project xmlns="http://maven.apache.org/POM/4.0.0"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>

  <groupId>com.google.adk.samples</groupId>
  <artifactId>google-adk-sample-live-audio</artifactId>
  <version>0.1.0</version>
  <name>Google ADK - Sample - Live Audio</name>
  <description>
    A sample application demonstrating a live audio conversation using ADK,
    runnable via samples.liveaudio.LiveAudioRun.
  </description>
  <packaging>jar</packaging>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <java.version>17</java.version>
    <auto-value.version>1.11.0</auto-value.version>
    <!-- Main class for exec-maven-plugin -->
    <exec.mainClass>samples.liveaudio.LiveAudioRun</exec.mainClass>
    <google-adk.version>0.1.0</google-adk.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>com.google.cloud</groupId>
        <artifactId>libraries-bom</artifactId>
        <version>26.53.0</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>com.google.adk</groupId>
      <artifactId>google-adk</artifactId>
      <version>${google-adk.version}</version>
    </dependency>
    <dependency>
      <groupId>commons-logging</groupId>
      <artifactId>commons-logging</artifactId>
      <version>1.2</version> <!-- Or use a property if defined in a parent POM -->
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
        <configuration>
          <source>${java.version}</source>
          <target>${java.version}</target>
          <parameters>true</parameters>
          <annotationProcessorPaths>
            <path>
              <groupId>com.google.auto.value</groupId>
              <artifactId>auto-value</artifactId>
              <version>${auto-value.version}</version>
            </path>
          </annotationProcessorPaths>
        </configuration>
      </plugin>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>build-helper-maven-plugin</artifactId>
        <version>3.6.0</version>
        <executions>
          <execution>
            <id>add-source</id>
            <phase>generate-sources</phase>
            <goals>
              <goal>add-source</goal>
            </goals>
            <configuration>
              <sources>
                <source>.</source>
              </sources>
            </configuration>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <groupId>org.codehaus.mojo</groupId>
        <artifactId>exec-maven-plugin</artifactId>
        <version>3.2.0</version>
        <configuration>
          <mainClass>${exec.mainClass}</mainClass>
          <classpathScope>runtime</classpathScope>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
```

### **建立即時音訊執行工具**

在 `src/main/java/` 目錄下建立 **LiveAudioRun.java** 檔案，內容如下。此工具在其上執行代理，並具有即時音訊輸入和輸出。

```java

package samples.liveaudio;

import com.google.adk.agents.LiveRequestQueue;
import com.google.adk.agents.RunConfig;
import com.google.adk.events.Event;
import com.google.adk.runner.Runner;
import com.google.adk.sessions.InMemorySessionService;
import com.google.common.collect.ImmutableList;
import com.google.genai.types.Blob;
import com.google.genai.types.Modality;
import com.google.genai.types.PrebuiltVoiceConfig;
import com.google.genai.types.Content;
import com.google.genai.types.Part;
import com.google.genai.types.SpeechConfig;
import com.google.genai.types.VoiceConfig;
import io.reactivex.rxjava3.core.Flowable;
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.URL;
import javax.sound.sampled.AudioFormat;
import javax.sound.sampled.AudioInputStream;
import javax.sound.sampled.AudioSystem;
import javax.sound.sampled.DataLine;
import javax.sound.sampled.LineUnavailableException;
import javax.sound.sampled.Mixer;
import javax.sound.sampled.SourceDataLine;
import javax.sound.sampled.TargetDataLine;
import java.util.UUID;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicBoolean;
import agents.ScienceTeacherAgent;

/** Main class to demonstrate running the {@link LiveAudioAgent} for a voice conversation. */
public final class LiveAudioRun {
  private final String userId;
  private final String sessionId;
  private final Runner runner;

  private static final javax.sound.sampled.AudioFormat MIC_AUDIO_FORMAT =
      new javax.sound.sampled.AudioFormat(16000.0f, 16, 1, true, false);

  private static final javax.sound.sampled.AudioFormat SPEAKER_AUDIO_FORMAT =
      new javax.sound.sampled.AudioFormat(24000.0f, 16, 1, true, false);

  private static final int BUFFER_SIZE = 4096;

  public LiveAudioRun() {
    this.userId = "test_user";
    String appName = "LiveAudioApp";
    this.sessionId = UUID.randomUUID().toString();

    InMemorySessionService sessionService = new InMemorySessionService();
    this.runner = new Runner(ScienceTeacherAgent.ROOT_AGENT, appName, null, sessionService);

    ConcurrentMap<String, Object> initialState = new ConcurrentHashMap<>();
    var unused =
        sessionService.createSession(appName, userId, initialState, sessionId).blockingGet();
  }

  private void runConversation() throws Exception {
    System.out.println("Initializing microphone input and speaker output...");

    RunConfig runConfig =
        RunConfig.builder()
            .setStreamingMode(RunConfig.StreamingMode.BIDI)
            .setResponseModalities(ImmutableList.of(new Modality("AUDIO")))
            .setSpeechConfig(
                SpeechConfig.builder()
                    .voiceConfig(
                        VoiceConfig.builder()
                            .prebuiltVoiceConfig(
                                PrebuiltVoiceConfig.builder().voiceName("Aoede").build())
                            .build())
                    .languageCode("en-US")
                    .build())
            .build();

    LiveRequestQueue liveRequestQueue = new LiveRequestQueue();

    Flowable<Event> eventStream =
        this.runner.runLive(
            runner.sessionService().createSession(userId, sessionId).blockingGet(),
            liveRequestQueue,
            runConfig);

    AtomicBoolean isRunning = new AtomicBoolean(true);
    AtomicBoolean conversationEnded = new AtomicBoolean(false);
    ExecutorService executorService = Executors.newFixedThreadPool(2);

    // Task for capturing microphone input
    Future<?> microphoneTask =
        executorService.submit(() -> captureAndSendMicrophoneAudio(liveRequestQueue, isRunning));

    // Task for processing agent responses and playing audio
    Future<?> outputTask =
        executorService.submit(
            () -> {
              try {
                processAudioOutput(eventStream, isRunning, conversationEnded);
              } catch (Exception e) {
                System.err.println("Error processing audio output: " + e.getMessage());
                e.printStackTrace();
                isRunning.set(false);
              }
            });

    // Wait for user to press Enter to stop the conversation
    System.out.println("Conversation started. Press Enter to stop...");
    System.in.read();

    System.out.println("Ending conversation...");
    isRunning.set(false);

    try {
      // Give some time for ongoing processing to complete
      microphoneTask.get(2, TimeUnit.SECONDS);
      outputTask.get(2, TimeUnit.SECONDS);
    } catch (Exception e) {
      System.out.println("Stopping tasks...");
    }

    liveRequestQueue.close();
    executorService.shutdownNow();
    System.out.println("Conversation ended.");
  }

  private void captureAndSendMicrophoneAudio(
      LiveRequestQueue liveRequestQueue, AtomicBoolean isRunning) {
    TargetDataLine micLine = null;
    try {
      DataLine.Info info = new DataLine.Info(TargetDataLine.class, MIC_AUDIO_FORMAT);
      if (!AudioSystem.isLineSupported(info)) {
        System.err.println("Microphone line not supported!");
        return;
      }

      micLine = (TargetDataLine) AudioSystem.getLine(info);
      micLine.open(MIC_AUDIO_FORMAT);
      micLine.start();

      System.out.println("Microphone initialized. Start speaking...");

      byte[] buffer = new byte[BUFFER_SIZE];
      int bytesRead;

      while (isRunning.get()) {
        bytesRead = micLine.read(buffer, 0, buffer.length);

        if (bytesRead > 0) {
          byte[] audioChunk = new byte[bytesRead];
          System.arraycopy(buffer, 0, audioChunk, 0, bytesRead);

          Blob audioBlob = Blob.builder().data(audioChunk).mimeType("audio/pcm").build();

          liveRequestQueue.realtime(audioBlob);
        }
      }
    } catch (LineUnavailableException e) {
      System.err.println("Error accessing microphone: " + e.getMessage());
      e.printStackTrace();
    } finally {
      if (micLine != null) {
        micLine.stop();
        micLine.close();
      }
    }
  }

  private void processAudioOutput(
      Flowable<Event> eventStream, AtomicBoolean isRunning, AtomicBoolean conversationEnded) {
    SourceDataLine speakerLine = null;
    try {
      DataLine.Info info = new DataLine.Info(SourceDataLine.class, SPEAKER_AUDIO_FORMAT);
      if (!AudioSystem.isLineSupported(info)) {
        System.err.println("Speaker line not supported!");
        return;
      }

      final SourceDataLine finalSpeakerLine = (SourceDataLine) AudioSystem.getLine(info);
      finalSpeakerLine.open(SPEAKER_AUDIO_FORMAT);
      finalSpeakerLine.start();

      System.out.println("Speaker initialized.");

      for (Event event : eventStream.blockingIterable()) {
        if (!isRunning.get()) {
          break;
        }

        AtomicBoolean audioReceived = new AtomicBoolean(false);
        processEvent(event, audioReceived);
        
        event.content().ifPresent(content -> content.parts().ifPresent(parts -> parts.forEach(part -> playAudioData(part, finalSpeakerLine))));
      }

      speakerLine = finalSpeakerLine; // Assign to outer variable for cleanup in finally block
    } catch (LineUnavailableException e) {
      System.err.println("Error accessing speaker: " + e.getMessage());
      e.printStackTrace();
    } finally {
      if (speakerLine != null) {
        speakerLine.drain();
        speakerLine.stop();
        speakerLine.close();
      }
      conversationEnded.set(true);
    }
  }

  private void playAudioData(Part part, SourceDataLine speakerLine) {
    part.inlineData()
        .ifPresent(
            inlineBlob ->
                inlineBlob
                    .data()
                    .ifPresent(
                        audioBytes -> {
                          if (audioBytes.length > 0) {
                            System.out.printf(
                                "Playing audio (%s): %d bytes%n",
                                inlineBlob.mimeType(),
                                audioBytes.length);
                            speakerLine.write(audioBytes, 0, audioBytes.length);
                          }
                        }));
  }

  private void processEvent(Event event, java.util.concurrent.atomic.AtomicBoolean audioReceived) {
    event
        .content()
        .ifPresent(
            content ->
                content
                    .parts()
                    .ifPresent(parts -> parts.forEach(part -> logReceivedAudioData(part, audioReceived))));
  }

  private void logReceivedAudioData(Part part, AtomicBoolean audioReceived) {
    part.inlineData()
        .ifPresent(
            inlineBlob ->
                inlineBlob
                    .data()
                    .ifPresent(
                        audioBytes -> {
                          if (audioBytes.length > 0) {
                            System.out.printf(
                                "    Audio (%s): received %d bytes.%n",
                                inlineBlob.mimeType(),
                                audioBytes.length);
                            audioReceived.set(true);
                          } else {
                            System.out.printf(
                                "    Audio (%s): received empty audio data.%n",
                                inlineBlob.mimeType());
                          }
                        }));
  }

  public static void main(String[] args) throws Exception {
    LiveAudioRun liveAudioRun = new LiveAudioRun();
    liveAudioRun.runConversation();
    System.out.println("Exiting Live Audio Run.");
  }
}
```

### **執行即時音訊執行工具**

要執行即時音訊執行工具，請在 `adk-agents` 目錄上使用以下指令：

```
mvn compile exec:java
```

然後您應該會看到：

```
$ mvn compile exec:java
...
Initializing microphone input and speaker output...
Conversation started. Press Enter to stop...
Speaker initialized.
Microphone initialized. Start speaking...
```

看到此訊息後，表示工具已準備好接收語音輸入。請向代理提出問題，例如 `什麼是電子？`。

!!! Caution
    當您發現代理不斷自行說話且無法停止時，請嘗試使用耳機來抑制回音。

## **摘要** {#summary}

ADK 的串流功能使開發人員能夠建立具有低延遲、雙向語音和視訊通訊能力的代理，從而增強互動體驗。本文展示了文字串流是 ADK 代理的內建功能，無需額外的特定程式碼，同時也展示了如何實現即時音訊對話，以便與代理進行即時語音互動。這使得溝通更加自然和動態，因為使用者可以無縫地與代理交談和聆聽。
