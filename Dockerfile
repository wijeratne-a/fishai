FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY renv ./renv
COPY data/SOURCES.yaml ./data/SOURCES.yaml

RUN pip install --no-cache-dir -e ".[dev]"

# Optional: bootstrap R deps when building with network
# RUN Rscript renv/scripts/bootstrap.R

CMD ["pytest"]
