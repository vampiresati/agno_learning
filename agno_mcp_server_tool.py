import asyncio
from pathlib import Path
from shlex import quote
from textwrap import dedent

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


async def run_agent(message: str) -> None:
    agent = Agent(
            instructions=[
                "You are a helpful calculator assistant",
            ],
            tools=[MCPTools("python -m mcp_server_calculator")],
            model=Ollama(id="qwen3:4b"),
        )


    await agent.aprint_response(message, stream=True)


# Example usage
if __name__ == "__main__":
    # Basic example - exploring project license
    asyncio.run(run_agent("What is 200+2*3-1*10"))
