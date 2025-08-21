import dotenv, os
dotenv.load_dotenv()  # May skip if you have exported environment variables.
from vertexai import agent_engines

agent_engine_id = os.getenv("AGENT_ENGINE_ID")
user_input = "cat riding  a bicycle"

agent_engine = agent_engines.get(agent_engine_id)

session = agent_engine.create_session(user_id="new_user")
for event in agent_engine.stream_query(user_id="new_user", session_id=session["id"], message=user_input):
    print(event)