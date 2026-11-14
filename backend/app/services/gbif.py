import logging
from typing import Any, Dict, Optional
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class GBIFService:
    """Service d'interrogation et de synchronisation taxonomique avec l'API GBIF Backbone Taxonomy."""

    @staticmethod
    async def match_species(scientific_name: str) -> Dict[str, Any]:
        """Interroge l'endpoint species/match de GBIF pour valider la nomenclature botanique.

        Retourne un dictionnaire standardisé contenant les clés GBIF et le nom
        accepté.
        """
        params = {"name": scientific_name, "verbose": "false", "strict": "false"}
        try:
            async with httpx.AsyncClient(
                timeout=settings.GBIF_API_TIMEOUT_SECONDS
            ) as client:
                response = await client.get(
                    settings.GBIF_BACKBONE_API_URL, params=params
                )
                if response.status_code == 200:
                    data = response.json()
                    match_type = data.get("matchType", "NONE")
                    if match_type != "NONE":
                        return {
                            "matched": True,
                            "usage_key": data.get("usageKey"),
                            "scientific_name": data.get("scientificName"),
                            "accepted_usage_key": data.get(
                                "acceptedUsageKey", data.get("usageKey")
                            ),
                            "accepted_name_gbif": data.get(
                                "species",
                                data.get(
                                    "acceptedScientificName",
                                    data.get("scientificName"),
                                ),
                            ),
                            "family": data.get("family"),
                            "genus": data.get("genus"),
                            "status": data.get("status", "ACCEPTED"),
                            "confidence": float(data.get("confidence", 0)),
                            "match_type": match_type,
                        }
        except Exception as e:
            logger.warning(
                f"Échec de synchronisation GBIF pour '{scientific_name}': {e}"
            )

        # Fallback hors-ligne ou si GBIF ne trouve pas de correspondance
        parts = scientific_name.split()
        fallback_genus = parts[0] if parts else ""
        return {
            "matched": False,
            "usage_key": None,
            "scientific_name": scientific_name,
            "accepted_usage_key": None,
            "accepted_name_gbif": scientific_name,
            "family": None,
            "genus": fallback_genus,
            "status": "UNMATCHED",
            "confidence": 0.0,
            "match_type": "NONE",
        }
