# Tests to add for software-bug-assistant (summary)

Unit tests
- test_tool_invocation_sequence
  - Arrange: mock runtime.tool_runner.invoke
  - Act: feed a synthetic Observation (error_rate_spike)
  - Assert: expected sequence:
    1) tool_runner.invoke("log_fetch", params) with correct time range
    2) tool_runner.invoke("git_search", params) when stack trace hints commit
    3) runtime.kv_store.set("last_investigation", <id>)
- test_http_client_retries_and_backoff
  - Mock runtime.http_client to fail first two times then succeed, assert retry count and backoff delays (use fast fake clock)
- test_state_persistence_and_recovery
  - Simulate kv_store.get returning partial state, verify agent recovers and continues investigation
- test_error_paths
  - tool failures -> AgentResponse.status == "error" and error_message populated

Integration / Contract tests
- fake AgentService server
  - Verify serialized AgentRequest fields: agent_id, observations, metadata
  - Return AgentResponse with a TriageAction; assert agent performs corresponding tool invocations
- tool-runner contract
  - Run agent against a local fake MCP/ToolRunner implementation that records calls and returns canned responses

E2E tests
- containerized run
  - Run agent in container with injected fake runtime (http_client, tool_runner, kv_store)
  - End-to-end scenario: inject monitoring alert -> agent collects logs -> proposes fix -> persists snapshot
  - Assertions: final AgentResponse.actions contains FixPatch with apply_procedure "create PR"

CI integration
- Add job "agent-contract-tests" that:
  - Generates proto stubs
  - Runs fake AgentService and runs contract tests
- Add job "agent-unit" with mocks for runtime.* APIs
