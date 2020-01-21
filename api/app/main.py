from fastapi import FastAPI

from app import db
from app.routers import twigs

app = FastAPI()


@app.on_event("startup")
async def startup():
    await db.database.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.database.disconnect()


app.include_router(
    twigs.router,
    prefix="/twigs",
    tags=["twigs"],
    responses={404: {"description": "Not found"}},
)
