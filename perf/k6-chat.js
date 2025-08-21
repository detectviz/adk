
// k6 壓測腳本：對 /api/v1/chat 發送請求以量測 P95
import http from 'k6/http';
import { sleep, check } from 'k6';

export const options = {
  vus: 10,
  duration: '30s',
};

export default function () {
  const url = __ENV.BASE_URL || 'http://localhost:8000/api/v1/chat';
  const payload = JSON.stringify({ message: 'diagnose cpu', session_id: 'k6' });
  const params = { headers: { 'Content-Type': 'application/json', 'X-API-Key': __ENV.X_API_KEY || 'devkey' } };
  const res = http.post(url, payload, params);
  check(res, { 'status 200': (r) => r.status === 200 });
  sleep(1);
}
