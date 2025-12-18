import uvicorn
import logging
from starlette.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from agent import a2a_app

if __name__ == '__main__':
    # Add CORS middleware to the app
    a2a_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info("Starting Kubernetes Agent on port 9996...")
    uvicorn.run(a2a_app, host='0.0.0.0', port=9996, log_level="info")
