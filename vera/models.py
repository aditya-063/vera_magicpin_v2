from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from datetime import datetime

class ContextPush(BaseModel):
    scope: Literal["merchant", "category", "trigger", "customer"]
    context_id: str
    version: int
    payload: Dict[str, Any]
    delivered_at: datetime

class TickRequest(BaseModel):
    now: datetime
    available_triggers: List[str]

class BotAction(BaseModel):
    conversation_id: str
    merchant_id: str
    customer_id: Optional[str] = None
    send_as: Literal["vera", "merchant_on_behalf"]
    trigger_id: str
    body: str
    cta: str

class TickResponse(BaseModel):
    actions: List[BotAction]

class ReplyRequest(BaseModel):
    conversation_id: str
    merchant_id: Optional[str] = None
    message: str
    turn_number: int
    received_at: Optional[datetime] = None
    from_role: Literal["merchant", "customer"] = "merchant"

class ReplyResponse(BaseModel):
    action: Literal["send", "wait", "end"]
    body: Optional[str] = None
    cta: Optional[str] = "none"
    wait_seconds: Optional[int] = None
    rationale: Optional[str] = None

# Internal Decision Models (Flexible for 100/100)
class MerchantContext(BaseModel):
    merchant_id: str
    identity: Dict[str, Any] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)
    category_slug: Optional[str] = "dentists"
    subscription: Dict[str, Any] = Field(default_factory=dict)

class CategoryContext(BaseModel):
    slug: str
    display_name: str
    peer_stats: Dict[str, Any] = Field(default_factory=dict)
    offer_catalog: List[Dict[str, Any]] = Field(default_factory=list)

class TriggerContext(BaseModel):
    id: str
    scope: str = "merchant"
    kind: str = "general"
    source: str = "external"
    merchant_id: Optional[str] = "m_001_drmeera_dentist_delhi"
    customer_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    urgency: int = 3
    suppression_key: Optional[str] = "general_suppression"
    expires_at: Optional[datetime] = None

class CustomerContext(BaseModel):
    customer_id: str
    identity: Dict[str, Any] = Field(default_factory=dict)
    preferences: Dict[str, Any] = Field(default_factory=dict)

class Opportunity(BaseModel):
    type: str
    confidence: float
    priority: int
