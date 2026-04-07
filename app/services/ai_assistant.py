import re
from sqlalchemy.orm import Session
from app.crud import crud_ticket
from app.models.ticket import TicketStatus, TicketPriority

class AIAssistant:
    def __init__(self, db: Session):
        self.db = db

    def process_query(self, query: str):
        query_lower = query.lower()

        try:
            # 1. "What is the status of ticket 12?"
            match = re.search(r'status of ticket (\d+)', query_lower)
            if match:
                ticket_id = int(match.group(1))
                ticket = crud_ticket.get_ticket(db=self.db, ticket_id=ticket_id)
                if ticket:
                    return f"The status of ticket {ticket_id} ('{ticket.title}') is {ticket.status.value}."
                return f"Ticket {ticket_id} was not found."

            # 2. "Summarize ticket 5"
            match = re.search(r'summarize ticket (\d+)', query_lower)
            if match:
                ticket_id = int(match.group(1))
                ticket = crud_ticket.get_ticket(db=self.db, ticket_id=ticket_id)
                if ticket:
                    return f"Ticket {ticket.id}: {ticket.title}. Description: {ticket.description}. Status: {ticket.status.value}. Priority: {ticket.priority.value}."
                return f"Ticket {ticket_id} was not found."

            # 3. "Show all high priority open tickets"
            if "high priority" in query_lower and "open" in query_lower:
                tickets = crud_ticket.get_tickets(db=self.db, priority=TicketPriority.high, status=TicketStatus.open)
                if not tickets:
                    return "There are no high priority open tickets right now."
                return "High priority open tickets:\n" + "\n".join([f"- Ticket {t.id}: {t.title}" for t in tickets])

            # 4. "Which tickets were created by user X?"
            match = re.search(r'created by user (\d+)', query_lower)
            if match:
                user_id = int(match.group(1))
                tickets = crud_ticket.get_tickets(db=self.db, user_id=user_id, limit=50)
                if not tickets:
                    return f"User {user_id} has not created any tickets."
                return f"Tickets created by user {user_id}:\n" + "\n".join([f"- Ticket {t.id}: {t.title}" for t in tickets])

            return "I'm sorry, I couldn't understand that query. Try asking about the status of a specific ticket ('status of ticket 1'), summarizing a ticket ('summarize ticket 1'), or viewing your open high priority ones."
        except Exception as e:
            return f"An error occurred while parsing your request: {e}"
