from fastapi import FastAPI

app = FastAPI()


@app.get("/health/live")
def live() -> dict[str, str]:
    return {"status": "ok"}
