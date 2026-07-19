FROM python:3.12-slim

WORKDIR /app

# Install the package (pulls FastAPI, uvicorn, OR-Tools, etc. from pyproject.toml).
COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

# Run as a non-root user.
RUN useradd --create-home --uid 10001 appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "route_engine.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
