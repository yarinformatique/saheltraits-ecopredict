# ==============================================================================
# SAHELTRAITS-DB & ECOPREDICT : MAKEFILE SCIENTIFIQUE (Couche 4a)
# ==============================================================================

.PHONY: all run module1 module2 module3 module4 test docker-build docker-run clean help

PYTHON = python
RSCRIPT = Rscript

all: run

run:
	$(PYTHON) run_pipeline.py --all

module1:
	$(PYTHON) run_pipeline.py --module 1

module2:
	$(PYTHON) run_pipeline.py --module 2

module3:
	$(PYTHON) run_pipeline.py --module 3

module4:
	$(PYTHON) run_pipeline.py --module 4

test:
	$(PYTHON) -m unittest discover -s tests -p "test_*.py"

docker-build:
	docker build -t saheltraits-pipeline:latest -f docker/Dockerfile .

docker-run:
	docker compose -f docker/docker-compose.yml up

clean:
	rm -rf __pycache__ src/**/__pycache__ tests/__pycache__ .pytest_cache

help:
	@echo "Usage make [cible]"
	@echo "  make run          : Exécute l'intégralité du pipeline (Modules 1 à 4)"
	@echo "  make module1      : Exécute le Module 1 (Web-Mining & Climat)"
	@echo "  make module2      : Exécute le Module 2 (IndVal & Plasticité)"
	@echo "  make module3      : Exécute le Module 3 (Syndromes & RLQ)"
	@echo "  make module4      : Exécute le Module 4 (JSDM & CMIP6)"
	@echo "  make test         : Exécute la suite de tests automatisés"
	@echo "  make docker-build : Construit l'image Docker reproductible"
	@echo "  make docker-run   : Démarre le conteneur Docker"
