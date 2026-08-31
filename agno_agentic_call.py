from agno.agent import Agent
from agno.team import Team
from agno.models.ollama import Ollama

from agno.tools.hackernews import HackerNewsTools
from agno.tools.yfinance import YFinanceTools


# ============================================================
# News Agent
# ============================================================

news_agent = Agent(
    name="News Agent",
    role="Get trending technology and AI news from Hacker News.",
    model=Ollama(id="qwen3:4b"),
    tools=[
        HackerNewsTools()
    ],
    instructions=[
        "Search Hacker News for trending technology and AI stories.",
        "Return the most relevant stories.",
        "Include the title and a short summary.",
        "Do not make up news.",
        "Use Hacker News tools for current news.",
    ],
    markdown=True,
)


# ============================================================
# Finance Agent
# ============================================================

finance_agent = Agent(
    name="Finance Agent",
    role="Get stock prices and financial information.",
    model=Ollama(id="qwen3:4b"),
    tools=[
        YFinanceTools()
    ],
    instructions=[
        "Use Yahoo Finance tools for stock-related questions.",
        "Provide current stock price and relevant financial information.",
        "Clearly identify the stock ticker.",
        "Do not invent financial data.",
    ],
    markdown=True,
)


# ============================================================
# Research Team
# ============================================================

research_team = Team(
    name="Research Team",

    model=Ollama(id="qwen3:4b"),

    members=[
        news_agent,
        finance_agent,
    ],

    instructions=[
        "You are the leader of a research team.",
        "Delegate technology and AI news questions to the News Agent.",
        "Delegate stock and financial questions to the Finance Agent.",
        "If a question requires both agents, delegate to both.",
        "Combine the results into one clear final answer.",
        "Do not make up information.",
    ],

    markdown=True,

    show_members_responses=True,
)


# ============================================================
# Run
# ============================================================

if __name__ == "__main__":
    research_team.print_response(
        "What are the trending AI stories and how is NVDA stock doing?",
        stream=True,
    )
