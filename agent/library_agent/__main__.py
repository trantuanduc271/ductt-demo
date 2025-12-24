import os
import uvicorn
import logging
from starlette.middleware.cors import CORSMiddleware

from agent import a2a_app

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # Add permissive CORS for demo/local use; tighten if exposing externally.
    a2a_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    port = int(os.getenv("LIBRARY_AGENT_PORT", "9999"))
    logger.info("Starting Library/Knowledge Agent on port %s...", port)
    uvicorn.run(a2a_app, host="0.0.0.0", port=port, log_level="info")

