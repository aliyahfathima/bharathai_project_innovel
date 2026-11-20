from typing import Optional, List, Literal
from pydantic import BaseModel, Field, ConfigDict

class CitizenProfile(BaseModel):
    model_config = ConfigDict(extra="ignore")
    name: Optional[str] = None
    age: Optional[int] = Field(default=None, ge=0, le=120)
    state: str = "Tamil Nadu"
    district: Optional[str] = None
    annual_income: Optional[float] = Field(default=None, ge=0)
    occupation: Optional[str] = None
    education: Optional[str] = None
    gender: Optional[str] = None
    category: Optional[str] = None
    disability: Optional[bool] = None
    marital_status: Optional[str] = None
    family_size: Optional[int] = Field(default=None, ge=1, le=30)
    need: str = "General welfare support"

class EligibilityResult(BaseModel):
    status: Literal[
        "Potential Match",
        "Possible Match",
        "More Information Required",
        "Potential Mismatch"
    ]
    satisfied: List[str] = []
    not_satisfied: List[str] = []
    missing: List[str] = []
    needs_verification: List[str] = []
    explanation: str

class Scheme(BaseModel):
    name: str
    department: str = "Department not confirmed"
    level: str = "Not confirmed"
    benefit: str = "Refer to official source"
    eligibility: List[str] = []
    documents: List[str] = []
    application_steps: List[str] = []
    official_url: Optional[str] = None
    source_title: str = "Search result"
    source_url: str
    retrieved_at: str
    deadline: Optional[str] = None
    contact: Optional[str] = None
    notes: List[str] = []
