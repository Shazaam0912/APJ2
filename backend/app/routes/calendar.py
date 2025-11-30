from fastapi import APIRouter, Body, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List, Optional
from app.models.calendar import CalendarEvent, CalendarEventCreate, CalendarEventUpdate
from app.database import db
from bson import ObjectId
from datetime import datetime

router = APIRouter()

@router.post("/", response_description="Add new event", response_model=CalendarEvent)
async def create_event(event: CalendarEventCreate = Body(...)):
    event_dict = jsonable_encoder(event)
    new_event = await db["calendar"].insert_one(event_dict)
    created_event = await db["calendar"].find_one({"_id": new_event.inserted_id})
    return created_event

@router.get("/", response_description="List events", response_model=List[CalendarEvent])
async def list_events(
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    project_id: Optional[str] = None
):
    query = {}
    if project_id:
        query["project_id"] = project_id
    
    # Date range filtering
    if start and end:
        query["start"] = {"$gte": start.isoformat()}
        query["end"] = {"$lte": end.isoformat()}
    elif start:
        query["start"] = {"$gte": start.isoformat()}
    elif end:
        query["end"] = {"$lte": end.isoformat()}

    events = await db["calendar"].find(query).to_list(1000)
    return events

@router.get("/{id}", response_description="Get a single event", response_model=CalendarEvent)
async def show_event(id: str):
    if (event := await db["calendar"].find_one({"_id": id})) is not None:
        return event
    raise HTTPException(status_code=404, detail=f"Event {id} not found")

@router.put("/{id}", response_description="Update an event", response_model=CalendarEvent)
async def update_event(id: str, event: CalendarEventUpdate = Body(...)):
    event_dict = {k: v for k, v in event.model_dump().items() if v is not None}

    if len(event_dict) >= 1:
        update_result = await db["calendar"].update_one({"_id": id}, {"$set": event_dict})

        if update_result.modified_count == 1:
            if (updated_event := await db["calendar"].find_one({"_id": id})) is not None:
                return updated_event

    if (existing_event := await db["calendar"].find_one({"_id": id})) is not None:
        return existing_event

    raise HTTPException(status_code=404, detail=f"Event {id} not found")

@router.delete("/{id}", response_description="Delete an event")
async def delete_event(id: str):
    delete_result = await db["calendar"].delete_one({"_id": id})

    if delete_result.deleted_count == 1:
        return {"message": "Event deleted successfully"}

    raise HTTPException(status_code=404, detail=f"Event {id} not found")
