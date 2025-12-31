from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel


class InboxItem(BaseModel):
    id: str
    kind: Literal["booking", "callback"]
    priority: Literal["urgent", "normal"]
    status: Literal["open", "done"]
    label: str
    time: Optional[str] = None
    created_at: datetime
