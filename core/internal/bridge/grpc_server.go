package bridge

import (
	"context"
	pb "sre-assistant/contracts/proto"
)

type Server struct {
	pb.UnimplementedAgentBridgeServer
	bridge *ToolBridge
}

func (s *Server) ExecuteTool(ctx context.Context, req *pb.ToolRequest) (*pb.ToolResponse, error) {
	// 執行工具
	result, err := s.bridge.Execute(req.Category, req.Name, req.Args...)
	if err != nil {
		return &pb.ToolResponse{
			Success: false,
			Error:   err.Error(),
		}, nil
	}

	// 返回結果
	return &pb.ToolResponse{
		Success: true,
		Status:  result.Status,
		Message: result.Message,
		Data:    string(result.Data),
	}, nil
}

func (s *Server) DiscoverTools(ctx context.Context, req *pb.Empty) (*pb.ToolsResponse, error) {
	tools := s.bridge.DiscoverTools()
	return &pb.ToolsResponse{Tools: tools}, nil
}
