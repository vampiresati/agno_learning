import asyncio
import sys
from shlex import quote

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.mcp import MCPTools


async def run_agent(message: str) -> None:
    # Use Python from the same environment as this script.
    python = quote(sys.executable)

    async with (
        MCPTools(
            command=f"{python} -m mcp_server_calculator",
            timeout_seconds=30,
        ) as calculator,
        MCPTools(
            command=f"{python} -m wikipedia_mcp",
            timeout_seconds=60,
        ) as wikipedia,
    ):
        agent = Agent(
            model=Ollama(id="qwen3:4b"),
            tools=[calculator, wikipedia],
            instructions=[
                "Use the calculator tool for arithmetic.",
                "Use the Wikipedia tools for factual questions.",
                "If a tool fails or times out, retry it once.",
                "If the retry fails, clearly report the failure.",
                "Do not replace failed tool results with model knowledge.",
                "Never claim a tool succeeded unless it returned a result.",
            ],
            debug_mode=True,
        )

        await agent.aprint_response(message, stream=True)


if __name__ == "__main__":
    asyncio.run(
        run_agent(
            "What is 200+2*3-1*10 and who founded Wikipedia?"
        )
    )
