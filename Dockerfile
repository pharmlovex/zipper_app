FROM python:3.12-slim

RUN groupadd -r zipper && useradd -r -g zipper zipper

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

RUN chown -R zipper:zipper /app

WORKDIR /app
RUN uv venv --python python3.12 && \
    uv pip install . && \
    chown -R zipper:zipper .venv

ENV PATH="/app/.venv/bin:$PATH"

USER zipper

CMD ["zipper", "--help"]