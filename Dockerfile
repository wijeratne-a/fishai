ARG R_BASE_IMAGE
FROM ${R_BASE_IMAGE}

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

COPY data/reference/shoreline/ne_10m_land_pilot_clip.json ./data/reference/shoreline/ne_10m_land_pilot_clip.json

ENV RENV_PATHS_LIBRARY=/app/renv/library
ENV FISHAI_ROOT=/app

CMD ["bash", "-lc", "python3 -m pytest tests/models && Rscript scripts/ci/run_r_model_tests.R"]
