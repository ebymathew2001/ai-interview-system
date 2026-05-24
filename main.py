from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.database import create_tables
from app.routes import session, agent, audio, report


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    yield


app = FastAPI(
    title="AI Interview System",
    description="Automated voice-based interview platform powered by LangGraph + LLaMA 3",
    version="1.0.0",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

app.include_router(session.router, prefix="/session", tags=["Session"])
app.include_router(agent.router, prefix="/agent",   tags=["Agent"])
app.include_router(audio.router,                    tags=["Audio"])
app.include_router(report.router, prefix="/report", tags=["Report"])


@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("frontend/index.html")


@app.get("/interview", include_in_schema=False)
async def serve_interview():
    return FileResponse("frontend/interview.html")


@app.get("/report-page", include_in_schema=False)
async def serve_report_page():
    return FileResponse("frontend/report.html")