FROM python:3.12.3-slim

# Set the working directory inside the container
WORKDIR /app

# Set custom Poetry cache and virtual environment paths
ENV POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_CACHE_DIR=/opt/poetry-cache \
    POETRY_VIRTUALENVS_PATH=/opt/venv \
    PATH="/opt/venv/bin:$PATH"

# Install essential system dependencies
RUN apt-get update && apt-get install -y \
    gcc libpq-dev curl && \
    rm -rf /var/lib/apt/lists/*

# Copy Poetry configuration and dependencies files
COPY ./pyproject.toml ./

# Install Poetry
RUN pip install --no-cache-dir poetry

# Install dependencies without creating a virtual environment inside the container
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Create a simple entrypoint script
RUN echo '#!/bin/bash\nexec "$@"' > /usr/local/bin/entrypoint.sh && \
    chmod +x /usr/local/bin/entrypoint.sh

# Set the entrypoint script
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Set default command to python
CMD ["python"]