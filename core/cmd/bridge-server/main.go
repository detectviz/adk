//go:build ignore

// 上述 build tag 僅為避免在未生成 pb 之前造成編譯失敗。
// 移除後即可正常編譯（繁體中文註解）。
package main

import (
	"log"
	"net"
	pb "sre-assistant/contracts/gen/go/contracts/proto"
	"sre-assistant/core/internal/bridge"

	"google.golang.org/grpc"
)

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("listen: %v", err)
	}
	s := grpc.NewServer()
	b := bridge.NewToolBridge("core/tools")
	srv := bridge.NewServer(b)
	pb.RegisterAgentBridgeServer(s, srv)
	log.Println("AgentBridge 服務已啟動 :50051")
	if err := s.Serve(lis); err != nil {
		log.Fatalf("serve: %v", err)
	}
}
