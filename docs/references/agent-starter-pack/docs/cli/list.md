# list

列出可用的代理和模板。

## 使用方式

```bash
uvx agent-starter-pack list [OPTIONS]
```

## 選項

- `--source URL` - 從特定的儲存庫列出模板
- `--adk` - 列出官方的 ADK 範例

## 範例

```bash
# 列出內建代理
uvx agent-starter-pack list

# 列出 ADK 範例
uvx agent-starter-pack list --adk

# 從儲存庫列出模板
uvx agent-starter-pack list --source https://github.com/user/templates
```

## 注意事項

只有在 `pyproject.toml` 中具有 `[tool.agent-starter-pack]` 設定的模板才會出現在清單中。沒有此設定的模板仍然可以與 `create` 一起使用，但無法被發現。

## 相關指令

- [`create`](./create.md) - 從模板建立代理
- [遠端模板](../remote-templates/) - 模板文件