import re
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.crud import crud_ticket
from app.models.ticket import TicketStatus, TicketPriority

# Dictionary to maintain context across requests based on user_id
# For production, this should ideally be in a cache store like Redis
_SESSION_MEMORIES: Dict[int, Dict[str, Any]] = {}

SYNONYMS = {
    "status": ["status", "state"],
    "summarize": ["summarize", "summary", "brief"],
    "show": ["show", "list", "display", "tickets"]
}

class AIAssistant:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id
        
        # Maintain context inside class
        if self.user_id not in _SESSION_MEMORIES:
            _SESSION_MEMORIES[self.user_id] = {}
        self.context = _SESSION_MEMORIES[self.user_id]

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        Main entry point for processing NLP questions.
        """
        try:
            parsed_query = self.parse_query(query)
            return self.execute_intent(parsed_query)
        except HTTPException:
            # Re-raise explicit HTTP exceptions
            raise
        except Exception as e:
            # Proper error handling capturing unexpected failures
            raise HTTPException(
                status_code=500,
                detail=self.format_error("Processing Error", f"Failed to process query: {str(e)}")
            )

    def parse_query(self, query: str) -> Dict[str, Any]:
        """
        Intent + Entity Separation Layer
        Supported Intents: GET_STATUS, SUMMARIZE, LIST_TICKETS, USER_TICKETS, UNKNOWN
        """
        query_lower = query.lower().strip()
        
        parsed = {
            "intent": "UNKNOWN",
            "ticket_id": None,
            "user_id": None,
            "filters": self.extract_filters(query_lower)
        }

        has_context_ref = bool(re.search(r'\b(it|its|this|that)\b', query_lower))
        context_ticket_id = self.context.get("last_ticket_id")

        # Create regex patterns dynamically from SYNONYMS
        status_pattern = r'\b(' + '|'.join(SYNONYMS["status"]) + r')\b'
        summarize_pattern = r'\b(' + '|'.join(SYNONYMS["summarize"]) + r')\b'
        show_pattern = r'\b(' + '|'.join(SYNONYMS["show"]) + r')\b'

        # 1. GET_STATUS
        if re.search(status_pattern, query_lower):
            ticket_id = self._extract_ticket_id(query_lower)
            if ticket_id is None and has_context_ref and context_ticket_id:
                ticket_id = context_ticket_id
                
            if ticket_id is not None:
                parsed["intent"] = "GET_STATUS"
                parsed["ticket_id"] = ticket_id
                return parsed

        # 2. SUMMARIZE
        if re.search(summarize_pattern, query_lower):
            ticket_id = self._extract_ticket_id(query_lower)
            if ticket_id is None and has_context_ref and context_ticket_id:
                ticket_id = context_ticket_id

            if ticket_id is not None:
                parsed["intent"] = "SUMMARIZE"
                parsed["ticket_id"] = ticket_id
                return parsed

        # 3. USER_TICKETS
        user_match = re.search(r'user\s+(\d+)', query_lower)
        if user_match:
            parsed["intent"] = "USER_TICKETS"
            parsed["user_id"] = int(user_match.group(1))
            return parsed

        # 4. LIST_TICKETS
        if re.search(show_pattern, query_lower):
            parsed["intent"] = "LIST_TICKETS"
            return parsed

        return parsed

    def _extract_ticket_id(self, query: str) -> Optional[int]:
        """
        Extracts ticket ID directly with flexible formats.
        """
        # Formats: 'ticket 1', 'ticket id 1', 'ticket #1'
        match = re.search(r'ticket\s*(?:id|#)?\s*(\d+)', query)
        if match:
            return int(match.group(1))
        
        # General number matcher if strictly nearby
        general_match = re.search(r'\b(\d+)\b', query)
        if general_match:
            return int(general_match.group(1))
            
        return None

    def extract_filters(self, query: str) -> Dict[str, Any]:
        """
        Dynamic Query Builder
        """
        filters = {}
        
        # Detect priority
        if "high" in query:
            filters["priority"] = "high"
        elif "medium" in query:
            filters["priority"] = "medium"
        elif "low" in query:
            filters["priority"] = "low"
            
        # Detect status
        if "open" in query:
            filters["status"] = "open"
        elif "closed" in query:
            filters["status"] = "closed"
        elif "in progress" in query or "in_progress" in query:
            filters["status"] = "in_progress"
            
        return filters

    def execute_intent(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execution Layer (Intent Handler). No regex logic here.
        Calls appropriate CRUD functions based on structured intent.
        """
        intent = parsed_query["intent"]
        
        if intent == "GET_STATUS":
            ticket_id = parsed_query["ticket_id"]
            if not ticket_id:
                raise HTTPException(status_code=400, detail=self.format_error("Invalid query", "Could not identify the ticket ID for the status request."))
                
            ticket = crud_ticket.get_ticket(self.db, ticket_id=ticket_id)
            if not ticket:
                raise HTTPException(status_code=404, detail=self.format_error("Not Found", f"Ticket {ticket_id} was not found."))
            
            # Save context
            self.context["last_ticket_id"] = ticket.id
            
            return self.format_response(intent, {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "status": ticket.status.value if hasattr(ticket.status, "value") else ticket.status
            })

        elif intent == "SUMMARIZE":
            ticket_id = parsed_query["ticket_id"]
            if not ticket_id:
                raise HTTPException(status_code=400, detail=self.format_error("Invalid query", "Could not identify the ticket ID to summarize."))
                
            ticket = crud_ticket.get_ticket(self.db, ticket_id=ticket_id)
            if not ticket:
                raise HTTPException(status_code=404, detail=self.format_error("Not Found", f"Ticket {ticket_id} was not found."))
            
            # Save context
            self.context["last_ticket_id"] = ticket.id
            
            return self.format_response(intent, {
                "ticket_id": ticket.id,
                "title": ticket.title,
                "description": ticket.description,
                "status": ticket.status.value if hasattr(ticket.status, "value") else ticket.status,
                "priority": ticket.priority.value if hasattr(ticket.priority, "value") else ticket.priority
            })

        elif intent == "USER_TICKETS":
            user_id = parsed_query["user_id"]
            filters = parsed_query.get("filters", {})
            db_filters = self._convert_filters(filters)
            
            tickets = crud_ticket.get_tickets(self.db, user_id=user_id, limit=50, **db_filters)
            self.context["last_filters"] = filters
            
            return self.format_response(intent, {
                "user_id": user_id,
                "tickets": [{"ticket_id": t.id, "title": t.title, "status": t.status.value if hasattr(t.status, "value") else t.status} for t in tickets]
            })

        elif intent == "LIST_TICKETS":
            filters = parsed_query.get("filters", {})
            
            # Fallback to previously stored context filters if no new ones exist
            if not filters and "last_filters" in self.context:
                filters = self.context["last_filters"]
                
            db_filters = self._convert_filters(filters)
            self.context["last_filters"] = filters
            
            tickets = crud_ticket.get_tickets(self.db, limit=50, **db_filters)
            return self.format_response(intent, {
                "filters": filters,
                "tickets": [{"ticket_id": t.id, "title": t.title, "status": t.status.value if hasattr(t.status, "value") else t.status, "priority": t.priority.value if hasattr(t.priority, "value") else t.priority} for t in tickets]
            })

        elif intent == "UNKNOWN":
            return {
                "message": "I didn't understand your query",
                "suggestions": [
                    "status of ticket 1",
                    "show open tickets",
                    "summarize ticket 2"
                ]
            }

        raise HTTPException(
            status_code=400, 
            detail=self.format_error("Invalid Intent", "Cannot execute an unknown or unsupported intent.")
        )

    def _convert_filters(self, filters: dict) -> dict:
        """
        Converts extracted string filters back to precise DB Enums.
        """
        db_filters = {}
        if "priority" in filters:
            try:
                db_filters["priority"] = TicketPriority(filters["priority"])
            except ValueError:
                pass
        if "status" in filters:
            try:
                db_filters["status"] = TicketStatus(filters["status"])
            except ValueError:
                pass
        return db_filters

    def format_response(self, intent: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensures a structured JSON response format.
        """
        return {
            "intent": intent,
            "data": data
        }

    def format_error(self, error: str, message: str) -> Dict[str, str]:
        """
        Ensures a structured error response format.
        """
        return {
            "error": error,
            "message": message
        }
