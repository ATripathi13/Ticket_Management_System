from pydantic import BaseModel
from app.models.ticket import TicketStatus, TicketPriority
from typing import Optional
from datetime import datetime

class TicketBase(BaseModel):
    title: str
    description: Optional[str] = None
    priority: Optional[TicketPriority] = TicketPriority.medium
    category: Optional[str] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    category: Optional[str] = None
    assigned_to: Optional[int] = None

class TicketStatusUpdate(BaseModel):
    status: TicketStatus

class TicketResponse(TicketBase):
    id: int
    status: TicketStatus
    created_by: int
    assigned_to: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True
    }
