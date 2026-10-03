from agno.agent import Agent
from agno.models.ollama import Ollama

news_agent = Agent(
    name="News Agent",
    model=Ollama(id="qwen3:4b"),
    markdown=True,
)
news_agent.print_response("what is news today?",stream=True)