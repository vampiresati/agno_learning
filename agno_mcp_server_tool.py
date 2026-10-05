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

        MCPTools(
            command=f"{python} -m fastmcp_server",
            timeout_seconds=60,
        ) as fastmcp_server,
    ):
        agent = Agent(
            model=Ollama(id="qwen3:4b"),

            tools=[
                calculator,
                wikipedia,
                fastmcp_server,
            ],

            instructions=[
                "You are a helpful AI assistant.",

                "Use the calculator MCP server for normal arithmetic.",
                "Use the Wikipedia MCP server for factual questions.",
                "Use the fastmcp_server calculator for mathematics operations "
                "such as factorial when the user explicitly requests it.",

                "If a tool fails or times out, retry it once.",
                "If the retry fails, clearly report the failure.",

                "Do not replace failed tool results with model knowledge.",
                "Never claim a tool succeeded unless it returned a result.",

                "When the user explicitly names a particular MCP server, "
                "use that server rather than another tool.",
            ],

            debug_mode=True,
        )

        await agent.aprint_response(
            message,
            stream=True,
        )


if __name__ == "__main__":
    asyncio.run(
        run_agent(
            "What is 200+2*3-1*10 "
            "and use fastmcp_server to find factorial of 5?"
        )
    )

