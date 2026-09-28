FROM python:3.12-slim-bookworm

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    gnupg \
    curl \
    && install -m 0755 -d /etc/apt/keyrings \
    && curl -fsSL https://cloud.r-project.org/bin/linux/debian/marutter_pubkey.asc \
      | gpg --dearmor -o /etc/apt/keyrings/cran.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/cran.gpg] https://cloud.r-project.org/bin/linux/debian bookworm-cran40/" \
      > /etc/apt/sources.list.d/cran-r.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    r-base \
    r-base-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    libxml2-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libuv1-dev \
    libudunits2-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
COPY python ./python
COPY configs ./configs
COPY renv ./renv
COPY renv.lock ./renv.lock
COPY data/SOURCES.yaml ./data/SOURCES.yaml

RUN pip install --no-cache-dir -e ".[dev]"

RUN Rscript renv/scripts/bootstrap.R

ENV RENV_PATHS_LIBRARY=/app/renv/library

CMD ["bash", "-lc", "pytest && Rscript -e \"testthat::test_dir('src/models/tests/testthat')\""]
