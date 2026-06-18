import logging

from fastapi import FastAPI

from app.api.routes import router
from app.config import configure_langsmith

logging.basicConfig(level=logging.INFO)

configure_langsmith()

app = FastAPI(
    title="Multi-Agent Research Assistant",
    description="Generates comprehensive research reports using LangGraph multi-agent workflows.",
    version="1.0.0",
)

app.include_router(router)
