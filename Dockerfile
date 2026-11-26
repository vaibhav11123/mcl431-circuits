FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends librsvg2-bin \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir ".[mcp]" \
    && useradd -r -u 10001 app && chown -R app /app
USER 10001
EXPOSE 8080
CMD ["python","-m","circuit.mcp_server","--http","--port","8080"]
