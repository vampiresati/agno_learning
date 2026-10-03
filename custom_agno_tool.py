from pathlib import Path
from typing import List, Optional, Union

from agno.tools import Toolkit
from agno.utils.log import log_debug, log_info, log_warning


class TimeTools(Toolkit):
    def __init__(
        self,
        base_dir: Optional[Union[Path, str]] = None,
        enable_run_shell_command: bool = True,
        all: bool = False,
        **kwargs,
    ):
        """Initialize TimeTools.
        """
        self.base_dir: Optional[Path] = None
        if base_dir is not None:
            self.base_dir = Path(base_dir) if isinstance(base_dir, str) else base_dir

        tools = []
        if all or enable_run_shell_command:
            tools.append(self.get_current_time)

        super().__init__(name="time_tools", tools=tools, **kwargs)

    def get_current_time(self) -> str:
        """
        Returns today's date
        """
        from datetime import datetime
        today=datetime.now().strftime("Today is %B %d, %Y")
        return today


