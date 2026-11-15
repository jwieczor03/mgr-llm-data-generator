from contextlib import asynccontextmanager

from fastapi import FastAPI, Request

from application_api.config import load_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.settings, app.state.config_report = load_config()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/health/config")
def config(request: Request) -> dict:
    return request.app.state.config_report
