# 参考: https://github.com/astral-sh/uv-docker-example/blob/main/multistage.Dockerfile
# ===构建阶段===
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS builder

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy
ENV UV_PYTHON_DOWNLOADS=0
WORKDIR /app
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --locked --no-install-project --no-dev
COPY . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-dev

# ===运行阶段===
FROM python:3.13-slim-bookworm

# 创建非 root 用户
RUN groupadd --system --gid 1001 nonroot \
 && useradd --system --gid 1001 --uid 1001 --create-home nonroot
COPY --from=builder --chown=nonroot:nonroot /app /app
ENV PATH="/app/.venv/bin:$PATH"
# 切换到非 root 用户
USER nonroot
WORKDIR /app
CMD ["python3", "/app/run.py"]
