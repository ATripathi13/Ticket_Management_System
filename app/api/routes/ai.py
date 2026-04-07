from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.services.ai_assistant import AIAssistant

router = APIRouter()

class AIQuery(BaseModel):
    query: str

class AIResponse(BaseModel):
    response: str

@router.post("/query", response_model=AIResponse)
def query_ai(
    query_in: AIQuery,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Experimental Rule-based AI Assistant endpoint.
    Pass in natural language queries like:
    - "What is the status of ticket 12?"
    - "Show all high priority open tickets"
    - "Summarize ticket 5"
    - "Which tickets were created by user 1?"
    """
    assistant = AIAssistant(db=db)
    result = assistant.process_query(query_in.query)
    return AIResponse(response=result)
