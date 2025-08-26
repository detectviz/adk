# 如何貢獻

我們很樂意接受您對此範例的補丁和貢獻。您只需遵循一些小小的指導方針。

## 貢獻者授權協議

對本專案的貢獻必須附有貢獻者授權協議 (Contributor License Agreement)。您（或您的雇主）保留您貢獻的版權；這僅僅是授權我們使用和重新分發您的貢獻作為專案的一部分。請前往 [Google Developers CLA](https://cla.developers.google.com/) 查看您已存檔的協議或簽署新協議。

您通常只需要提交一次 CLA，所以如果您已經提交過（即使是為不同的專案），您可能不需要再做一次。

## 程式碼審查

所有提交，包括專案成員的提交，都需要審查。我們使用 GitHub 的拉取請求 (pull requests) 來達成此目的。有關使用拉取請求的更多資訊，請參閱 [GitHub 說明](https://help.github.com/articles/about-pull-requests/)。

## 社群準則

本專案遵循 [Google 的開源社群準則](https://opensource.google/conduct/)。

## 貢獻者指南

如果您是開源貢獻的新手，可以在此貢獻者指南中找到有用的資訊。

您可以按照以下步驟進行貢獻：

1.  **Fork 官方儲存庫。** 這將在您自己的帳戶中建立官方儲存庫的副本。
2.  **同步分支。** 這將確保您的儲存庫副本與官方儲存庫的最新變更保持同步。
3.  **在您 fork 的儲存庫的 feature 分支上工作。** 您將在這裡對程式碼進行變更。
4.  **在您 fork 的儲存庫的 feature 分支上提交您的更新。** 這將把您的變更儲存到您的儲存庫副本中。
5.  **向官方儲存庫的 main 分支提交拉取請求。** 這將請求將您的變更合併到官方儲存庫中。
6.  **解決任何 linting 錯誤。** 這將確保您的變更格式正確。
    *   對於由 [check-spelling](https://github.com/check-spelling/check-spelling) 產生的錯誤，請前往 [Job Summary](https://github.com/GoogleCloudPlatform/generative-ai/actions/workflows/spelling.yaml) 閱讀錯誤。
        *   修正所有發現的拼寫錯誤。
        *   禁止的模式被定義為正規表示式，您可以將它們複製/貼到許多 IDE 中以找到實例。[Visual Studio Code 範例](https://medium.com/@nikhilbaxi3/visual-studio-code-secrets-of-regular-expression-search-71723c2ecbd2)。
        *   將誤報新增至 [`.github/actions/spelling/allow.txt`](.github/actions/spelling/allow.txt)。請務必檢查拼寫是否確實正確！

在過程中，請記住以下額外事項：

-   **閱讀 [Google 的開源社群準則](https://opensource.google/conduct/)。** 貢獻準則將為您提供有關專案以及如何貢獻的更多資訊。
-   **測試您的變更。** 在提交拉取請求之前，請確保您的變更按預期工作。
-   **保持耐心。** 您的拉取請求可能需要一些時間才能被審查和合併。

---

## 對於 Google 員工

如果您是 Google 員工，作為一項要求，請遵循 [Google Cloud Platform Generative AI 儲存庫的貢獻指南](https://github.com/GoogleCloudPlatform/generative-ai/blob/main/CONTRIBUTING.md#for-google-employees) 中概述的流程和要求。

## 程式碼品質檢查

為確保程式碼品質，我們利用自動化檢查。在提交拉取請求之前，請在本地執行以下命令：

```bash
make install
```

這會安裝開發依賴項，包括 linting 工具。

然後，執行以下 Make 命令：

```bash
make lint
```

此命令會執行以下 linter 來檢查程式碼風格、潛在錯誤和類型提示：

-   **codespell**：檢測程式碼和文件中的常見拼寫錯誤。
-   **ruff**：一個快速的 Python linter 和格式化工具，它會檢查錯誤、編碼標準並強制執行風格一致性。
-   **mypy**：執行靜態類型檢查，以在執行前捕捉類型錯誤。

```bash
make test
```

此命令使用 pytest 執行測試套件，涵蓋單元測試和整合測試：

您的拉取請求也將使用 GitHub Actions 自動由這些工具檢查。確保您的程式碼在本地通過這些檢查將有助於加快審查過程。
