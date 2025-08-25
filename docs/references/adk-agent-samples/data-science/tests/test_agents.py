# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""分析代理及其子代理的測試案例。"""

import os
import sys
import pytest
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from google.genai import types
from google.adk.artifacts import InMemoryArtifactService
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

from data_science.agent import root_agent
from data_science.sub_agents.bqml.agent import root_agent as bqml_agent
from data_science.sub_agents.bigquery.agent import database_agent

session_service = InMemorySessionService()
artifact_service = InMemoryArtifactService()


class TestAgents(unittest.TestCase):
    """分析代理及其子代理的測試案例。"""

    def setUp(self):
        """為測試方法進行設定。"""
        self.session = session_service.create_session(
            app_name="DataAgent",
            user_id="test_user",
        )
        self.user_id = "test_user"
        self.session_id = self.session.id

        self.runner = Runner(
            app_name="DataAgent",
            agent=None,
            artifact_service=artifact_service,
            session_service=session_service,
        )

    def _run_agent(self, agent, query):
        """執行代理並取得最終回應的輔助方法。"""
        self.runner.agent = agent
        content = types.Content(role="user", parts=[types.Part(text=query)])
        events = list(
            self.runner.run(
                user_id=self.user_id, session_id=self.session_id, new_message=content
            )
        )

        last_event = events[-1]
        final_response = "".join(
            [part.text for part in last_event.content.parts if part.text]
        )
        return final_response


    @pytest.mark.db_agent
    def test_db_agent_can_handle_env_query(self):
        """使用來自環境變數的查詢測試 db_agent。"""
        query = "what countries exist in the train table?"
        response = self._run_agent(database_agent, query)
        print(response)
        # self.assertIn("Canada", response)
        self.assertIsNotNone(response)

    @pytest.mark.ds_agent
    def test_ds_agent_can_be_called_from_root(self):
        """從根代理測試 ds_agent。"""
        query = "plot the most selling category"
        response = self._run_agent(root_agent, query)
        print(response)
        self.assertIsNotNone(response)

    @pytest.mark.bqml
    def test_bqml_agent_can_check_for_models(self):
        """測試 bqml_agent 是否可以檢查現有模型。"""
        query = "Are there any existing models in the dataset?"
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response)

    @pytest.mark.bqml
    def test_bqml_agent_can_execute_code(self):
        """測試 bqml_agent 是否可以執行 BQML 程式碼。"""
        query = """
    I want to train a BigQuery ML model on the sales_train_validation data for sales prediction.
    Please show me an execution plan. 
    """
        response = self._run_agent(bqml_agent, query)
        print(response)
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()

    # testagent = TestAgents
    # testagent.setUp(testagent)
    # testagent.test_root_agent_can_list_tools(testagent)
    # testagent.test_db_agent_can_handle_env_query(testagent)
