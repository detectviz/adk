import os

from datetime import datetime, timedelta
from typing import Any

from github import Auth, Github
from pydantic import BaseModel


class GitHubUser(BaseModel):
    """GitHub 使用者資訊"""

    login: str
    name: str | None = None
    email: str | None = None


class GitHubRepository(BaseModel):
    """GitHub 儲存庫資訊"""

    name: str
    full_name: str
    description: str | None = None
    url: str
    updated_at: str
    pushed_at: str | None = None
    language: str | None = None
    stars: int
    forks: int


class GitHubCommit(BaseModel):
    """GitHub 提交資訊"""

    sha: str
    message: str
    author: str
    date: str
    url: str


class GitHubResponse(BaseModel):
    """GitHub API 操作的基本回應模型"""

    status: str
    message: str
    count: int | None = None
    error_message: str | None = None


class RepositoryResponse(GitHubResponse):
    """儲存庫操作的回應模型"""

    data: list[GitHubRepository] | None = None


class CommitResponse(GitHubResponse):
    """提交操作的回應模型"""

    data: list[GitHubCommit] | None = None


class GitHubToolset:
    """用於查詢儲存庫和最近更新的 GitHub API 工具集"""

    def __init__(self):
        self._github_client = None

    def _get_github_client(self) -> Github:
        """取得帶有驗證的 GitHub 用戶端"""
        if self._github_client is None:
            github_token = os.getenv('GITHUB_TOKEN')
            if github_token:
                auth = Auth.Token(github_token)
                self._github_client = Github(auth=auth)
            else:
                # 不使用驗證（有限速率）
                print(
                    '警告：找不到 GITHUB_TOKEN，使用未經身份驗證的存取（有限速率）'
                )
                self._github_client = Github()
        return self._github_client

    def get_user_repositories(
        self,
        username: str | None = None,
        days: int | None = None,
        limit: int | None = None,
    ) -> RepositoryResponse:
        """取得使用者最近更新的儲存庫
        參數：
            username：GitHub 使用者名稱（可選，預設為已驗證的使用者）
            days：尋找最近更新的天數（預設：30 天）
            limit：要傳回的最大儲存庫數量（預設：10）

        傳回：
            RepositoryResponse：包含狀態、儲存庫列表和元數據
        """
        # 設定預設值
        if days is None:
            days = 30
        if limit is None:
            limit = 10

        try:
            github = self._get_github_client()

            if username:
                user = github.get_user(username)
            else:
                try:
                    user = github.get_user()
                except Exception:
                    # 如果沒有權杖，我們無法取得已驗證的使用者，因此需要使用者名稱
                    return RepositoryResponse(
                        status='error',
                        message='未使用驗證權杖時需要使用者名稱',
                        error_message='未使用驗證權杖時需要使用者名稱',
                    )

            repos = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for repo in user.get_repos(sort='updated', direction='desc'):
                if len(repos) >= limit:
                    break

                if repo.updated_at >= cutoff_date:
                    repos.append(
                        GitHubRepository(
                            name=repo.name,
                            full_name=repo.full_name,
                            description=repo.description,
                            url=repo.html_url,
                            updated_at=repo.updated_at.isoformat(),
                            pushed_at=repo.pushed_at.isoformat()
                            if repo.pushed_at
                            else None,
                            language=repo.language,
                            stars=repo.stargazers_count,
                            forks=repo.forks_count,
                        )
                    )

            return RepositoryResponse(
                status='success',
                data=repos,
                count=len(repos),
                message=f'成功擷取在過去 {days} 天內更新的 {len(repos)} 個儲存庫',
            )
        except Exception as e:
            return RepositoryResponse(
                status='error',
                message=f'無法取得儲存庫：{e!s}',
                error_message=f'無法取得儲存庫：{e!s}',
            )

    def get_recent_commits(
        self, repo_name: str, days: int | None = None, limit: int | None = None
    ) -> CommitResponse:
        """取得儲存庫的最近提交

        參數：
            repo_name：格式為 'owner/repo' 的儲存庫名稱
            days：尋找最近提交的天數（預設：7 天）
            limit：要傳回的最大提交數量（預設：10）

        傳回：
            CommitResponse：包含狀態、提交列表和元數據
        """
        # 設定預設值
        if days is None:
            days = 7
        if limit is None:
            limit = 10

        try:
            github = self._get_github_client()

            repo = github.get_repo(repo_name)
            commits = []
            cutoff_date = datetime.now() - timedelta(days=days)

            for commit in repo.get_commits(since=cutoff_date):
                if len(commits) >= limit:
                    break

                commits.append(
                    GitHubCommit(
                        sha=commit.sha[:8],
                        message=commit.commit.message.split('\n')[
                            0
                        ],  # 只取第一行
                        author=commit.commit.author.name,
                        date=commit.commit.author.date.isoformat(),
                        url=commit.html_url,
                    )
                )

            return CommitResponse(
                status='success',
                data=commits,
                count=len(commits),
                message=f'成功擷取儲存庫 {repo_name} 在過去 {days} 天內的 {len(commits)} 個提交',
            )
        except Exception as e:
            return CommitResponse(
                status='error',
                message=f'無法取得提交：{e!s}',
                error_message=f'無法取得提交：{e!s}',
            )

    def search_repositories(
        self, query: str, sort: str | None = None, limit: int | None = None
    ) -> RepositoryResponse:
        """搜尋最近有活動的儲存庫

        參數：
            query：搜尋查詢字串
            sort：排序方法，可選值：'updated'、'stars'、'forks'（預設：'updated'）
            limit：要傳回的最大儲存庫數量（預設：10）

        傳回：
            RepositoryResponse：包含狀態、搜尋結果和元數據
        """
        # 設定預設值
        if sort is None:
            sort = 'updated'
        if limit is None:
            limit = 10

        try:
            github = self._get_github_client()

            # 將最近活動篩選器新增至查詢
            search_query = f'{query} pushed:>={datetime.now() - timedelta(days=30):%Y-%m-%d}'

            repos = []
            results = github.search_repositories(
                query=search_query, sort=sort, order='desc'
            )

            for repo in results[:limit]:
                repos.append(
                    GitHubRepository(
                        name=repo.name,
                        full_name=repo.full_name,
                        description=repo.description,
                        url=repo.html_url,
                        updated_at=repo.updated_at.isoformat(),
                        pushed_at=repo.pushed_at.isoformat()
                        if repo.pushed_at
                        else None,
                        language=repo.language,
                        stars=repo.stargazers_count,
                        forks=repo.forks_count,
                    )
                )

            return RepositoryResponse(
                status='success',
                data=repos,
                count=len(repos),
                message=f'成功搜尋到 {len(repos)} 個符合「{query}」的儲存庫',
            )
        except Exception as e:
            return RepositoryResponse(
                status='error',
                message=f'無法搜尋儲存庫：{e!s}',
                error_message=f'無法搜尋儲存庫：{e!s}',
            )

    def get_tools(self) -> dict[str, Any]:
        """傳回可用於 OpenAI 函式呼叫的工具字典"""
        return {
            'get_user_repositories': self,
            'get_recent_commits': self,
            'search_repositories': self,
        }
