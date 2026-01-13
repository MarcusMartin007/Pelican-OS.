from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from enum import Enum
import uuid
from datetime import datetime

class TaskStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARN = "WARN"
    INFO = "INFO"

@dataclass
class AuditTask:
    task_id: str
    layer: int
    name: str
    description: str
    status: TaskStatus = TaskStatus.INFO
    score_impact: int = 0
    max_points: int = 0
    evidence: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

@dataclass
class LayerScore:
    layer_id: int
    name: str
    points_earned: int = 0
    max_points: int = 0
    percentage: float = 0.0
    grade: str = "N/A"
    tasks: List[AuditTask] = field(default_factory=list)
    summary: str = ""

@dataclass
class OverallScore:
    total_points: int = 0
    max_total_points: int = 0
    grade: str = "N/A"
    summary_text: str = ""
    ai_narrative: Dict[str, Any] = field(default_factory=dict)
    layer_scores: List[LayerScore] = field(default_factory=list)

@dataclass
class AuditSubmission:
    business_name: str
    website_url: str
    contact_email: str
    location: str = ""
    services: List[str] = field(default_factory=list)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)

@dataclass
class AuditResult:
    submission: AuditSubmission
    overall_score: OverallScore
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = field(default_factory=datetime.utcnow)
