# app/inbox/router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from inbox.service import build_inbox
from inbox.models import InboxItem
from schemas import PracticeId

router = APIRouter(prefix="/api/inbox", tags=["Inbox"])


@router.get("", response_model=List[InboxItem])
def get_inbox(
    practice_id: PracticeId = Query(..., description="Mandanten-ID"),
    db: Session = Depends(get_db),
):
    """
    Liefert die Inbox für eine Praxis.
    - DB-basiert
    - mandantenfähig
    - frontend-sicher (immer Liste)
    """
    return build_inbox(db=db, practice_id=practice_id.value)
