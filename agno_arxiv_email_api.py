import json
import os
from typing import Any

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from agno.tools.arxiv import ArxivTools
from agno.tools.email import EmailTools
from agno_email_agent import load_email_variables

API_HOST = os.getenv("ARXIV_EMAIL_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("ARXIV_EMAIL_API_PORT", "8000"))
DEFAULT_ARTICLE_COUNT = int(os.getenv("ARXIV_EMAIL_ARTICLE_COUNT", "5"))

app = FastAPI(title="ArXiv Email API")


class ArxivEmailRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    num_articles: int = Field(default=DEFAULT_ARTICLE_COUNT, ge=1, le=20)
    receiver_email: str | None = None


def search_arxiv(topic: str, num_articles: int) -> list[dict[str, Any]]:
    arxiv_tools = ArxivTools(enable_read_arxiv_papers=False)
    result = arxiv_tools.search_arxiv_and_return_articles(
        query=topic,
        num_articles=num_articles,
    )
    return json.loads(result)


def build_email(topic: str, articles: list[dict[str, Any]]) -> tuple[str, str]:
    subject = f"ArXiv papers for: {topic}"
    if not articles:
        return subject, f"No arXiv papers were found for '{topic}'."

    lines = [
        f"Here are the top {len(articles)} arXiv papers found for '{topic}':",
        "",
    ]
    for index, article in enumerate(articles, start=1):
        authors = ", ".join(article.get("authors", [])) or "Unknown authors"
        summary = " ".join((article.get("summary") or "").split())
        if len(summary) > 900:
            summary = f"{summary[:897]}..."

        lines.extend(
            [
                f"{index}. {article.get('title', 'Untitled')}",
                f"Authors: {authors}",
                f"Published: {article.get('published') or 'Unknown'}",
                f"PDF: {article.get('pdf_url') or 'No PDF URL'}",
                f"Summary: {summary or 'No summary available.'}",
                "",
            ]
        )

    return subject, "\n".join(lines).strip()


def send_email(subject: str, body: str, receiver_email: str | None = None) -> str:
    default_receiver_email, sender_email, sender_name, sender_passkey = load_email_variables()
    email_tools = EmailTools(
        receiver_email=receiver_email or default_receiver_email,
        sender_email=sender_email,
        sender_name=sender_name,
        sender_passkey=sender_passkey,
        enable_email_user=True,
    )
    return email_tools.email_user(subject=subject, body=body)


def search_and_send(topic: str, num_articles: int, receiver_email: str | None = None) -> dict[str, Any]:
    articles = search_arxiv(topic=topic, num_articles=num_articles)
    subject, body = build_email(topic=topic, articles=articles)
    email_status = send_email(subject=subject, body=body, receiver_email=receiver_email)
    return {
        "topic": topic,
        "num_articles": len(articles),
        "email_status": email_status,
        "subject": subject,
        "articles": [
            {
                "title": article.get("title"),
                "id": article.get("id"),
                "pdf_url": article.get("pdf_url"),
                "published": article.get("published"),
            }
            for article in articles
        ],
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/send-arxiv-email")
def send_arxiv_email(request: ArxivEmailRequest) -> dict[str, Any]:
    try:
        result = search_and_send(
            topic=request.topic.strip(),
            num_articles=request.num_articles,
            receiver_email=request.receiver_email.strip() if request.receiver_email else None,
        )
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error

    if result["email_status"] != "email sent successfully":
        raise HTTPException(status_code=502, detail=result)
    return result


def run_api() -> None:
    uvicorn.run("agno_arxiv_email_api:app", host=API_HOST, port=API_PORT, reload=True)


if __name__ == "__main__":
    run_api()
