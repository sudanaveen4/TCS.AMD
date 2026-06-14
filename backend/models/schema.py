from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class Status(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"

class Machine(BaseModel):
    machine_id: str
    name: str
    manufacturer: str
    machine_type: str
    zone_id: str
    status: str = "active"
    health_score: float = 100.0
    throughput: float = 0.0
    failure_probability: float = 0.0
    rul_days: int = 999
    predicted_failure_mode: str = "none"

class Zone(BaseModel):
    zone_id: str
    name: str
    risk_score: float = 0.0

class Incident(BaseModel):
    incident_id: str
    machine_id: str
    zone_id: str
    severity: Severity
    incident_type: str
    failure_probability: float = 0.0
    rul_days: int = 999
    status: Status = Status.OPEN
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    root_cause: Optional[str] = None
    evidence_links: List[str] = []

class Alert(BaseModel):
    alert_id: str
    persona: str
    incident_id: str
    priority: Severity
    status: Status = Status.OPEN

class Task(BaseModel):
    task_id: str
    persona: str
    owner: str
    incident_id: str
    eta_minutes: int
    status: Status = Status.OPEN
    description: str

class ShiftReport(BaseModel):
    report_id: str
    shift_id: str
    persona: str
    generated_time: datetime = Field(default_factory=datetime.utcnow)
    content: str
    report_path: Optional[str] = None

class Document(BaseModel):
    document_id: str
    machine_id: str
    title: str
    chunk_text: str
    metadata: Dict[str, str] = {}
