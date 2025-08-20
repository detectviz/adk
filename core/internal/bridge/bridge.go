// Package bridge 提供工具橋接能力：將分類好的 Shell 工具以一致介面執行。
// 目錄結構預期：core/tools/{diagnostic,config,remediation}/*.sh
package bridge

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"time"
)

// ToolBridge 封裝工具執行邏輯。
type ToolBridge struct {
	toolsDir string // 工具根目錄（相對或絕對路徑）
}

// ToolResult 標準化工具執行結果。
type ToolResult struct {
	Status     string          `json:"status"`      // ok / warning / error / dry_run
	Message    string          `json:"message"`     // 人類可讀訊息
	Data       json.RawMessage `json:"data"`        // 工具回傳資料（JSON 字串）
	DurationMs int64           `json:"duration_ms"` // 執行耗時（毫秒）
	StartedAt  time.Time       `json:"started_at"`  // 開始時間
	EndedAt    time.Time       `json:"ended_at"`    // 結束時間
}

// NewToolBridge 產生新的橋接器。
func NewToolBridge(toolsDir string) *ToolBridge {
	if toolsDir == "" {
		toolsDir = filepath.Join("core", "tools")
	}
	return &ToolBridge{toolsDir: toolsDir}
}

// scriptPath 根據分類與名稱推導 Shell 腳本路徑。
func (tb *ToolBridge) scriptPath(category, name string) string {
	return filepath.Join(tb.toolsDir, category, fmt.Sprintf("%s.sh", name))
}

// Execute 執行指定工具。
// args 將直接傳入目標腳本；請確保安全來源。
func (tb *ToolBridge) Execute(category, name string, args ...string) (*ToolResult, error) {
	started := time.Now()
	path := tb.scriptPath(category, name)
	if _, err := os.Stat(path); err != nil {
		return nil, fmt.Errorf("找不到腳本：%s: %w", path, err)
	}
	// 以 /bin/bash 執行，捕捉 stdout/stderr
	cmd := exec.CommandContext(context.Background(), "/bin/bash", append([]string{path}, args...)...)
	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		// 將 stderr 也納入訊息方便除錯
		msg := strings.TrimSpace(stderr.String())
		if msg == "" {
			msg = err.Error()
		}
		res := &ToolResult{
			Status:     "error",
			Message:    msg,
			Data:       json.RawMessage(`{}`),
			StartedAt:  started,
			EndedAt:    time.Now(),
			DurationMs: time.Since(started).Milliseconds(),
		}
		return res, nil
	}

	out := strings.TrimSpace(stdout.String())
	// 工具約定輸出為單一 JSON 物件字串
	var parsed map[string]any
	if err := json.Unmarshal([]byte(out), &parsed); err != nil {
		// 若非 JSON，則包一層
		parsed = map[string]any{"status": "ok", "message": "raw", "data": out}
	}
	// 正規化欄位
	status := fmt.Sprintf("%v", parsed["status"])
	message := fmt.Sprintf("%v", parsed["message"])
	dataRaw, _ := json.Marshal(parsed["data"])

	res := &ToolResult{
		Status:     status,
		Message:    message,
		Data:       dataRaw,
		StartedAt:  started,
		EndedAt:    time.Now(),
		DurationMs: time.Since(started).Milliseconds(),
	}
	return res, nil
}

// DiscoverTools 列出各分類可用的工具清單。
func (tb *ToolBridge) DiscoverTools() map[string][]string {
	tools := map[string][]string{}
	categories := []string{"diagnostic", "config", "remediation"}
	for _, cat := range categories {
		catPath := filepath.Join(tb.toolsDir, cat)
		matches, _ := filepath.Glob(filepath.Join(catPath, "*.sh"))
		for _, file := range matches {
			base := filepath.Base(file)
			name := strings.TrimSuffix(base, ".sh")
			tools[cat] = append(tools[cat], name)
		}
	}
	return tools
}
