from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusUpdate
from typing import Optional

def get_ticket(db: Session, ticket_id: int):
    return db.query(Ticket).filter(Ticket.id == ticket_id).first()

def get_tickets(
    db: Session, 
    skip: int = 0, 
    limit: int = 10, 
    status: Optional[str] = None, 
    priority: Optional[str] = None, 
    category: Optional[str] = None,
    user_id: Optional[int] = None
):
    query = db.query(Ticket)
    if status:
        query = query.filter(Ticket.status == status)
    if priority:
        query = query.filter(Ticket.priority == priority)
    if category:
        query = query.filter(Ticket.category == category)
    if user_id is not None:
        query = query.filter(Ticket.created_by == user_id)
        
    return query.offset(skip).limit(limit).all()

def create_ticket(db: Session, ticket: TicketCreate, user_id: int):
    try:
        db_ticket = Ticket(
            **ticket.model_dump(),
            created_by=user_id
        )
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {e.orig}")

def update_ticket(db: Session, db_ticket: Ticket, ticket_in: TicketUpdate):
    try:
        update_data = ticket_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_ticket, field, value)
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database constraint error. Possibly assigning to a non-existent user.")

def update_ticket_status(db: Session, db_ticket: Ticket, status_in: TicketStatusUpdate):
    try:
        db_ticket.status = status_in.status
        db.add(db_ticket)
        db.commit()
        db.refresh(db_ticket)
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {e.orig}")

def delete_ticket(db: Session, db_ticket: Ticket):
    try:
        db.delete(db_ticket)
        db.commit()
        return db_ticket
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Database integrity error: {e.orig}")
