from fastapi import FastAPI

app = FastAPI(
    title="Catalyst API",
    description="Backend API for the talent scouting and engagement agent",
    version="0.1.0",
)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
