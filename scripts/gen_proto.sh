
  #!/usr/bin/env bash
  # 目的：產生 Go 端的 gRPC 代碼（繁體中文註解）。
  set -euo pipefail

  PROTO=contracts/proto/agent_bridge.proto
  OUT=contracts/gen/go

  mkdir -p "$OUT"
  protoc \
--go_out="$OUT" --go_opt=paths=source_relative \
--go-grpc_out="$OUT" --go-grpc_opt=paths=source_relative \
"$PROTO"
  echo "已產生 Go 端 gRPC 代碼於 $OUT"
