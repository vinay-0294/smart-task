import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from . import schemas
from . import database as db
from . import ai_intake

app = FastAPI(title="Smart Task Tracker API", version="1.0.0")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    """Health check endpoint."""
    return {"ok": True}


# --- Projects API ---

@app.get("/api/projects", response_model=List[schemas.ProjectRead])
def list_projects():
    """List all projects."""
    projects = db.get_all_projects()
    return projects


@app.post("/api/projects", response_model=schemas.ProjectRead, status_code=201)
def create_project(body: schemas.ProjectCreate):
    """Create a new project."""
    try:
        project = db.create_project(body.name)
        return project
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="Project name already exists")
        raise HTTPException(status_code=500, detail=str(e))


# --- Tasks API ---

@app.get("/api/projects/{project_id}/tasks", response_model=List[schemas.TaskRead])
def list_tasks(project_id: int, status: Optional[schemas.Status] = Query(None)):
    """
    List tasks for a project.
    Optionally filter by status (Todo, In-Progress, Done).
    """
    # Check if project exists
    project = db.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    tasks = db.get_tasks_by_project(project_id, status)
    return tasks


@app.post("/api/projects/{project_id}/tasks", response_model=schemas.TaskRead, status_code=201)
def create_task(project_id: int, body: schemas.TaskCreate):
    """Create a new task in a project."""
    # Check if project exists
    project = db.get_project_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    task = db.create_task(
        project_id=project_id,
        title=body.title,
        description=body.description,
        status=body.status,
        priority=body.priority
    )
    return task


@app.patch("/api/tasks/{task_id}", response_model=schemas.TaskRead)
def update_task(task_id: int, body: schemas.TaskUpdate):
    """Update an existing task."""
    # Check if task exists
    existing_task = db.get_task_by_id(task_id)
    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Build updates dict
    updates = {}
    if body.title is not None:
        updates["title"] = body.title
    if body.description is not None:
        updates["description"] = body.description
    if body.status is not None:
        updates["status"] = body.status
    if body.priority is not None:
        updates["priority"] = body.priority
    
    updated_task = db.update_task(task_id, updates)
    return updated_task


# --- AI Intake API ---

@app.post("/api/ai/intake", response_model=schemas.AIIntakeResponse)
def ai_intake_endpoint(body: schemas.AIIntakeRequest):
    """
    Smart Intake: Process user text and suggest title + priority.
    
    This is a FAKE adapter that uses deterministic rules:
    - Extracts title from first sentence
    - Detects priority based on keywords
    """
    title, priority = ai_intake.process_intake(body.input)
    return schemas.AIIntakeResponse(title=title, priority=priority)
