
import os
import sys
from urllib.parse import urlparse

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.email import EmailTools

from extract_links import get_all_links


# ============================================================
# 1. CONFIGURATION
# ============================================================

load_dotenv()

AGENT_NAME = "Qualcomm Free Course Email Agent"
MODEL_ID = os.getenv("OLLAMA_MODEL", "qwen3:4b")

CATALOG_URL = (
    "https://academy.qualcomm.com/course-catalog"
    "?ByFormat=eLearning%2B-%2BFREE"
)

BASE_DOMAIN = "academy.qualcomm.com"


# ============================================================
# 2. LOAD EMAIL CONFIGURATION
# ============================================================

def load_email_variables():
    receiver_email = os.getenv("RECEIVER_EMAIL")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv(
        "SENDER_NAME",
        "My AI Email Agent",
    )
    sender_passkey = os.getenv("SENDER_PASSKEY")

    required = {
        "RECEIVER_EMAIL": receiver_email,
        "SENDER_EMAIL": sender_email,
        "SENDER_PASSKEY": sender_passkey,
    }

    missing = [
        name
        for name, value in required.items()
        if not value
    ]

    if missing:
        raise ValueError(
            "Missing .env variables: "
            + ", ".join(missing)
        )

    return (
        receiver_email,
        sender_email,
        sender_name,
        sender_passkey,
    )


# ============================================================
# 3. FILTER CANDIDATE COURSE LINKS
# ============================================================

def filter_course_links(all_links):
    """
    Filter navigation links and retain candidate URLs.

    IMPORTANT:
    This filter does not prove that a URL is a course page.
    Actual course-page verification requires further inspection.
    """

    candidates = []
    seen_urls = set()

    excluded_paths = {
        "",
        "/",
        "/home",
        "/course-catalog",
        "/course-catalog/Corporate-Training",
        "/shopping-cart",
        "/blogs",
        "/about-us",
    }

    for item in all_links:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()

        if not url:
            continue

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            continue

        if parsed.netloc.lower() != BASE_DOMAIN:
            continue

        path = parsed.path.rstrip("/")

        if path.lower() in excluded_paths:
            continue

        # Ignore query-string links because many are
        # catalog filters, sorting options, or tracking URLs.
        # Remove this condition if course URLs require queries.
        if parsed.query:
            continue

        # Ignore empty link labels.
        if not title:
            continue

        # Deduplicate by URL.
        if url in seen_urls:
            continue

        seen_urls.add(url)

        candidates.append({
            "title": title,
            "url": url,
        })

    print("\nCandidate links for inspection:")

    if not candidates:
        print("No candidate links found.")
    else:
        for number, item in enumerate(candidates, start=1):
            print(f"{number}. {item['title']}")
            print(f"   {item['url']}")

    return candidates


# ============================================================
# 4. CREATE AGNO EMAIL AGENT
# ============================================================

def create_email_agent():
    (
        receiver_email,
        sender_email,
        sender_name,
        sender_passkey,
    ) = load_email_variables()

    return Agent(
        name=AGENT_NAME,

        model=Ollama(
            id=MODEL_ID,
        ),

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
            "You are a technical learning assistant.",
            "The user requests an email report.",
            "Use the email_user tool to send the email.",
            "Use a professional subject line.",
            "Write a clear and friendly email.",
            "Include the official Qualcomm Academy catalog URL.",
            "Use only the supplied course titles and URLs.",
            "Do not invent courses, links, prices, or dates.",

            # CRITICAL URL FORMATTING RULES
            "Write every URL as a plain URL.",
            "Never format URLs as Markdown links.",
            "Never put a URL inside square brackets.",
            "Never put a URL inside parentheses.",
            "Never create a Markdown link of the form "
            "[URL](URL).",
            "Do not escape URL characters with backslashes.",
            "Preserve the catalog URL exactly as supplied.",

            "Prioritize AI, Edge AI, robotics, IoT, "
            "embedded systems, and 5G when relevant.",
            "Label unverified entries as candidate links.",
            "Do not claim a course is available or free "
            "unless that status has been verified.",
            "Explain that course availability and enrollment "
            "should be checked on the official course page.",
            "Do not invent publication dates.",
            "Report tool failures honestly.",
            "Do not generate an unsupported compliance claim.",
            "After using the email tool, give a concise status "
            "based on the tool result.",
        ],

        markdown=True,
    )


# ============================================================
# 5. PREPARE THE EMAIL REQUEST
# ============================================================

def build_email_request(courses, receiver_email):
    course_lines = []

    for number, course in enumerate(courses, start=1):
        course_lines.append(
            f"{number}. {course['title']}\n"
            f"   URL: {course['url']}"
        )

    if course_lines:
        course_text = "\n\n".join(course_lines)
    else:
        course_text = "No candidate links were found."

    return f"""
Send a Qualcomm Academy course-link report by email.

Recipient: {receiver_email}

Subject:
Qualcomm Academy Free eLearning Courses Report

IMPORTANT: EXACT URL FORMATTING

The following is the official catalog URL.
Copy it exactly as written. Do not modify it.

{CATALOG_URL}

The catalog URL above MUST appear as a plain URL in the email.

Do not format it like this:
[URL](URL)

Do not add square brackets or parentheses around it.
Do not insert backslashes into it.
Do not duplicate the URL as Markdown link text.

Candidate course links collected by Python:

{course_text}

Email requirements:

1. Use the subject specified above.
2. Include the official catalog URL exactly as supplied.
3. Include every candidate title and URL supplied above.
4. Write each URL as plain text on its own line.
5. Do not convert any URL into a Markdown hyperlink.
6. Briefly explain technical relevance only where apparent.
7. Do not invent course descriptions, prices, or dates.
8. Do not claim that enrollment is currently available
   without verification.
9. State that candidate links may need manual verification.
10. Use the email_user tool to send the email to the
    configured recipient.
11. Report tool failures honestly.

The URLs have been collected and filtered by Python.
They have not necessarily been verified as course pages.

After sending, provide a short status. Do not produce
a fabricated compliance checklist or unsupported success claim.
"""


# ============================================================
# 6. MAIN WORKFLOW
# ============================================================

def main():
    try:
        (
            receiver_email,
            _,
            _,
            _,
        ) = load_email_variables()

        print("=" * 60)
        print("QUALCOMM FREE COURSE EMAIL AGENT")
        print("=" * 60)

        print("\nStep 1: Fetching catalog links...")

        all_links = get_all_links(
            url=CATALOG_URL,
            output_dir="output",
        )

        print(f"\nAll unique links: {len(all_links)}")

        print("\nStep 2: Filtering candidate course links...")

        courses = filter_course_links(all_links)

        print(f"\nCandidate course links: {len(courses)}")

        if not courses:
            print(
                "\nNo candidate course links were found."
            )
            print(
                "Inspect output/qualcomm_all_links.csv "
                "and adjust the filter to match the actual "
                "course detail URLs."
            )
            sys.exit(1)

        print("\nCandidate links:")

        for number, course in enumerate(courses, start=1):
            print(f"{number}. {course['title']}")
            print(f"   {course['url']}")

        print("\nStep 3: Creating the Agno email agent...")

        email_agent = create_email_agent()

        request = build_email_request(
            courses=courses,
            receiver_email=receiver_email,
        )

        print("\nStep 4: Asking Ollama and Agno to send the email...")

        response = email_agent.run(request)

        print("\n" + "=" * 60)
        print("AGENT RESPONSE")
        print("=" * 60)

        print(
            getattr(response, "content", None)
            or "(No text response returned.)"
        )

        print(
            "\nNote: The agent response is not independent "
            "proof of email delivery. Check the email tool "
            "result and the recipient's inbox."
        )

    except Exception as error:
        print(
            f"\nERROR: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
