from agno.agent import Agent
from agno.tools.arxiv import ArxivTools
from agno.models.ollama import Ollama

agent_arxiv_full = Agent(
    model=Ollama(id="qwen3:4b",),
    tools=[ArxivTools()],  # All functions enabled by default
    description="You are a research assistant with full ArXiv search capabilities.",
    instructions=[
        "Help users find and analyze academic papers from ArXiv",
        "Provide detailed paper summaries and insights",
        "Support comprehensive literature reviews",
    ],
    markdown=True,
)

if __name__ == "__main__":
    print("=== ArXiv Paper Search Example ===")
    agent_arxiv_full.print_response("Search arxiv for latest 'rag'", markdown=True)
