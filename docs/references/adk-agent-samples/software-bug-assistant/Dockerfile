# 使用預先安裝 uv 的 Python 映像
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

# 將專案安裝到 /app
WORKDIR /app

# 從快取複製而不是連結，因為它是一個掛載的磁碟區
ENV UV_LINK_MODE=copy
ENV PYTHONUNBUFFERED=1

ADD . /app

# 使用鎖定檔案和設定安裝專案的依賴套件
RUN uv sync --locked --no-install-project --no-dev

# 然後，新增其餘的專案原始碼並安裝它
# 將其與依賴套件分開安裝可以實現最佳的層快取
RUN uv sync --locked --no-dev

# 將可執行檔放在環境路徑的前面
ENV PATH="/app/.venv/bin:$PATH"

# 開放通訊埠
EXPOSE 8080

# 預設執行 adk web，您也可以選擇執行 api_server
ENTRYPOINT ["uv", "run", "adk", "web", "--host", "0.0.0.0", "--port", "8080"]
