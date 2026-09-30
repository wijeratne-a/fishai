FROM rocker/r-ver:4.5.2

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-venv \
    cmake \
    pkg-config \
    libabsl-dev \
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
COPY docs ./docs
COPY prereg ./prereg
COPY Dockerfile ./Dockerfile
COPY tests ./tests
COPY scripts ./scripts
COPY security ./security
COPY renv ./renv
COPY renv.lock ./renv.lock
COPY .Rprofile ./.Rprofile
COPY data/SOURCES.yaml ./data/SOURCES.yaml
COPY scripts/ci/run_r_model_tests.R ./scripts/ci/run_r_model_tests.R

RUN pip3 install --no-cache-dir --break-system-packages -e ".[dev]"

RUN Rscript -e 'install.packages("renv", repos = "https://cloud.r-project.org"); source("renv/activate.R"); renv::restore(prompt = FALSE)'

ENV RENV_PATHS_LIBRARY=/app/renv/library
ENV FISHAI_ROOT=/app

CMD ["bash", "-lc", "python3 -m pytest tests/models && Rscript scripts/ci/run_r_model_tests.R"]
