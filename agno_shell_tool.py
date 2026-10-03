import os
import shlex
from pathlib import Path

import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agno.tools.shell import ShellTools


API_HOST = os.getenv("SHELL_TOOL_API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("SHELL_TOOL_API_PORT", "8001"))

BASE_DIR = Path(
    os.getenv(
        "SHELL_TOOL_BASE_DIR",
        os.getcwd(),
    )
)

app = FastAPI(
    title="Agno Shell Tool API",
)

shell_tools = ShellTools(
    base_dir=BASE_DIR,
)


class ShellCommandRequest(BaseModel):
    command: str = Field(..., min_length=1)
    tail: int = Field(default=100, ge=1, le=1000)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok"
    }


@app.post("/run-shell-command")
def run_shell_command(
    request: ShellCommandRequest,
) -> dict[str, object]:

    try:
        args = shlex.split(request.command)

        output = shell_tools.run_shell_command(
            args=args,
            tail=request.tail,
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        ) from error

    return {
        "base_dir": str(BASE_DIR),
        "command": request.command,
        "args": args,
        "tail": request.tail,
        "output": output,
    }


def run_api() -> None:
    uvicorn.run(
        "agno_shell_tool:app",
        host=API_HOST,
        port=API_PORT,
        reload=True,
    )


if __name__ == "__main__":
    run_api()