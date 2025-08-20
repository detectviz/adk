
package main

import (
    "encoding/json"
    "fmt"
    "log"
    "os"
    "sre-assistant/core/internal/bridge"
)

func main() {
    if len(os.Args) < 3 {
        log.Fatalf("usage: %s <category> <name> [args...]", os.Args[0])
    }
    category := os.Args[1]
    name := os.Args[2]
    args := []string{}
    if len(os.Args) > 3 {
        args = os.Args[3:]
    }
    tb := bridge.NewToolBridge("core/tools")
    res, err := tb.Execute(category, name, args...)
    if err != nil {
        out := map[string]any{"status":"error","message": err.Error(), "data": map[string]any{}}
        enc := json.NewEncoder(os.Stdout)
        enc.SetEscapeHTML(false)
        _ = enc.Encode(out)
        os.Exit(1)
    }
    enc := json.NewEncoder(os.Stdout)
    enc.SetEscapeHTML(false)
    if err := enc.Encode(res); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
