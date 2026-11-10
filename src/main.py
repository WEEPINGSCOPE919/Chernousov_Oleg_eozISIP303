from fastapi import FastAPI

from .api import router

app = FastAPI(
    title="Система учёта заявок",
    version="1.0.0",
    description="REST API для учебного проекта «Система учёта заявок»",
)

app.include_router(router)


@app.get("/health", tags=["system"], summary="Проверка доступности")
def health():
    return {"status": "ok"}