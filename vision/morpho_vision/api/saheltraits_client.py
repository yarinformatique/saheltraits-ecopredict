"""
HTTP client for synchronization with SahelTraits-DB REST API.
Connects Morpho-Analyzer vision results directly to PostgreSQL/PostGIS database.
"""

from typing import Any, Dict, List, Optional
import httpx

from morpho_vision.traceability.exporter import DataExporter


class SahelTraitsClient:
    """Asynchronous and synchronous client for SahelTraits-DB."""

    def __init__(self, base_url: str = "http://localhost:8000/api/v1", timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def get_individual_by_qr(
        self,
        qr_code: str,
        token: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Looks up an individual tree by qr_code_tag."""
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{self.base_url}/individuals/qr/{qr_code}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    return resp.json()
                return None
            except Exception:
                return None

    async def push_measurements(
        self,
        payloads: List[Dict[str, Any]],
        token: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Sends multiple TraitMeasurement records to SahelTraits-DB."""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        url = f"{self.base_url}/traits/measurements"
        created = []
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            for payload in payloads:
                try:
                    resp = await client.post(url, json=payload, headers=headers)
                    if resp.status_code in [200, 201]:
                        created.append(resp.json())
                except Exception as e:
                    pass

        return created
