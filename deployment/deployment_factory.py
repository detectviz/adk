# src/sre_assistant/deployment/deployment_factory.py
from abc import ABC, abstractmethod
from typing import Dict, Any
import subprocess
import json
import os
import uvicorn

# Assuming config_manager is accessible, or passed in.
# To avoid circular dependency, we might need to pass config explicitly.
from ..config.config_manager import DeploymentConfig, config_manager

class DeploymentStrategy(ABC):
    """部署策略介面"""

    @abstractmethod
    async def deploy(self, config: DeploymentConfig) -> Dict[str, Any]:
        """執行部署"""
        pass

    @abstractmethod
    async def update(self, config: DeploymentConfig) -> Dict[str, Any]:
        """更新部署"""
        pass

    @abstractmethod
    async def rollback(self) -> Dict[str, Any]:
        """回滾部署"""
        pass

class AgentEngineDeployment(DeploymentStrategy):
    """Vertex AI Agent Engine 部署策略"""

    async def deploy(self, config: DeploymentConfig):
        # This is a placeholder for the actual SDK calls which can be complex.
        # The real implementation would use google.cloud.aiplatform.preview.agents
        print("Deploying to Vertex AI Agent Engine...")
        print(f"Project: {config.project_id}, Region: {config.region}")

        # Mocked response
        return {
            "status": "deployed",
            "endpoint_url": f"projects/{config.project_id}/locations/{config.region}/agents/sre_assistant",
            "platform": "agent_engine"
        }

    async def update(self, config: DeploymentConfig):
        print("Updating Agent Engine deployment...")
        return await self.deploy(config)

    async def rollback(self):
        print("Rolling back Agent Engine deployment...")
        return {"status": "rolled_back"}


class CloudRunDeployment(DeploymentStrategy):
    """Cloud Run 部署策略"""

    def _format_env_vars(self):
        memory_config = config_manager.get_memory_config()
        envs = [
            f"MEMORY_BACKEND={memory_config.backend.value}",
            f"WEAVIATE_URL={memory_config.weaviate_url or ''}",
            f"DATABASE_URL={memory_config.postgres_connection_string or ''}"
        ]
        return ",".join(envs)

    def _extract_service_url(self, output: str) -> str:
        for line in output.splitlines():
            if "Service URL:" in line:
                return line.split("Service URL:")[1].strip()
        return "URL not found"

    async def deploy(self, config: DeploymentConfig):
        print("Building container image for Cloud Run...")
        # Build command
        build_cmd = [
            "gcloud", "builds", "submit",
            "--tag", f"gcr.io/{config.project_id}/{config.service_name}",
            f"--project={config.project_id}"
        ]
        subprocess.run(build_cmd, check=True)

        print("Deploying to Cloud Run...")
        # Deploy command
        deploy_cmd = [
            "gcloud", "run", "deploy", config.service_name,
            "--image", f"gcr.io/{config.project_id}/{config.service_name}",
            "--platform", "managed",
            "--region", config.region,
            "--memory", config.memory,
            "--cpu", config.cpu,
            "--concurrency", str(config.concurrency),
            "--set-env-vars", self._format_env_vars(),
            "--allow-unauthenticated",
            f"--project={config.project_id}",
            "--quiet"
        ]
        result = subprocess.run(deploy_cmd, capture_output=True, text=True, check=True)

        return {
            "status": "deployed",
            "service_url": self._extract_service_url(result.stdout),
            "platform": "cloud_run"
        }

    async def update(self, config: DeploymentConfig):
        return await self.deploy(config)

    async def rollback(self):
        print("Rolling back Cloud Run deployment is typically done via the console or gcloud command to a previous revision.")
        return {"status": "manual_rollback_required"}

class GKEDeployment(DeploymentStrategy):
    """GKE 部署策略"""

    async def deploy(self, config: DeploymentConfig):
        print("Applying Kubernetes manifests for GKE deployment...")
        # This assumes k8s manifests are in a standard location
        subprocess.run([
            "kubectl", "apply", "-f", "deployment/k8s/",
            "--namespace", config.namespace
        ], check=True)

        print("Waiting for GKE deployment rollout to complete...")
        subprocess.run([
            "kubectl", "rollout", "status",
            "deployment/sre_assistant",
            "--namespace", config.namespace,
            "--timeout=5m"
        ], check=True)

        return {
            "status": "deployed",
            "platform": "gke",
            "namespace": config.namespace
        }

    async def update(self, config: DeploymentConfig):
        return await self.deploy(config)

    async def rollback(self):
        print("Rolling back GKE deployment...")
        subprocess.run([
            "kubectl", "rollout", "undo", "deployment/sre_assistant",
            "--namespace", config.namespace
        ], check=True)
        return {"status": "rolled_back"}

class LocalDeployment(DeploymentStrategy):
    """本地開發部署策略"""

    async def deploy(self, config: DeploymentConfig):
        print(f"Starting local server at http://{config.host}:{config.port}")
        # In a real app, you would run this in a separate process.
        # This is a placeholder for the command.
        # from sre_assistant import create_app # This would be the FastAPI app
        # app = create_app()
        # uvicorn.run(
        #     app,
        #     host=config.host,
        #     port=config.port,
        #     reload=config.debug
        # )
        return {
            "status": "running",
            "url": f"http://{config.host}:{config.port}",
            "platform": "local"
        }

    async def update(self, config: DeploymentConfig):
        print("Restart local server to apply changes.")
        return {"status": "manual_restart_required"}

    async def rollback(self):
        print("Stopping local server.")
        return {"status": "stopped"}

class DeploymentFactory:
    """部署工廠"""

    @staticmethod
    def create(config: DeploymentConfig) -> DeploymentStrategy:
        """根據配置創建部署策略"""

        strategy_map = {
            "agent_engine": AgentEngineDeployment,
            "cloud_run": CloudRunDeployment,
            "gke": GKEDeployment,
            "local": LocalDeployment
        }

        strategy_class = strategy_map.get(config.platform.value)
        if not strategy_class:
            raise ValueError(f"Unsupported platform: {config.platform.value}")

        return strategy_class()
