package bridge

import (
	"context"
	"encoding/json"
	"fmt"
	"os/exec"
	"path/filepath"
	"time"
)

type ToolBridge struct {
	toolsDir string
}

type ToolResult struct {
	Status  string          `json:"status"`
	Message string          `json:"message"`
	Data    json.RawMessage `json:"data"`
}

type ToolExecutor interface {
	Execute(ctx context.Context, req *ToolRequest) (*ToolResult, error)
	WithTimeout(duration time.Duration) ToolExecutor
	WithRetry(attempts int) ToolExecutor
	WithCircuitBreaker(threshold int) ToolExecutor
}

// 執行 Shell 腳本工具
func (tb *ToolBridge) Execute(toolType, toolName string, args ...string) (*ToolResult, error) {
	// 構建腳本路徑
	scriptPath := filepath.Join(tb.toolsDir, toolType, toolName+".sh")

	// 執行腳本
	cmd := exec.Command("/bin/bash", append([]string{scriptPath}, args...)...)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("failed to execute tool: %w", err)
	}

	// 解析 JSON 結果
	var result ToolResult
	if err := json.Unmarshal(output, &result); err != nil {
		return nil, fmt.Errorf("failed to parse tool output: %w", err)
	}

	return &result, nil
}

// 工具註冊和發現
func (tb *ToolBridge) DiscoverTools() map[string][]string {
	tools := make(map[string][]string)

	categories := []string{"diagnostic", "config", "remediation"}
	for _, cat := range categories {
		catPath := filepath.Join(tb.toolsDir, cat)
		files, _ := filepath.Glob(filepath.Join(catPath, "*.sh"))

		for _, file := range files {
			name := filepath.Base(file)
			name = name[:len(name)-3] // 移除 .sh
			tools[cat] = append(tools[cat], name)
		}
	}

	return tools
}
