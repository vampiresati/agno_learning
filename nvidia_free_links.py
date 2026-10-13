
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

AGENT_NAME = "NVIDIA Free Course Email Agent"
MODEL_ID = os.getenv("OLLAMA_MODEL", "qwen3:4b")

CATALOG_URL = (
    "https://www.nvidia.com/en-us/training/find-training/"
    "?Free+Courses=Free"
)

OUTPUT_DIR = "output/nvidia"

# Allow official NVIDIA pages, including learn.nvidia.com.
ALLOWED_DOMAIN = "nvidia.com"

EXCLUDED_PATHS = {
    "/",
    "/en-us",
    "/en-us/training/find-training",
    "/en-us/training/self-paced-courses",
    "/en-us/training",
    "/en-us/about-nvidia",
    "/en-us/contact",
    "/en-us/developer",
    "/en-us/learn",
}


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
    Retain candidate NVIDIA course URLs.

    This function filters obvious navigation pages.
    It does not independently verify course titles,
    current free status, or enrollment availability.
    """

    candidates = []
    seen_urls = set()

    for item in all_links:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()

        if not url:
            continue

        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            continue

        hostname = (parsed.hostname or "").lower()

        # Accept nvidia.com and its official subdomains.
        if not (
            hostname == ALLOWED_DOMAIN
            or hostname.endswith("." + ALLOWED_DOMAIN)
        ):
            continue

        path = parsed.path.rstrip("/").lower()

        if path in EXCLUDED_PATHS:
            continue

        # Exclude obvious navigation routes.
        excluded_fragments = (
            "/search",
            "/shopping-cart",
            "/checkout",
            "/privacy",
            "/terms",
            "/contact-us",
        )

        if any(fragment in path for fragment in excluded_fragments):
            continue

        # Keep query parameters on potential course URLs.
        # NVIDIA course detail pages may need a course_id.
        if url in seen_urls:
            continue

        seen_urls.add(url)

        if not title:
            title = "(Title not available in extracted link)"

        candidates.append({
            "title": title,
            "url": url,
        })

    print("\nCandidate NVIDIA course links:")

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
            "Send the requested report using email_user.",
            "Use the configured recipient.",
            "Use the supplied titles and URLs only.",
            "Do not invent courses or course details.",
            "Do not claim that a course is currently free "
            "unless that status has been verified.",
            "Label extracted links as candidates when unverified.",
            "Highlight AI, deep learning, generative AI, "
            "data science, robotics, and accelerated computing "
            "when relevant to the supplied information.",

            # Exact URL formatting requirements.
            "Write URLs as plain text.",
            "Never format URLs as Markdown links.",
            "Never use the pattern [URL](URL).",
            "Do not put URLs inside square brackets.",
            "Do not wrap URLs in parentheses.",
            "Do not insert backslashes into URLs.",
            "Preserve the official catalog URL exactly.",
            "Include every supplied candidate link.",

            "Do not invent a compliance check.",
            "Report tool failures honestly.",
            "Give a concise final status based on tool results.",
        ],

        markdown=True,
    )


# ============================================================
# 5. BUILD EMAIL REQUEST
# ============================================================

def build_email_request(courses, receiver_email):
    course_lines = []

    for number, course in enumerate(courses, start=1):
        course_lines.append(
            f"{number}. {course['title']}\n"
            f"URL: {course['url']}"
        )

    course_text = (
        "\n\n".join(course_lines)
        if course_lines
        else "No candidate course links were extracted."
    )

    return f"""
Send an NVIDIA free training course report by email.

Recipient: {receiver_email}

Subject:
NVIDIA Free Training Courses Report

IMPORTANT: COPY THIS OFFICIAL CATALOG URL EXACTLY.

{CATALOG_URL}

The URL above must appear as plain text.
Do not convert it into a Markdown hyperlink.
Do not add square brackets, parentheses, or backslashes.
Do not duplicate the URL.

CANDIDATE COURSE LINKS:

{course_text}

EMAIL REQUIREMENTS:

1. Include the official NVIDIA catalog URL exactly as supplied.
2. Include every candidate title and URL above.
3. Write each URL as plain text on its own line.
4. Do not create Markdown links.
5. Do not invent course titles, prices, dates, or descriptions.
6. Explain that extracted links are candidates until verified.
7. Do not claim that all courses are free or open for enrollment
   unless that information has been verified.
8. Use a professional, readable email format.
9. Send the email using the email_user tool.
10. Report tool failures honestly.

The links were extracted from the official NVIDIA training page.
Course status and current enrollment availability may require
verification on the individual course pages.

After attempting to send, return a concise status based on
the actual tool result. Do not fabricate delivery confirmation.
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
        print("NVIDIA FREE COURSE EMAIL AGENT")
        print("=" * 60)

        print("\nStep 1: Fetching NVIDIA training links...")
        print(f"Catalog URL: {CATALOG_URL}")

        all_links = get_all_links(
            url=CATALOG_URL,
            output_dir=OUTPUT_DIR,
        )

        print(f"\nTotal extracted links: {len(all_links)}")

        print("\nStep 2: Filtering candidate course links...")

        courses = filter_course_links(all_links)

        print(f"\nCandidate links: {len(courses)}")

        if not courses:
            print(
                "\nNo candidate course links were found."
            )
            print(
                f"Inspect the extracted files in {OUTPUT_DIR}."
            )
            print(
                "The NVIDIA page may require JavaScript rendering, "
                "or the extraction/filtering logic may need updating."
            )
            sys.exit(1)

        print("\nStep 3: Creating Agno email agent...")

        email_agent = create_email_agent()

        request = build_email_request(
            courses=courses,
            receiver_email=receiver_email,
        )

        print("\nStep 4: Requesting email delivery...")

        response = email_agent.run(request)

        print("\n" + "=" * 60)
        print("AGENT RESPONSE")
        print("=" * 60)

        print(
            getattr(response, "content", None)
            or "(No text response returned.)"
        )

        print(
            "\nThe model response alone does not prove email delivery. "
            "Check the email tool result and recipient inbox."
        )

    except Exception as error:
        print(
            f"\nERROR: {error}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
