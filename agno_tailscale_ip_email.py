import os
import socket
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from agno.tools.email import EmailTools


TAILSCALE_CGNAT_PREFIX = "100."
DEFAULT_SENDER_NAME = "Tailscale IP Notifier"


def run_command(command: list[str]) -> str:
    process = subprocess.run(
        command,
        capture_output=True,
        check=False,
        text=True,
    )
    if process.returncode != 0:
        return ""
    return process.stdout.strip()


def get_tailscale_ip() -> str:
    tailscale_ip = run_command(["tailscale", "ip", "-4"])
    if tailscale_ip:
        return tailscale_ip.splitlines()[0].strip()

    hostname_ips = run_command(["hostname", "-I"])
    for ip_address in hostname_ips.split():
        if ip_address.startswith(TAILSCALE_CGNAT_PREFIX):
            return ip_address

    return ""


def send_tailscale_ip_email() -> str:
    load_dotenv()
    receiver_email = os.getenv("RECEIVER_EMAIL")
    sender_email = os.getenv("SENDER_EMAIL")
    sender_name = os.getenv("SENDER_NAME", DEFAULT_SENDER_NAME)
    sender_passkey = os.getenv("SENDER_PASSKEY")
    tailscale_ip = get_tailscale_ip()
    hostname = socket.gethostname()
    timestamp = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%Y-%m-%d %H:%M:%S %Z")

    if tailscale_ip:
        subject = f"Tailscale IP for {hostname}: {tailscale_ip}"
        body = "\n".join(
            [
                f"Computer: {hostname}",
                f"Tailscale IP: {tailscale_ip}",
                f"Agno Shell docs: http://{tailscale_ip}:8001/docs",
                f"Health check: http://{tailscale_ip}:8001/health",
                f"Time: {timestamp}",
            ]
        )
    else:
        subject = f"Tailscale IP not found for {hostname}"
        body = "\n".join(
            [
                f"Computer: {hostname}",
                "Tailscale IP was not available when this startup check ran.",
                "Make sure the Tailscale service is running and connected.",
                f"Time: {timestamp}",
            ]
        )

    email_tools = EmailTools(
        receiver_email=receiver_email,
        sender_email=sender_email,
        sender_name=sender_name,
        sender_passkey=sender_passkey,
        enable_email_user=True,
    )
    return email_tools.email_user(subject=subject, body=body)


if __name__ == "__main__":
    print(send_tailscale_ip_email())
