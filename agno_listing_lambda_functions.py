from agno.agent import Agent
from agno.models.ollama import Ollama

from agno.tools.aws_lambda import AWSLambdaTools



agent = Agent(
    name="lambda Agent",
    role="Get aws lambda informations",
    model=Ollama(id="qwen3:4b"),
    tools=[
        AWSLambdaTools(region_name="us-west-1")
    ],
    instructions=[
        "List aws lambda functions names"
    ],
    markdown=True,
)


if __name__ == "__main__":
    agent.print_response(
        "List Aws lambda functions names",
        stream=True,
    )
