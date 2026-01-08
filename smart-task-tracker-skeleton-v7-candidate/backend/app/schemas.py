from typing import Optional, Literal
from pydantic import BaseModel, Field

Priority = Literal["Low", "Med", "High"]
Status = Literal["Todo", "In-Progress", "Done"]

class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)

class ProjectRead(BaseModel):
    id: int
    name: str

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=300)
    description: Optional[str] = None
    status: Status = "Todo"
    priority: Priority = "Med"

class TaskRead(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: Status
    priority: Priority
    project_id: int

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None

class AIIntakeRequest(BaseModel):
    input: str = Field(min_length=1, max_length=2000)

class AIIntakeResponse(BaseModel):
    title: str
    priority: Priority