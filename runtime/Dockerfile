# The server runtime, built once and copied into every task image as /opt/arena.
# It carries its own Python (uv-managed, relocatable) so the task image's own
# Python and packages stay untouched.
#   docker build -t arena-runtime:local runtime/
FROM debian:bookworm-slim

ENV UV_PYTHON_INSTALL_DIR=/opt/arena/python \
    UV_LINK_MODE=copy \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.9.7 /uv /opt/arena/bin/uv
ENV PATH="/opt/arena/bin:$PATH"

RUN uv python install 3.12 \
    && uv venv /opt/arena/venv --python 3.12

COPY runtime/requirements.txt /tmp/requirements.txt
COPY runtime/vendor /tmp/vendor
RUN uv pip install --python /opt/arena/venv/bin/python -r /tmp/requirements.txt \
    && uv pip install --python /opt/arena/venv/bin/python --no-deps /tmp/vendor/openenv-*.whl \
    && rm -rf /tmp/requirements.txt /tmp/vendor

COPY arena_env /opt/arena/venv/lib/python3.12/site-packages/arena_env
COPY openenv.yaml /opt/arena/pkg/openenv.yaml
COPY tools/prepare_image.py /opt/arena/pkg/prepare_image.py
