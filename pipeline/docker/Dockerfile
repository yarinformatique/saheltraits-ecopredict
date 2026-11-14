# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : DOCKERFILE REPRODUCTIBLE (Couche 4a)
# Image conteneurisée : R 4.4+ & Python 3.12+ avec pile géospatiale complète
# Auteur : YAGO Abdoul Rachide (UJKZ - ICC)
# ==============================================================================

FROM rocker/geospatial:4.4.1

LABEL maintainer="YAGO Abdoul Rachide <rachide.yago@ujkz.bf>"
LABEL project="SahelTraits-DB & EcoPredict - Couche 4a"
LABEL description="Pipeline 100% reproductible JSDM/CMIP6, IndVal, RLQ et biomod2"
LABEL version="1.0.0"

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# 1. Dépendances système géospatiales & Python 3.12+
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-dev \
    python3-venv \
    python3-poetry \
    libgdal-dev \
    gdal-bin \
    libgeos-dev \
    libproj-dev \
    libudunits2-dev \
    libnetcdf-dev \
    curl \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# 2. Répertoire de travail
WORKDIR /workspace/pipeline

# 3. Installation des dépendances Python via Poetry & Pip
COPY pyproject.toml requirements.txt ./
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# 4. Installation des paquets R indispensables pour la Couche 4a
RUN R -e "install.packages(c( \
    'renv', 'ade4', 'ape', 'lme4', 'glmmTMB', 'DHARMa', \
    'FactoMineR', 'factoextra', 'ggplot2', 'dplyr', 'tidyr', \
    'future', 'parallel', 'purrr', 'tibble' \
), repos='https://cloud.r-project.org/')"

# Paquets écologiques et spatiaux spécialisés
RUN R -e "install.packages(c( \
    'terra', 'sf', 'raster', 'indicspecies', 'drc', \
    'biomod2', 'mFD', 'CoordinateCleaner' \
), repos='https://cloud.r-project.org/')"

# 5. Copie du code source du pipeline
COPY . .

# 6. Point d'entrée
RUN chmod +x run_pipeline.py
ENTRYPOINT ["python3", "run_pipeline.py"]
CMD ["--all"]
