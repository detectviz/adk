import json
import os

from a2a.types import AgentCard
from auth0_api_python import ApiClient, ApiClientOptions
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, PlainTextResponse


api_client = ApiClient(
    ApiClientOptions(
        domain=os.getenv('HR_AUTH0_DOMAIN'),
        audience=os.getenv('HR_AGENT_AUTH0_AUDIENCE'),
    )
)


class OAuth2Middleware(BaseHTTPMiddleware):
    """使用 OAuth2 持有人權杖驗證 A2A 存取的 Starlette 中介軟體。"""

    def __init__(
        self,
        app: Starlette,
        agent_card: AgentCard = None,
        public_paths: list[str] = None,
    ):
        super().__init__(app)
        self.agent_card = agent_card
        self.public_paths = set(public_paths or [])

        # 處理代理 (Agent) 名片以識別在根目錄中定義了哪些（如果有的話）安全要求
        # 代理 (Agent) 名片，表示代理層級的驗證/授權。

        # 為此示範使用應用程式狀態（簡單起見）
        self.a2a_auth = {}

        # 處理驗證要求物件
        if agent_card.authentication:
            credentials = json.loads(
                agent_card.authentication.credentials or '{}'
            )
            if 'scopes' in credentials:
                self.a2a_auth = {
                    'required_scopes': credentials['scopes'].keys()
                }

        # # 處理安全要求物件
        # for sec_req in agent_card.security or []:
        #     # 由於我們預先驗證了（非詳盡的）安全方案和安全
        #     # 要求的已使用部分，因此以下程式碼將不執行任何驗證。

        #     # 空的安全要求物件表示您允許匿名存取，無需處理任何其他安全
        #     # 要求物件
        #     if not sec_req:
        #         break

        #     # 示範如何處理安全要求以設定用於
        #     # 驗證和/或授權代理 (Agent) 互動的機制。
        #     #
        #     # 注意：這純粹是為了支援範例而編寫的，僅用於示範目的。
        #     for name, scopes in sec_req.items():
        #         # sec_scheme = self.agent_card.security_schemes[name]

        #         # if not isinstance(sec_scheme, OAuth2SecurityScheme) or sec_scheme.flows.authorization_code is None:
        #         #     raise NotImplementedError('僅支援 OAuth2SecurityScheme -> ClientCredentialsOAuthFlow。')

        #         self.a2a_auth = { 'required_scopes': scopes }

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # 允許公用路徑和匿名存取
        if path in self.public_paths or not self.a2a_auth:
            return await call_next(request)

        # 驗證請求
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return self._unauthorized(
                '遺失或格式錯誤的授權標頭。', request
            )

        access_token = auth_header.split('Bearer ')[1]

        try:
            if self.a2a_auth:
                payload = await api_client.verify_access_token(
                    access_token=access_token
                )
                scopes = payload.get('scope', '').split()
                missing_scopes = [
                    s
                    for s in self.a2a_auth['required_scopes']
                    if s not in scopes
                ]
                if missing_scopes:
                    return self._forbidden(
                        f'遺失必要的範圍：{missing_scopes}', request
                    )

        except Exception as e:
            return self._forbidden(f'驗證失敗：{e}', request)

        return await call_next(request)

    def _forbidden(self, reason: str, request: Request):
        accept_header = request.headers.get('accept', '')
        if 'text/event-stream' in accept_header:
            return PlainTextResponse(
                f'錯誤：禁止：{reason}',
                status_code=403,
                media_type='text/event-stream',
            )
        return JSONResponse(
            {'error': '禁止', 'reason': reason}, status_code=403
        )

    def _unauthorized(self, reason: str, request: Request):
        accept_header = request.headers.get('accept', '')
        if 'text/event-stream' in accept_header:
            return PlainTextResponse(
                f'錯誤：未經授權：{reason}',
                status_code=401,
                media_type='text/event-stream',
            )
        return JSONResponse(
            {'error': '未經授權', 'reason': reason}, status_code=401
        )
