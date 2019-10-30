import logging
import typing as T
from datetime import datetime

import pydantic
from fastapi import FastAPI, Depends, Body
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.exceptions import HTTPException
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_404_NOT_FOUND,
)

#  --- Config ---
DB_NAME = "storage-dev"
TABLE_EVENTS = "events"


#  --- Init ---
class DataBase:
    client: AsyncIOMotorClient = None


app = FastAPI()
db = DataBase()


#  --- Db Utils ---
async def get_database():
    return db.client


async def connect_to_mongo():
    logging.info("Connect to MongoDB...")
    db.client = AsyncIOMotorClient("mongodb://localhost:27017", maxPoolSize=4, minPoolSize=2)
    logging.info("Connection established ！")


async def close_mongo_connection():
    logging.info("Disconnect MongoDB...")
    db.client.close()
    logging.info("Connection removed ！")


#  --- Models ---
class EventModel(pydantic.BaseModel):
    type: str
    state: int  # 0 - not finished event, 1 - finished event
    started_at: datetime = None
    finished_at: T.Optional[datetime] = None

    @pydantic.validator('started_at', pre=True, always=True)
    def default_started_at(cls, v):
        return v or datetime.utcnow()


class EventIn(pydantic.BaseModel):
    type: str


class EventOut(EventModel):
    id: str


#  --- Controllers ---
ROUTE_PREFIX = "/v1"


class GetListResponse(pydantic.BaseModel):
    count: int
    items: T.List[EventOut]


class NotGetResponse(pydantic.BaseModel):
    status: str


@app.get(f"{ROUTE_PREFIX}/events", response_model=GetListResponse)
async def get_list(conn: AsyncIOMotorClient = Depends(get_database)):
    count = await conn[DB_NAME][TABLE_EVENTS].count_documents({})
    rows = conn[DB_NAME][TABLE_EVENTS].find({}, limit=100, skip=0)

    return {
        "count": count,
        "items": [EventOut(id=str(row.pop("_id")), **row) async for row in rows]
    }


@app.post(
    f"{ROUTE_PREFIX}/events/start",
    response_model=NotGetResponse,
    status_code=HTTP_201_CREATED
)
async def start(
        event: EventIn = Body(..., embed=False),
        conn: AsyncIOMotorClient = Depends(get_database)
):
    existed = await conn[DB_NAME][TABLE_EVENTS].find_one({"type": event.type})
    if not existed:
        await conn[DB_NAME][TABLE_EVENTS].insert_one(EventModel(
            type=event.type,
            state=0
        ).dict())

    return {"status": "success"}


@app.post(
    f"{ROUTE_PREFIX}/events/finish",
    response_model=NotGetResponse
)
async def finish(
        event: EventIn = Body(..., embed=False),
        conn: AsyncIOMotorClient = Depends(get_database)
):
    existed = await conn[DB_NAME][TABLE_EVENTS].find_one({"type": event.type})
    if not existed:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"Event with type '{event.type}' not found",
        )

    existed = EventModel(**existed)
    existed.state = 1
    existed.finished_at = datetime.utcnow()

    await conn[DB_NAME][TABLE_EVENTS].replace_one({"type": event.type}, existed.dict())

    return {"status": "success"}


#  --- App Configuration ---
app.add_event_handler("startup", connect_to_mongo)
app.add_event_handler("shutdown", close_mongo_connection)
