// 負載測試（k6）：對 /api/v1/chat 發送請求，觀察 P95 延遲
import http from 'k6/http';
import { sleep, check } from 'k6';

export let options = {
  vus: 5,
  duration: '30s',
};

export default function () {
  const url = __ENV.BASE_URL || 'http://localhost:8000/api/v1/chat';
  const payload = JSON.stringify({ message: 'diagnose cpu', session_id: 'perf' });
  const params = { headers: { 'Content-Type': 'application/json', 'X-API-Key': __ENV.API_KEY || 'devkey' } };
  let res = http.post(url, payload, params);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
