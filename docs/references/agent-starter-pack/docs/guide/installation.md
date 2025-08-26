# 安裝

有多種方法可以安裝 Agent Starter Pack。請選擇最適合您工作流程的方法。

**想要零設定嗎？** 👉 [在 Firebase Studio 中試用](https://studio.firebase.google.com/new?template=https%3A%2F%2Fgithub.com%2FGoogleCloudPlatform%2Fagent-starter-pack%2Ftree%2Fmain%2Fsrc%2Fresources%2Fidx) 或在 [Cloud Shell](https://shell.cloud.google.com/cloudshell/editor?cloudshell_git_repo=https%3A%2F%2Fgithub.com%2Feliasecchig%2Fasp-open-in-cloud-shell&cloudshell_print=open-in-cs) 中試用

## 使用 `uvx` 快速建立專案

如果您已安裝 [uv](https://astral.sh/uv)，您可以在沒有永久安裝的情況下建立專案：
```bash
uvx agent-starter-pack create my-awesome-agent
```

## 虛擬環境安裝

安裝到一個隔離的 Python 環境中。

```bash
# 建立並啟用 venv
python -m venv .venv && source .venv/bin/activate # 對於 Windows Git Bash，使用 source .venv/Scripts/activate

# 使用 pip 或 uv 安裝
pip install agent-starter-pack
```

## 永久性 CLI 安裝

全域安裝 `agent-starter-pack` 指令。

### 使用 `pipx` (隔離的全域工具)
```bash
# 安裝 pipx (如果需要)
python3 -m pip install --user pipx && python3 -m pipx ensurepath

# 安裝 Agent Starter Pack
pipx install agent-starter-pack
```

### 使用 `uv tool install` (快速、隔離的全域工具)
需要 `uv` (請參閱 `uvx` 部分的安裝說明)。
```bash
uv tool install agent-starter-pack
```

## 建立專案 (在永久性/Venv 安裝後)

如果您是透過 `pipx`、`uv tool install` 或在虛擬環境中安裝的：
```bash
agent-starter-pack create my-awesome-agent
```

## 管理安裝

### 升級
*   **`uvx`:** 不需要 (總是使用最新版本)。
*   **`pipx`:** `pipx upgrade agent-starter-pack`
*   **`uv tool`:** `uv tool install agent-starter-pack` (此指令會升級)
*   **`pip`/`uv pip` (在 .venv 中):** `(uv) pip install --upgrade agent-starter-pack`

### 解除安裝
*   **`uvx`:** 不適用。
*   **`pipx`:** `pipx uninstall agent-starter-pack`
*   **`uv tool`:** `uv tool uninstall agent-starter-pack`
*   **`pip`/`uv pip` (在 .venv 中):** `(uv) pip uninstall agent-starter-pack`

## 常見安裝問題疑難排解

### 安裝後找不到指令

如果您在安裝後遇到「找不到指令」的錯誤：

1.  **檢查您的 PATH**：確保 Python 指令碼目錄在您的 PATH 中：
    ```bash
    echo $PATH
    ```
2.  **驗證安裝位置**：檢查套件的安裝位置：
    ```bash
    pip show agent-starter-pack
    ```
3.  **手動新增路徑**：如果需要，將指令碼目錄新增到您的 PATH：
    ```bash
    export PATH="$HOME/.local/bin:$PATH"
    # 對於使用者安裝
    ```
    將此行新增到您的 `~/.bashrc` 或 `~/.zshrc` 以永久生效。

### 安裝過程中的權限錯誤

如果您遇到權限錯誤：

1.  **使用使用者安裝模式**：
    ```bash
    pip install --user agent-starter-pack
    ```
2.  **檢查目錄權限**：
    ```bash
    ls -la ~/.local/bin
    ```
3.  **如果需要，修正權限**：
    ```bash
    chmod +x ~/.local/bin/agent-starter-pack
    ```

### Python 版本相容性問題

如果您遇到 Python 版本錯誤：

1.  **檢查您的 Python 版本**：
    ```bash
    python --version
    ```
2.  **如果需要，安裝相容的 Python 版本** (需要 3.10 或更新版本)。
3.  **使用正確的 Python 版本建立虛擬環境**：
    ```bash
    python3.10 -m venv .venv
    source .venv/bin/activate
    ```

### 套件依賴衝突

如果您遇到依賴衝突：

1.  **使用乾淨的虛擬環境**：
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    pip install agent-starter-pack
    ```
2.  **更新 pip 和 setuptools**：
    ```bash
    pip install --upgrade pip setuptools
    ```
3.  **使用詳細輸出進行安裝以識別衝突**：
    ```bash
    pip install -v agent-starter-pack
    ```

### 安裝驗證

要驗證您的安裝是否正常運作：

1.  **檢查已安裝的版本**：
    ```bash
    agent-starter-pack --version
    ```
2.  **執行說明指令**：
    ```bash
    agent-starter-pack --help
    ```

如果您仍然遇到問題，請[提交一個 issue](https://github.com/GoogleCloudPlatform/agent-starter-pack/issues)，並提供有關您的環境和您遇到的具體錯誤訊息的詳細資訊。
