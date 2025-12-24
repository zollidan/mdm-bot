FROM python:3.13-slim-trixie

# Устанавливаем менеджер uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ADD . /app

RUN uv sync --locked

# Default command (can be overridden in docker-compose)
CMD [ "uv", "run", "python", "-m", "mdm_bot.bot"]
