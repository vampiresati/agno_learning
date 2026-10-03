import json
import os
import re
from pathlib import Path
from typing import Any

import arxiv
import requests
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pypdf import PdfReader
from agno.tools.arxiv import ArxivTools
from agno.tools.email import EmailTools
from agno_email_agent import load_email_variables

API_HOST = os.getenv("ARXIV_EMAIL_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("ARXIV_EMAIL_API_PORT", "8000"))
DEFAULT_ARTICLE_COUNT = int(os.getenv("ARXIV_EMAIL_ARTICLE_COUNT", "5"))
DEFAULT_MAX_PAPER_CHARS = int(os.getenv("ARXIV_EMAIL_MAX_PAPER_CHARS", "20000"))
PDF_DOWNLOAD_DIR = Path(os.getenv("ARXIV_EMAIL_PDF_DIR", "/tmp/agno_arxiv_pdfs"))

app = FastAPI(title="ArXiv Email API")


class ArxivEmailRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    num_articles: int = Field(default=DEFAULT_ARTICLE_COUNT, ge=1, le=20)
    receiver_email: str | None = None


class PaperMarkdownEmailRequest(BaseModel):
    paper_ids: list[str] = Field(..., min_length=1)
    pages_to_read: int | None = Field(default=3, ge=1, le=50)
    max_chars: int = Field(default=DEFAULT_MAX_PAPER_CHARS, ge=1000, le=100000)
    receiver_email: str | None = None


def search_arxiv(topic: str, num_articles: int) -> list[dict[str, Any]]:
    arxiv_tools = ArxivTools(enable_read_arxiv_papers=False)
    result = arxiv_tools.search_arxiv_and_return_articles(
        query=topic,
        num_articles=num_articles,
    )
    return json.loads(result)


def read_arxiv_papers(paper_ids: list[str], pages_to_read: int | None) -> list[dict[str, Any]]:
    client = arxiv.Client()
    search = arxiv.Search(id_list=paper_ids)
    papers = []
    PDF_DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

    for result in client.results(search=search):
        paper = {
            "title": result.title,
            "id": result.get_short_id(),
            "entry_id": result.entry_id,
            "authors": [author.name for author in result.authors],
            "primary_category": result.primary_category,
            "categories": result.categories,
            "published": result.published.isoformat() if result.published else None,
            "pdf_url": result.pdf_url,
            "links": [link.href for link in result.links],
            "summary": result.summary,
            "comment": result.comment,
            "content": [],
        }

        if result.pdf_url:
            pdf_path = download_pdf(result.pdf_url, result.get_short_id())
            pdf_reader = PdfReader(pdf_path)
            for page_number, page in enumerate(pdf_reader.pages, start=1):
                if pages_to_read and page_number > pages_to_read:
                    break
                paper["content"].append(
                    {
                        "page": page_number,
                        "text": page.extract_text() or "",
                    }
                )

        papers.append(paper)

    return papers


def download_pdf(pdf_url: str, paper_id: str) -> Path:
    safe_paper_id = re.sub(r"[^a-zA-Z0-9_.-]", "_", paper_id)
    pdf_path = PDF_DOWNLOAD_DIR / f"{safe_paper_id}.pdf"
    response = requests.get(pdf_url, timeout=60)
    response.raise_for_status()
    pdf_path.write_bytes(response.content)
    return pdf_path


def normalize_arxiv_id(paper_id: str) -> str:
    return re.sub(r"v\d+$", "", paper_id.strip())


def read_arxiv_papers_with_fallback(paper_ids: list[str], pages_to_read: int | None) -> list[dict[str, Any]]:
    papers = read_arxiv_papers(paper_ids=paper_ids, pages_to_read=pages_to_read)
    if papers:
        return papers

    normalized_paper_ids = [normalize_arxiv_id(paper_id) for paper_id in paper_ids]
    if normalized_paper_ids == paper_ids:
        return papers

    return read_arxiv_papers(paper_ids=normalized_paper_ids, pages_to_read=pages_to_read)


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


def build_paper_markdown_email(
    paper_ids: list[str],
    papers: list[dict[str, Any]],
    max_chars: int,
) -> tuple[str, str]:
    subject = f"ArXiv paper markdown: {', '.join(paper_ids)}"
    if not papers:
        return subject, f"No arXiv papers were found for IDs: {', '.join(paper_ids)}"

    sections = [f"# ArXiv Paper Markdown\n\nRequested IDs: {', '.join(paper_ids)}"]
    for paper in papers:
        authors = ", ".join(paper.get("authors", [])) or "Unknown authors"
        sections.extend(
            [
                f"## {paper.get('title', 'Untitled')}",
                f"- **ID:** {paper.get('id') or 'Unknown'}",
                f"- **Authors:** {authors}",
                f"- **Published:** {paper.get('published') or 'Unknown'}",
                f"- **PDF:** {paper.get('pdf_url') or 'No PDF URL'}",
                "",
                "### Abstract",
                paper.get("summary") or "No abstract available.",
                "",
            ]
        )

        pages = paper.get("content", [])
        if pages:
            sections.append("### Extracted Paper Text")
            for page in pages:
                page_number = page.get("page", "Unknown")
                page_text = " ".join((page.get("text") or "").split())
                sections.extend(
                    [
                        "",
                        f"#### Page {page_number}",
                        page_text or "No text extracted from this page.",
                    ]
                )

    body = "\n".join(sections).strip()
    if len(body) > max_chars:
        body = f"{body[:max_chars]}\n\n[Truncated to {max_chars} characters.]"
    return subject, body


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


def read_paper_markdown_and_send(
    paper_ids: list[str],
    pages_to_read: int | None,
    max_chars: int,
    receiver_email: str | None = None,
) -> dict[str, Any]:
    cleaned_paper_ids = [paper_id.strip() for paper_id in paper_ids if paper_id.strip()]
    papers = read_arxiv_papers_with_fallback(paper_ids=cleaned_paper_ids, pages_to_read=pages_to_read)
    subject, body = build_paper_markdown_email(
        paper_ids=cleaned_paper_ids,
        papers=papers,
        max_chars=max_chars,
    )
    email_status = send_email(subject=subject, body=body, receiver_email=receiver_email)
    return {
        "paper_ids": cleaned_paper_ids,
        "num_papers": len(papers),
        "pages_to_read": pages_to_read,
        "email_status": email_status,
        "subject": subject,
        "papers": [
            {
                "title": paper.get("title"),
                "id": paper.get("id"),
                "pdf_url": paper.get("pdf_url"),
                "published": paper.get("published"),
                "pages_extracted": len(paper.get("content", [])),
            }
            for paper in papers
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


@app.post("/send-arxiv-paper-email")
def send_arxiv_paper_email(request: PaperMarkdownEmailRequest) -> dict[str, Any]:
    paper_ids = [paper_id.strip() for paper_id in request.paper_ids if paper_id.strip()]
    if not paper_ids:
        raise HTTPException(status_code=400, detail="paper_ids must include at least one paper ID")

    try:
        result = read_paper_markdown_and_send(
            paper_ids=paper_ids,
            pages_to_read=request.pages_to_read,
            max_chars=request.max_chars,
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
