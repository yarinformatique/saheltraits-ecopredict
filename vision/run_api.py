"""
Convenience launcher for the Morpho-Analyzer FastAPI service.
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run("morpho_vision.api.main:app", host="0.0.0.0", port=8001, reload=True)
