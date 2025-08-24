# 參考資源分析與借鏡

作為 Google ADK 首席架構師，深入分析 `docs/references` 中的官方範例，找出可以借鏡加強 SRE Assistant 的關鍵點：

## 1. [RAG 範例的深入借鏡](docs/references/adk-samples-agents/RAG)

### 1. **引用格式標準化**
```python
# 建議為 SRE Assistant 加入
class SRECitationFormatter:
    """標準化的引用格式管理"""
    
    def format_citation(self, sources: List[Dict]) -> str:
        """
        格式化引用來源
        
        範例輸出：
        Citations:
        1) Prometheus Alert Rules: CPU Usage Monitoring (prometheus.yml:L45)
        2) K8s Deployment Guide: Rolling Update Strategy (k8s-docs/deployment.md)
        3) Incident #12345: Similar CPU Spike Resolution (2024-08-20)
        """
        citations = []
        for idx, source in enumerate(sources, 1):
            if source['type'] == 'config':
                citation = f"{source['name']}: {source['section']} ({source['file']}:{source['line']})"
            elif source['type'] == 'incident':
                citation = f"Incident #{source['id']}: {source['title']} ({source['date']})"
            elif source['type'] == 'documentation':
                citation = f"{source['title']}: {source['section']} ({source['path']})"
            citations.append(f"{idx}) {citation}")
        
        return "Citations:\n" + "\n".join(citations)
```

#### 2. **智能檢索策略**
```python
# 改進 SRE 記憶體系統
class EnhancedSREMemorySystem(SREMemorySystem):
    """增強的 RAG 檢索系統"""
    
    def __init__(self):
        super().__init__()
        self.retrieval_config = {
            'similarity_top_k': 10,
            'vector_distance_threshold': 0.6,
            'reranking_enabled': True,
            'hybrid_search': True  # 結合向量和關鍵字搜索
        }
    
    async def smart_retrieve(self, query: str, context: Dict) -> List[Dict]:
        """智能檢索相關資訊"""
        # 1. 判斷查詢意圖
        intent = self._classify_intent(query)
        
        # 2. 根據意圖調整檢索策略
        if intent == 'troubleshooting':
            # 優先檢索相似事件和解決方案
            return await self._retrieve_incidents_and_solutions(query)
        elif intent == 'configuration':
            # 檢索配置範例和最佳實踐
            return await self._retrieve_configs_and_docs(query)
        elif intent == 'monitoring':
            # 檢索監控規則和 dashboard
            return await self._retrieve_monitoring_resources(query)
        else:
            # 通用檢索
            return await self._general_retrieval(query)
```

## 2. [Machine Learning Engineering 範例的深入借鏡](docs/references/adk-samples-agents/machine-learning-engineering)

### 1. **迭代優化框架**
```python
# 借鏡 ML 範例的迭代優化模式
class SREIterativeOptimizer:
    """SRE 配置迭代優化器"""
    
    def __init__(self):
        self.max_iterations = 5
        self.improvement_threshold = 0.1
        self.state_manager = OptimizationStateManager()
    
    async def optimize_slo_configuration(self, current_config: Dict) -> Dict:
        """迭代優化 SLO 配置"""
        best_config = current_config
        best_score = await self._evaluate_config(current_config)
        
        for iteration in range(self.max_iterations):
            # 1. 生成改進建議
            suggestions = await self._generate_improvements(best_config, iteration)
            
            # 2. 並行評估多個配置
            results = await asyncio.gather(*[
                self._evaluate_config(config) 
                for config in suggestions
            ])
            
            # 3. 選擇最佳配置
            for config, score in zip(suggestions, results):
                if score > best_score * (1 + self.improvement_threshold):
                    best_config = config
                    best_score = score
                    self.state_manager.save_iteration(iteration, config, score)
            
            # 4. 檢查收斂
            if self._has_converged(iteration):
                break
        
        return best_config
    
    async def _generate_improvements(self, config: Dict, iteration: int) -> List[Dict]:
        """生成配置改進建議"""
        improvements = []
        
        # 調整 SLO 目標
        if iteration < 2:
            # 早期迭代：大幅調整
            improvements.extend(self._adjust_slo_targets(config, step=0.1))
        else:
            # 後期迭代：微調
            improvements.extend(self._adjust_slo_targets(config, step=0.01))
        
        # 優化錯誤預算分配
        improvements.extend(self._optimize_error_budget(config))
        
        # 調整警報閾值
        improvements.extend(self._tune_alert_thresholds(config))
        
        return improvements
```

#### 2. **狀態管理與回調**
```python
# 借鏡 ML 範例的狀態管理
class SREWorkflowStateManager:
    """工作流狀態管理器"""
    
    def __init__(self):
        self.states = {}
        self.checkpoints = []
        self.callbacks = {
            'before_diagnosis': [],
            'after_diagnosis': [],
            'before_remediation': [],
            'after_remediation': [],
            'on_error': [],
            'on_success': []
        }
    
    def register_callback(self, event: str, callback: Callable):
        """註冊回調函數"""
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    async def execute_callbacks(self, event: str, context: Dict):
        """執行回調"""
        for callback in self.callbacks.get(event, []):
            try:
                await callback(context, self.states)
            except Exception as e:
                logger.error(f"Callback failed for {event}: {e}")
    
    def save_checkpoint(self, name: str):
        """保存檢查點"""
        checkpoint = {
            'name': name,
            'timestamp': datetime.utcnow(),
            'states': self.states.copy()
        }
        self.checkpoints.append(checkpoint)
    
    def restore_checkpoint(self, name: str):
        """恢復到檢查點"""
        for checkpoint in reversed(self.checkpoints):
            if checkpoint['name'] == name:
                self.states = checkpoint['states'].copy()
                return True
        return False
```

## 3. [Data Science 範例的深入借鏡](docs/references/adk-samples-agents/data-science)

### BigQuery 整合模式

#### 1. **SQL 生成與驗證**
```python
# 借鏡 BigQuery 工具的 SQL 生成
class SREMetricsQueryBuilder:
    """SRE 指標查詢構建器"""
    
    def __init__(self):
        self.query_templates = {
            'error_rate': """
                SELECT 
                    TIMESTAMP_TRUNC(timestamp, MINUTE) as minute,
                    service_name,
                    COUNT(CASE WHEN status_code >= 500 THEN 1 END) / COUNT(*) as error_rate
                FROM `{project}.{dataset}.{table}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {window} MINUTE)
                GROUP BY minute, service_name
                HAVING error_rate > {threshold}
                ORDER BY minute DESC
                LIMIT {limit}
            """,
            'latency_percentile': """
                SELECT 
                    service_name,
                    APPROX_QUANTILES(latency_ms, 100)[OFFSET({percentile})] as p{percentile}_latency
                FROM `{project}.{dataset}.{table}`
                WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL {window} MINUTE)
                GROUP BY service_name
                HAVING p{percentile}_latency > {threshold}
            """
        }
    
    def build_query(self, metric_type: str, **params) -> str:
        """構建並驗證查詢"""
        template = self.query_templates.get(metric_type)
        if not template:
            raise ValueError(f"Unknown metric type: {metric_type}")
        
        # 驗證參數
        self._validate_params(metric_type, params)
        
        # 注入安全檢查
        params = self._sanitize_params(params)
        
        return template.format(**params)
    
    def _validate_params(self, metric_type: str, params: Dict):
        """驗證查詢參數"""
        required = {
            'error_rate': ['project', 'dataset', 'table', 'window', 'threshold', 'limit'],
            'latency_percentile': ['project', 'dataset', 'table', 'window', 'percentile', 'threshold']
        }
        
        missing = set(required.get(metric_type, [])) - set(params.keys())
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
```

## 4. [Software Bug Assistant 範例的深入借鏡](docs/references/adk-samples-agents/software-bug-assistant)

### GitHub 整合模式

#### 1. **Issue 追蹤整合**
```python
# 借鏡 GitHub 整合模式
class SREIncidentTracker:
    """SRE 事件追蹤器（整合 GitHub Issues）"""
    
    def __init__(self):
        self.github_client = GitHubClient()
        self.issue_template = {
            'title': '[SRE-{severity}] {service}: {summary}',
            'body': """
## Incident Details
- **Incident ID**: {incident_id}
- **Severity**: {severity}
- **Service**: {service}
- **Start Time**: {start_time}
- **Status**: {status}

## Impact
{impact_description}

## Root Cause
{root_cause}

## Resolution Steps
{resolution_steps}

## Follow-up Actions
- [ ] Update runbook
- [ ] Add monitoring
- [ ] Schedule postmortem
            """,
            'labels': ['sre-incident', 'auto-generated']
        }
    
    async def create_incident_issue(self, incident: Dict) -> str:
        """創建事件 Issue"""
        issue_data = {
            'title': self.issue_template['title'].format(**incident),
            'body': self.issue_template['body'].format(**incident),
            'labels': self._get_labels(incident)
        }
        
        issue = await self.github_client.create_issue(issue_data)
        return issue['url']
    
    async def link_pr_to_incident(self, incident_id: str, pr_url: str):
        """關聯 PR 到事件"""
        # 在 Issue 中添加 PR 連結
        comment = f"Related fix: {pr_url}"
        await self.github_client.add_comment(incident_id, comment)
```



## 5. [SRE Bot 範例的深度分析與借鏡](docs/references/other-samples/sre-bot)

### 1. **Session 管理的優秀實踐**

#### A. 完整的 Session 生命週期管理
```python
# 借鏡 sre-bot 的 session 管理模式
class EnhancedSessionManager:
    """增強的會話管理器"""
    
    def __init__(self):
        self.session_service = DatabaseSessionService(db_url=DB_URL)
        self.session_cache = {}
        self.cleanup_interval = 7200  # 2 小時
        
    def get_session(self, channel: str, user: str, thread_ts: str = None) -> ConversationSession:
        """智能會話管理"""
        # 1. 清理過期會話
        self._cleanup_expired_sessions()
        
        # 2. Thread 連續性支援
        thread_key = f"{channel}_{thread_ts}" if thread_ts else None
        
        # 3. 重用現有會話
        if thread_ts and thread_key in self.thread_session_map:
            existing_session_key = self.thread_session_map[thread_key]
            if existing_session_key in self.sessions and not self.sessions[existing_session_key].is_expired():
                session = self.sessions[existing_session_key]
                session.update_activity()
                return session
        
        # 4. 創建新會話
        key = f"{channel}_{user}_{thread_ts if thread_ts else 'main'}"
        if key not in self.sessions or self.sessions[key].is_expired():
            self.sessions[key] = ConversationSession(channel, user, thread_ts)
            if thread_ts:
                self.thread_session_map[thread_key] = key
                
        return self.sessions[key]
    
    def _cleanup_expired_sessions(self):
        """清理過期會話"""
        expired_keys = [k for k, v in self.sessions.items() if v.is_expired()]
        for k in expired_keys:
            # 清理 thread 映射
            expired_session = self.sessions[k]
            if expired_session.thread_ts:
                thread_key = f"{expired_session.channel}_{expired_session.thread_ts}"
                if thread_key in self.thread_session_map:
                    del self.thread_session_map[thread_key]
            del self.sessions[k]
```

### 2. **多服務通訊架構**

#### A. 服務間通訊模式
```python
# 借鏡 sre-bot 的多服務架構
class ServiceCommunicationLayer:
    """服務間通訊層"""
    
    def __init__(self):
        self.services = {
            'sre-bot-api': 'http://sre-bot-api:8000',
            'slack-bot': 'http://slack-bot:80',
            'postgres': 'postgresql://postgres:postgres@postgres:5432/srebot'
        }
        self.http_client = httpx.AsyncClient(timeout=120)
        
    async def create_api_session(self, session: ConversationSession) -> bool:
        """創建 API 會話"""
        url = f"{self.services['sre-bot-api']}/apps/sre_agent/users/{session.user_id}/sessions/{session.session_id}"
        payload = {
            'state': {
                'channel': session.channel,
                'thread_ts': session.thread_ts,
                'slack_user': session.user,
            }
        }
        
        try:
            async with self.http_client.post(url, json=payload, timeout=10) as response:
                if response.status == 200:
                    return True
                elif response.status == 400 and "already exists" in await response.text():
                    # 會話已存在也視為成功
                    return True
                return False
        except asyncio.TimeoutError:
            logger.error("Connection timeout to sre-bot-api")
            return False
```

### 3. **AWS Cost Analysis 整合**

#### A. 成本分析工具整合
```python
# 借鏡 AWS Cost 工具的實現
class SRECostAnalyzer:
    """SRE 成本分析器"""
    
    def __init__(self):
        self.cost_explorer = boto3.client("ce")
        self._thread_pool = ThreadPoolExecutor()
        
    async def analyze_incident_cost(self, incident_id: str) -> Dict:
        """分析事件相關成本"""
        # 1. 獲取事件時間範圍
        incident = await self.get_incident(incident_id)
        start_time = incident['start_time']
        end_time = incident['end_time'] or datetime.now()
        
        # 2. 計算相關服務成本
        costs = await self._get_cost_for_period(
            start_date=start_time.strftime('%Y-%m-%d'),
            end_date=end_time.strftime('%Y-%m-%d'),
            filter_expression={
                'Tags': {
                    'Key': 'incident_id',
                    'Values': [incident_id]
                }
            }
        )
        
        # 3. 計算資源浪費
        waste_analysis = await self._analyze_resource_waste(costs)
        
        return {
            'total_cost': costs['total'],
            'breakdown': costs['by_service'],
            'waste_analysis': waste_analysis,
            'optimization_suggestions': self._generate_cost_optimizations(waste_analysis)
        }
    
    async def _analyze_resource_waste(self, costs: Dict) -> Dict:
        """分析資源浪費"""
        waste = {
            'idle_resources': 0,
            'over_provisioned': 0,
            'unnecessary_retries': 0
        }
        
        # 分析閒置資源
        if 'EC2' in costs['by_service']:
            cpu_utilization = await self._get_cpu_utilization()
            if cpu_utilization < 10:
                waste['idle_resources'] = costs['by_service']['EC2'] * 0.8
        
        return waste
```

### 4. **Kubernetes 工具的完整實現**

#### A. 增強的 K8s 操作工具
```python
# 借鏡完整的 Kubernetes 工具實現
class EnhancedK8sTools:
    """增強的 Kubernetes 工具集"""
    
    def __init__(self):
        config.load_config()
        self.api_v1 = client.CoreV1Api()
        self.apps_v1 = client.AppsV1Api()
        self.batch_v1 = client.BatchV1Api()
        
    def get_events(self, namespace: str = "default", 
                   limit: int = 200,
                   time_window_minutes: Optional[int] = None) -> List[Dict]:
        """獲取 K8s 事件（支援時間窗口過濾）"""
        try:
            events = self.api_v1.list_namespaced_event(namespace, limit=limit)
            formatted_events = self._format_k8s_events(events.items)
            
            # 時間窗口過濾
            if time_window_minutes:
                cutoff_time = datetime.now(timezone.utc) - timedelta(minutes=time_window_minutes)
                formatted_events = [
                    event for event in formatted_events
                    if event["last_seen"] and 
                    datetime.fromisoformat(event["last_seen"]) >= cutoff_time
                ]
            
            return formatted_events
        except ApiException as e:
            return [{"error": f"Failed to get events: {str(e)}"}]
    
    def _format_k8s_events(self, events_items: List) -> List[Dict]:
        """格式化 K8s 事件"""
        formatted_events = []
        for event in events_items:
            formatted_events.append({
                'name': event.metadata.name,
                'namespace': event.metadata.namespace,
                'type': event.type,
                'reason': event.reason,
                'message': event.message,
                'source': {
                    'component': event.source.component if event.source else None,
                    'host': event.source.host if event.source else None,
                },
                'first_seen': event.first_timestamp.isoformat() if event.first_timestamp else None,
                'last_seen': event.last_timestamp.isoformat() if event.last_timestamp else None,
                'count': event.count,
                'involved_object': {
                    'kind': event.involved_object.kind,
                    'name': event.involved_object.name,
                    'namespace': event.involved_object.namespace,
                } if event.involved_object else None,
            })
        return formatted_events
```

### 5. **Slack 整合的最佳實踐**

#### A. 異步 Slack 處理
```python
# 借鏡 Slack 整合模式
class EnhancedSlackIntegration:
    """增強的 Slack 整合"""
    
    def __init__(self):
        self.app = AsyncApp()
        self.session_manager = SessionManager()
        
    async def handle_message_events(self, body, say, client, logger):
        """處理消息事件"""
        event = body.get("event", {})
        
        if event.get("type") == "message" and "text" in event:
            user = event.get("user")
            text = event.get("text")
            channel = event.get("channel")
            thread_ts = event.get("thread_ts", event.get("ts"))
            
            # 避免響應機器人自己的消息
            if not event.get("bot_id") and user:
                # 1. 快速確認
                await say({
                    "text": f"處理中 <@{user}>，請稍候...",
                    "thread_ts": thread_ts,
                })
                
                # 2. 異步處理
                asyncio.create_task(
                    self.process_message_with_api(
                        client=client,
                        channel=channel,
                        thread_ts=thread_ts,
                        user=user,
                        message=text,
                    )
                )
    
    async def process_message_with_api(self, client, channel, thread_ts, user, message):
        """處理消息並調用 API"""
        try:
            # 獲取或創建會話
            session = self.session_manager.get_session(channel, user, thread_ts)
            
            # 創建 API 會話
            session_created = await self.create_api_session(session)
            
            if not session_created:
                await self.send_error_message(client, channel, thread_ts, user)
                return
            
            # 發送消息到 API
            response = await self.send_message_to_api(session, message)
            
            # 返回響應
            await client.chat_postMessage(
                channel=channel,
                text=response,
                thread_ts=thread_ts
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await client.chat_postMessage(
                channel=channel,
                text=f"抱歉 <@{user}>，處理請求時發生錯誤。",
                thread_ts=thread_ts
            )
```

### 6. **JSON 序列化處理**

#### A. 自定義 JSON 編碼器
```python
# 借鏡 JSON 處理模式
import json
from datetime import datetime
import functools

class DateTimeEncoder(json.JSONEncoder):
    """處理 datetime 的 JSON 編碼器"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Monkey patch json.dumps
original_dumps = json.dumps
json.dumps = functools.partial(original_dumps, cls=DateTimeEncoder)

# 在 SRE Assistant 中應用
class SREResponseSerializer:
    """SRE 響應序列化器"""
    
    @staticmethod
    def serialize(response: Any) -> str:
        """安全序列化響應"""
        try:
            # 處理各種響應格式
            if isinstance(response, list) and response:
                # ADK 事件結構
                if "id" in response[-1] and "content" in response[-1]:
                    event = response[-1]
                    if isinstance(event["content"], dict) and "parts" in event["content"]:
                        parts = event["content"]["parts"]
                        if parts and isinstance(parts[0], dict) and "text" in parts[0]:
                            return parts[0]["text"]
            
            # 默認序列化
            return json.dumps(response, cls=DateTimeEncoder)
            
        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return str(response)
```

### 7. **Docker Compose 最佳實踐**

#### A. 多服務編排
```yaml
# 借鏡 docker-compose.yml 配置
version: '3.8'

services:
  sre-assistant-web:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - DB_HOST=postgres
      - DB_PORT=5432
      - LOG_LEVEL=INFO
    volumes:
      - ${HOME}/.kube:/root/.kube:ro
      - ${HOME}/.aws:/root/.aws:ro
    command: ["adk", "web", "--session_db_url=postgresql://postgres:postgres@postgres:5432/srebot"]
    depends_on:
      - postgres
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:17
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-postgres}
      - POSTGRES_DB=srebot
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  postgres_data:
```

### 8. 綜合改進建議

基於 `sre-bot` 範例的分析，SRE Assistant 可以實施以下關鍵改進：

### 1. **完整的 Session 管理系統**

```python
# 整合 sre-bot 的 session 管理
class ProductionSessionManager:
    """生產級會話管理器"""
    
    def __init__(self):
        self.db_service = DatabaseSessionService(db_url=DB_URL)
        self.thread_mapping = {}  # Thread 到會話的映射
        self.cache = TTLCache(maxsize=1000, ttl=7200)
        self.lock = asyncio.Lock()
        
    async def get_or_create_session(self, 
                                   app_name: str,
                                   user_id: str,
                                   context: Dict = None) -> str:
        """獲取或創建會話"""
        async with self.lock:
            # 檢查緩存
            cache_key = f"{app_name}:{user_id}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # 從數據庫獲取
            existing = self.db_service.list_sessions(app_name, user_id)
            if existing.sessions:
                session_id = existing.sessions[0].id
                self.cache[cache_key] = session_id
                return session_id
            
            # 創建新會話
            new_session = self.db_service.create_session(
                app_name=app_name,
                user_id=user_id,
                state=context or {}
            )
            self.cache[cache_key] = new_session.id
            return new_session.id
```

### 2. **多模型支援**

```python
# 借鏡 LiteLLM 整合
class MultiModelSupport:
    """多模型支援"""
    
    def __init__(self):
        self.models = {
            'gemini': LiteLlm(model="gemini-2.5-flash"),
            'claude': LiteLlm(model="bedrock/anthropic.claude-3-7-sonnet"),
            'deepseek': LiteLlm(model="bedrock/deepseek.r1-v1:0")
        }
        
    def get_model_for_task(self, task_type: str) -> LiteLlm:
        """根據任務類型選擇模型"""
        if task_type == 'diagnosis':
            return self.models['gemini']  # 診斷用 Gemini
        elif task_type == 'code_generation':
            return self.models['deepseek']  # 代碼生成用 DeepSeek
        elif task_type == 'report':
            return self.models['claude']  # 報告用 Claude
        return self.models['gemini']  # 默認
```

### 3. **健康檢查與監控**

```python
# 完整的健康檢查系統
class HealthCheckSystem:
    """健康檢查系統"""
    
    def __init__(self):
        self.checks = {
            'database': self.check_database,
            'kubernetes': self.check_kubernetes,
            'aws': self.check_aws,
            'models': self.check_models
        }
        
    async def health_check(self) -> Dict:
        """執行健康檢查"""
        results = {}
        for name, check_func in self.checks.items():
            try:
                results[name] = await check_func()
            except Exception as e:
                results[name] = {
                    'status': 'unhealthy',
                    'error': str(e)
                }
        
        overall_status = 'healthy' if all(
            r.get('status') == 'healthy' for r in results.values()
        ) else 'unhealthy'
        
        return {
            'status': overall_status,
            'checks': results,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def check_database(self) -> Dict:
        """檢查數據庫連接"""
        try:
            # 執行簡單查詢
            result = await self.db.execute("SELECT 1")
            return {'status': 'healthy', 'latency_ms': result.latency}
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}
```

### 4. **成本優化建議系統**

```python
# 整合成本分析
class CostOptimizationAdvisor:
    """成本優化顧問"""
    
    def __init__(self):
        self.cost_analyzer = SRECostAnalyzer()
        self.resource_manager = ResourceManager()
        
    async def analyze_and_optimize(self, time_window: str = "7d") -> Dict:
        """分析並優化成本"""
        # 1. 獲取成本數據
        costs = await self.cost_analyzer.get_cost_trend(time_window)
        
        # 2. 識別浪費
        waste = await self.identify_waste(costs)
        
        # 3. 生成優化建議
        recommendations = []
        
        if waste['idle_resources'] > 100:
            recommendations.append({
                'type': 'resource_termination',
                'description': '終止閒置資源',
                'potential_savings': waste['idle_resources'],
                'risk': 'low'
            })
        
        if waste['over_provisioned'] > 50:
            recommendations.append({
                'type': 'right_sizing',
                'description': '調整資源規格',
                'potential_savings': waste['over_provisioned'],
                'risk': 'medium'
            })
        
        return {
            'current_cost': costs['total'],
            'waste_identified': sum(waste.values()),
            'recommendations': recommendations,
            'implementation_plan': self.create_implementation_plan(recommendations)
        }
```

### 5. **異步任務處理**

```python
# 借鏡異步處理模式
class AsyncTaskProcessor:
    """異步任務處理器"""
    
    def __init__(self):
        self.task_queue = asyncio.Queue()
        self.workers = []
        self.results = {}
        
    async def start_workers(self, num_workers: int = 5):
        """啟動工作線程"""
        for i in range(num_workers):
            worker = asyncio.create_task(self.worker(f"worker-{i}"))
            self.workers.append(worker)
    
    async def worker(self, name: str):
        """工作線程"""
        while True:
            try:
                task = await self.task_queue.get()
                result = await self.process_task(task)
                self.results[task['id']] = result
                self.task_queue.task_done()
            except Exception as e:
                logger.error(f"Worker {name} error: {e}")
    
    async def submit_task(self, task: Dict) -> str:
        """提交任務"""
        task_id = str(uuid.uuid4())
        task['id'] = task_id
        await self.task_queue.put(task)
        return task_id
    
    async def get_result(self, task_id: str, timeout: float = 60) -> Optional[Dict]:
        """獲取結果"""
        start = time.time()
        while time.time() - start < timeout:
            if task_id in self.results:
                return self.results.pop(task_id)
            await asyncio.sleep(0.1)
        return None
```

### 6. 最終整合建議

將 `sre-bot` 的優秀實踐整合到 SRE Assistant：

```python
# sre_assistant/core/enhanced_coordinator.py
class EnhancedSRECoordinator(SRECoordinator):
    """增強的 SRE 協調器"""
    
    def __init__(self):
        super().__init__()
        
        # 整合 sre-bot 的最佳實踐
        self.session_manager = ProductionSessionManager()
        self.multi_model = MultiModelSupport()
        self.health_check = HealthCheckSystem()
        self.cost_advisor = CostOptimizationAdvisor()
        self.async_processor = AsyncTaskProcessor()
        self.slack_integration = EnhancedSlackIntegration()
        
        # 啟動異步工作線程
        asyncio.create_task(self.async_processor.start_workers())
        
    async def execute_workflow(self, request: SRERequest) -> SREResponse:
        """執行增強的工作流"""
        # 1. 會話管理
        session_id = await self.session_manager.get_or_create_session(
            app_name="sre_assistant",
            user_id=request.user_id,
            context=request.context
        )
        
        # 2. 選擇合適的模型
        model = self.multi_model.get_model_for_task(request.task_type)
        
        # 3. 異步處理
        task_id = await self.async_processor.submit_task({
            'type': 'workflow',
            'request': request,
            'session_id': session_id,
            'model': model
        })
        
        # 4. 等待結果
        result = await self.async_processor.get_result(task_id)
        
        # 5. 成本分析（如果需要）
        if request.include_cost_analysis:
            cost_analysis = await self.cost_advisor.analyze_and_optimize()
            result['cost_analysis'] = cost_analysis
        
        return SREResponse(**result)
```

通過借鏡 `sre-bot` 的實踐，SRE Assistant 可以獲得：
1. **生產級的會話管理**
2. **多服務通訊架構**
3. **完整的 Kubernetes 工具集**
4. **AWS 成本分析能力**
5. **Slack 整合最佳實踐**
6. **健壯的錯誤處理**
7. **異步處理模式**

這些改進將使 SRE Assistant 更適合生產環境部署。


## 6. 綜合改進建議

### A. 建立統一的知識管理系統

```python
class UnifiedKnowledgeSystem:
    """統一的 SRE 知識管理系統"""
    
    def __init__(self):
        self.knowledge_sources = {
            'runbooks': RunbookRAG(),
            'incidents': IncidentHistoryRAG(),
            'configurations': ConfigRAG(),
            'metrics': MetricsRAG(),
            'documentation': DocRAG()
        }
        
        self.citation_manager = SRECitationFormatter()
        self.query_optimizer = QueryOptimizer()
    
    async def query(self, question: str, context: Dict) -> Dict:
        """統一查詢介面"""
        # 1. 優化查詢
        optimized_query = self.query_optimizer.optimize(question, context)
        
        # 2. 多源檢索
        results = await self._multi_source_retrieval(optimized_query)
        
        # 3. 重新排序
        reranked = self._rerank_results(results, question)
        
        # 4. 生成答案
        answer = await self._generate_answer(question, reranked)
        
        # 5. 添加引用
        answer['citations'] = self.citation_manager.format_citation(reranked)
        
        return answer
```

### B. 實現漸進式優化系統

```python
class ProgressiveOptimizationSystem:
    """漸進式 SRE 優化系統"""
    
    def __init__(self):
        self.optimization_stages = [
            QuickFixStage(),      # 快速修復
            PerformanceTuning(),   # 性能調優
            ConfigOptimization(),  # 配置優化
            ArchitectureReview()   # 架構審查
        ]
    
    async def optimize_system(self, issue: Dict) -> List[Dict]:
        """漸進式系統優化"""
        recommendations = []
        
        for stage in self.optimization_stages:
            # 執行優化階段
            stage_result = await stage.optimize(issue)
            recommendations.append(stage_result)
            
            # 評估是否需要繼續
            if stage_result['resolution_confidence'] > 0.9:
                break
        
        return recommendations
```

### C. 增強的評估框架

```python
class EnhancedSREEvaluator(SREAssistantEvaluator):
    """增強的 SRE 評估器"""
    
    def __init__(self):
        super().__init__()
        self.add_custom_metrics()
    
    def add_custom_metrics(self):
        """添加自定義指標"""
        self.custom_metrics = {
            'knowledge_coverage': self.evaluate_knowledge_coverage,
            'citation_accuracy': self.evaluate_citation_accuracy,
            'optimization_effectiveness': self.evaluate_optimization,
            'incident_prevention': self.evaluate_prevention
        }
    
    async def evaluate_knowledge_coverage(self, dataset: Dataset) -> float:
        """評估知識覆蓋率"""
        covered = 0
        total = len(dataset)
        
        for example in dataset:
            response = await self.agent.query(example.question)
            if response.get('sources') and len(response['sources']) > 0:
                covered += 1
        
        return covered / total
```


