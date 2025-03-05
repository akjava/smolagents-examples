import os

from smolagents.agents import CodeAgent
from sleep_per_last_token_model import SleepPerLastTokenModelLiteLLM
from dotenv import load_dotenv

load_dotenv()

model = SleepPerLastTokenModelLiteLLM(
    model_id="groq/llama3-70b-8192",
    api_base="https://api.groq.com/openai/v1/",
    api_key=os.environ["GROQ_API_KEY"],
)
# model._flatten_messages_as_text = True
agent = CodeAgent(tools=[], model=model)
agent.run("make something joke")
