# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT REST API — Multi-stage Dockerfile
# Python 3.12-slim avec PostGIS/C-libs, non-root user et cache optimisé
# ==============================================================================

# Étape 1 : Build & Dépendances
FROM python:3.12-slim AS builder

WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# Étape 2 : Image d'exécution finale allégée
FROM python:3.12-slim AS runner

WORKDIR /app

# Installation des dépendances système d'exécution (libpq, geos, proj, curl pour healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libgeos-c1v5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Création d'un utilisateur applicatif non-privilégié (sécurité renforcée)
RUN groupadd -g 1001 appuser && \
    useradd -u 1001 -g appuser -m -s /bin/bash appuser

# Copie des packages Python installés depuis le builder
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copie du code source
COPY --chown=appuser:appuser . /app

USER appuser

EXPOSE 8000

# Healthcheck de conformité Docker
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4", "--proxy-headers"]
