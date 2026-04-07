from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate, TicketStatusUpdate, TicketResponse
from app.crud import crud_ticket, crud_user

router = APIRouter()

@router.post("/", response_model=TicketResponse)
def create_ticket(
    ticket_in: TicketCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_ticket.create_ticket(db=db, ticket=ticket_in, user_id=current_user.id)

@router.get("/", response_model=List[TicketResponse])
def get_tickets(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return crud_ticket.get_tickets(
        db=db, skip=skip, limit=limit, status=status, priority=priority, category=category, user_id=current_user.id
    )

@router.get("/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = crud_ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return ticket

@router.put("/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    ticket_in: TicketUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = crud_ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    if ticket_in.assigned_to is not None:
        user = crud_user.get_user(db=db, user_id=ticket_in.assigned_to)
        if not user:
            raise HTTPException(status_code=400, detail="Assigned user does not exist")
            
    return crud_ticket.update_ticket(db=db, db_ticket=ticket, ticket_in=ticket_in)

@router.patch("/{ticket_id}/status", response_model=TicketResponse)
def update_ticket_status(
    ticket_id: int,
    status_in: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = crud_ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return crud_ticket.update_ticket_status(db=db, db_ticket=ticket, status_in=status_in)

@router.delete("/{ticket_id}")
def delete_ticket(
    ticket_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ticket = crud_ticket.get_ticket(db=db, ticket_id=ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    if ticket.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    crud_ticket.delete_ticket(db=db, db_ticket=ticket)
    return {"detail": "Ticket successfully deleted"}
