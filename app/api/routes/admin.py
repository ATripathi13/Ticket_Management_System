from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from app.db.session import get_db
from app.api.deps import get_current_active_admin
from app.models.user import User
from app.models.ticket import Ticket
from app.schemas.ticket import TicketResponse

router = APIRouter()

@router.get("/tickets", response_model=List[TicketResponse])
def get_all_tickets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin)
):
    """
    Retrieve all tickets across all users. Admin only.
    """
    tickets = db.query(Ticket).offset(skip).limit(limit).all()
    return tickets

@router.get("/stats")
def get_stats(
    db: Session = Depends(get_db),
    admin_user: User = Depends(get_current_active_admin)
):
    """
    Retrieve ticket statistics: counts by status, priority, etc.
    """
    status_counts = db.query(Ticket.status, func.count(Ticket.id)).group_by(Ticket.status).all()
    priority_counts = db.query(Ticket.priority, func.count(Ticket.id)).group_by(Ticket.priority).all()
    
    return {
        "status_distribution": {status.value: count for status, count in status_counts},
        "priority_distribution": {priority.value: count for priority, count in priority_counts},
        "total_tickets": sum(count for _, count in status_counts)
    }
