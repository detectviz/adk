// 提供 AgentBridge gRPC 服務的最小實作樣板（需搭配 pb 代碼生成）。
package bridge

import (
	"context"
	"fmt"
	pb "sre-assistant/contracts/gen/go/contracts/proto"
)

type Server struct {
	pb.UnimplementedAgentBridgeServer
	bridge *ToolBridge
}

// NewServer 建立服務器（繁體中文註解）。
func NewServer(b *ToolBridge) *Server {
	return &Server{bridge: b}
}

// ExecuteTool 代理執行工具並回傳標準化結果。
func (s *Server) ExecuteTool(ctx context.Context, req *pb.ToolRequest) (*pb.ToolResponse, error) {
	if s.bridge == nil {
		return nil, fmt.Errorf("bridge 尚未初始化")
	}
	result, err := s.bridge.Execute(req.GetCategory(), req.GetName(), req.GetArgs()...)
	if err != nil {
		// 直接回傳 gRPC 錯誤
		return nil, err
	}
	return &pb.ToolResponse{
		Success: true,
		Status:  result.Status,
		Message: result.Message,
		Data:    string(result.Data),
	}, nil
}

// DiscoverTools 列出可用工具。
func (s *Server) DiscoverTools(ctx context.Context, _ *pb.Empty) (*pb.ToolsResponse, error) {
	tools := s.bridge.DiscoverTools()
	resp := &pb.ToolsResponse{Tools: map[string]*pb.ToolList{}}
	for cat, names := range tools {
		resp.Tools[cat] = &pb.ToolList{Names: names}
	}
	return resp, nil
}
