"""Action, observation and state models: the tbench2_env schema, unchanged."""

from pydantic import Field

from openenv.core.env_server.types import Action, Observation, State


class Tbench2Action(Action):
    action_type: str = Field(default="exec")
    command: str = Field(default="")
    session_id: str | None = Field(default=None)
    block: bool = Field(default=True)
    wait_seconds: float | None = Field(default=None)
    file_path: str = Field(default="")
    content: str = Field(default="")


class Tbench2Observation(Observation):
    instruction: str = Field(default="")
    output: str = Field(default="")
    success: bool = Field(default=True)
    error: str = Field(default="")
    task_id: str = Field(default="")
    task_path: str = Field(default="")
    session_id: str | None = Field(default=None)
    action_type: str = Field(default="")
    info: dict = Field(default_factory=dict)


class Tbench2State(State):
    task_id: str = Field(default="")
    task_path: str = Field(default="")
    session_id: str = Field(default="")
    terminal_ready: bool = Field(default=False)
    last_action_type: str = Field(default="")
    last_command: str = Field(default="")
    last_output: str = Field(default="")
