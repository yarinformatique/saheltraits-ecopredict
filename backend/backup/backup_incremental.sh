#!/usr/bin/env bash
# ==============================================================================
# SAHELTRAITS-DB — SCRIPT DE SAUVEGARDE INCERMENTALE QUOTIDIENNE (VPS LINUX)
# Composant : Entrepôt de données centralisé (Couche 3)
# Projet : Thèse de Doctorat — YAGO Abdoul Rachide (UJKZ-ICC)
# ==============================================================================

set -euo pipefail

# Configuration des répertoires et variables
BACKUP_DIR="${BACKUP_DIR:-/var/backups/saheltraits}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
DATE_TAG=$(date +"%Y%m%d_%H%M%S")
DATE_DAY=$(date +"%Y%m%d")

DB_CONTAINER="${DB_CONTAINER:-saheltraits_postgis}"
DB_USER="${POSTGRES_USER:-saheltraits_user}"
DB_NAME="${POSTGRES_DB:-saheltraits_db}"
LOG_FILE="${BACKUP_DIR}/backup_${DATE_DAY}.log"

mkdir -p "${BACKUP_DIR}/daily"
mkdir -p "${BACKUP_DIR}/wal_archives"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Démarrage de la sauvegarde SAHELTRAITS-DB..." | tee -a "${LOG_FILE}"

# 1. Export SQL compressé de sécurité (Full dump quotidien)
DUMP_FILE="${BACKUP_DIR}/daily/saheltraits_${DB_NAME}_${DATE_TAG}.sql.gz"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Génération du dump PostgreSQL avec pg_dump..." | tee -a "${LOG_FILE}"

docker exec -t "${DB_CONTAINER}" pg_dump -U "${DB_USER}" -d "${DB_NAME}" --clean --if-exists --no-owner --no-privileges | gzip > "${DUMP_FILE}"

# Vérification de l'intégrité du fichier généré
if [ -s "${DUMP_FILE}" ]; then
    DUMP_SIZE=$(du -h "${DUMP_FILE}" | cut -f1)
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Dump réussi : ${DUMP_FILE} (${DUMP_SIZE})" | tee -a "${LOG_FILE}"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] ERREUR : Le fichier de dump est vide ou manquant !" | tee -a "${LOG_FILE}"
    exit 1
fi

# 2. Sauvegarde des métadonnées et checksum SHA256 pour conformité FAIR
sha256sum "${DUMP_FILE}" > "${DUMP_FILE}.sha256"

# 3. Synchronisation incrémentale des WALs (Write-Ahead Logging pour Point-In-Time Recovery)
if docker exec -t "${DB_CONTAINER}" test -d "/var/lib/postgresql/data/pg_wal"; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Synchronisation incrémentale des archives WAL..." | tee -a "${LOG_FILE}"
    docker exec -t "${DB_CONTAINER}" rsync -av --ignore-existing /var/lib/postgresql/data/pg_wal/ /wal_backup/ 2>/dev/null || true
fi

# 4. Purge des sauvegardes antérieures à la durée de rétention ($RETENTION_DAYS)
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Nettoyage des sauvegardes datant de plus de ${RETENTION_DAYS} jours..." | tee -a "${LOG_FILE}"
find "${BACKUP_DIR}/daily" -type f -name "saheltraits_*.sql.gz*" -mtime +${RETENTION_DAYS} -exec rm -f {} \;

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Sauvegarde quotidienne terminée avec succès." | tee -a "${LOG_FILE}"
