import uvicorn
import logging
from starlette.middleware.cors import CORSMiddleware
from agent import a2a_app


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Enable more verbose logging for ADK A2A to debug response handling
logging.getLogger("google_adk").setLevel(logging.DEBUG)
logging.getLogger("a2a").setLevel(logging.DEBUG)


if __name__ == "__main__":
    a2a_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("Starting DevOps Root Agent on port 9995...")
    uvicorn.run(a2a_app, host="0.0.0.0", port=9995, log_level="info")


