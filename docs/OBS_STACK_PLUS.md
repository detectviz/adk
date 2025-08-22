# 觀測堆疊加固
- Loki Derived Field：以正則擷取 `trace_id` 鏈到 Tempo。
- docker-compose 加入持久卷與 healthcheck（生產請使用外部儲存與備援）。
