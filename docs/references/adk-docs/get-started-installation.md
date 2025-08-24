# 安裝 ADK

=== "Python"

    ## 建立並啟用虛擬環境
    
    我們建議使用 [venv](https://docs.python.org/3/library/venv.html) 建立一個虛擬 Python 環境：
    
    ```shell
    python -m venv .venv
    ```
    
    現在，您可以使用適合您作業系統和環境的指令來啟用虛擬環境：
    
    ```
    # Mac / Linux
    source .venv/bin/activate
    
    # Windows CMD:
    .venv\Scripts\activate.bat
    
    # Windows PowerShell:
    .venv\Scripts\Activate.ps1
    ```

    ### 安裝 ADK
    
    ```bash
    pip install google-adk
    ```
    
    (可選) 驗證您的安裝：
    
    ```bash
    pip show google-adk
    ```

=== "Java"

    您可以使用 maven 或 gradle 來新增 `google-adk` 和 `google-adk-dev` 套件。

    `google-adk` 是核心的 Java ADK 函式庫。Java ADK 還附帶一個可插拔的範例 SpringBoot 伺服器，可以無縫地執行您的代理。這個可選的套件是 `google-adk-dev` 的一部分。
    
    如果您使用 maven，請將以下內容新增到您的 `pom.xml` 中：

    ```xml title="pom.xml"
    <dependencies>
      <!-- ADK 核心相依性 -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk</artifactId>
        <version>0.2.0</version>
      </dependency>
      
      <!-- 用於除錯代理的 ADK 開發網頁介面 (可選) -->
      <dependency>
        <groupId>com.google.adk</groupId>
        <artifactId>google-adk-dev</artifactId>
        <version>0.2.0</version>
      </dependency>
    </dependencies>
    ```

    這是一個完整的 [pom.xml](https://github.com/google/adk-docs/tree/main/examples/java/cloud-run/pom.xml) 檔案以供參考。

    如果您使用 gradle，請將相依性新增到您的 build.gradle 中：

    ```title="build.gradle"
    dependencies {
        implementation 'com.google.adk:google-adk:0.2.0'
        implementation 'com.google.adk:google-adk-dev:0.2.0'
    }
    ```


## 後續步驟

* 嘗試使用 [**快速入門**](get-started-quickstart.md) 建立您的第一個代理
