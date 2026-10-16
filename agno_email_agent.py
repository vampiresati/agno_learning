import os
from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.email import EmailTools
# Phoenix imports
from phoenix.otel import register
load_dotenv()
os.environ["PHOENIX_COLLECTOR_ENDPOINT"] = (
    "http://localhost:6006"
)
tracer_provider = register(
    project_name="agno-email-agent",
    auto_instrument=True,
)
print("Phoenix tracing initialized")
print("Phoenix UI: http://localhost:6006")
email_agent_name = "My AI Email Agent"
def load_email_variables():
    receiver_email = os.getenv("RECEIVER_EMAIL")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME", email_agent_name)
    sender_passkey = os.getenv("SENDER_PASSKEY")
    return receiver_email,sender_email,sender_name,sender_passkey
receiver_email,sender_email,sender_name,sender_passkey=load_email_variables()
email_agent = Agent(
    name=email_agent_name,
    model=Ollama(id="qwen3:4b",),
    tools=[
        EmailTools(
            receiver_email=receiver_email,
            sender_email=sender_email,
            sender_name=sender_name,
            sender_passkey=sender_passkey,
            enable_email_user=True,
        )
    ],

    instructions=[
        "You are an email assistant.",
        "Use the email tool when the user explicitly asks to send an email.",
        "Create a clear and professional subject.",
        "Create a clear and friendly email body.",
        "Do not send an email unless the user explicitly asks you to send one.",
    ],
    markdown=True,
    debug_mode=True,
)

if __name__ == "__main__":

    email_agent.print_response(
        """
        Send an email to the receiver.
        Subject:Test Email from Qwen
        Message:
        Hello!
        This is a test email sent by my AI agent
        using Agno, Ollama, and Qwen.
        Have a great day!
        """,
        markdown=True,
    )
