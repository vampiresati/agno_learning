from agno.agent import Agent
from custom_agno_tool import TimeTools
from agno.models.ollama import Ollama

agent_time_full = Agent(
    model=Ollama(id="qwen3:4b",),
    tools=[TimeTools()],  # All functions enabled by default
    description="You are a Time teller assistant.",
    instructions=[
        "Provide detailed current time",
    ],
    markdown=True,
)

if __name__ == "__main__":
    print("=== time teller Example ===")
    agent_time_full.print_response("what is current time now", markdown=True)
