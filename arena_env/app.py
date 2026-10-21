"""HTTP and WebSocket server (OpenEnv). Run: python -m arena_env.app"""

from openenv.core.env_server.http_server import create_app

from .environment import ArenaEnvironment, bundle
from .models import Tbench2Action, Tbench2Observation

# Load the task (and move the verifier into memory) before serving.
bundle()

app = create_app(
    ArenaEnvironment,
    Tbench2Action,
    Tbench2Observation,
    env_name="arena_env",
    max_concurrent_envs=4,
)


def main(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
