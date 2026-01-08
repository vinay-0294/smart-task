"""
In-memory database with SQLite for persistence.
Simple implementation using sqlite3 for a 4-hour exercise.
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Dict, Any
import threading

DATABASE_PATH = "tasks.db"

# Thread-local storage for connections
_local = threading.local()

def get_connection() -> sqlite3.Connection:
    """Get thread-local database connection."""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        _local.connection.row_factory = sqlite3.Row
    return _local.connection

def init_db():
    """Initialize database tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create projects table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    """)
    
    # Create tasks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT NOT NULL DEFAULT 'Todo',
            priority TEXT NOT NULL DEFAULT 'Med',
            project_id INTEGER NOT NULL,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    
    conn.commit()

def reset_db():
    """Reset database - useful for testing."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS tasks")
    cursor.execute("DROP TABLE IF EXISTS projects")
    conn.commit()
    init_db()

# Project operations
def create_project(name: str) -> Dict[str, Any]:
    """Create a new project."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO projects (name) VALUES (?)", (name,))
    conn.commit()
    return {"id": cursor.lastrowid, "name": name}

def get_all_projects() -> List[Dict[str, Any]]:
    """Get all projects."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM projects ORDER BY id")
    return [dict(row) for row in cursor.fetchall()]

def get_project_by_id(project_id: int) -> Optional[Dict[str, Any]]:
    """Get a project by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM projects WHERE id = ?", (project_id,))
    row = cursor.fetchone()
    return dict(row) if row else None

# Task operations
def create_task(project_id: int, title: str, description: Optional[str], 
                status: str, priority: str) -> Dict[str, Any]:
    """Create a new task."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO tasks (title, description, status, priority, project_id) 
           VALUES (?, ?, ?, ?, ?)""",
        (title, description, status, priority, project_id)
    )
    conn.commit()
    return {
        "id": cursor.lastrowid,
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "project_id": project_id
    }

def get_tasks_by_project(project_id: int, status: Optional[str] = None) -> List[Dict[str, Any]]:
    """Get tasks for a project, optionally filtered by status."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if status:
        cursor.execute(
            """SELECT id, title, description, status, priority, project_id 
               FROM tasks WHERE project_id = ? AND status = ? ORDER BY id""",
            (project_id, status)
        )
    else:
        cursor.execute(
            """SELECT id, title, description, status, priority, project_id 
               FROM tasks WHERE project_id = ? ORDER BY id""",
            (project_id,)
        )
    
    return [dict(row) for row in cursor.fetchall()]

def get_task_by_id(task_id: int) -> Optional[Dict[str, Any]]:
    """Get a task by ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, title, description, status, priority, project_id 
           FROM tasks WHERE id = ?""",
        (task_id,)
    )
    row = cursor.fetchone()
    return dict(row) if row else None

def update_task(task_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update a task."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Build dynamic update query
    update_fields = []
    values = []
    for key, value in updates.items():
        if value is not None:
            update_fields.append(f"{key} = ?")
            values.append(value)
    
    if not update_fields:
        return get_task_by_id(task_id)
    
    values.append(task_id)
    query = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
    cursor.execute(query, values)
    conn.commit()
    
    return get_task_by_id(task_id)

# Initialize database on module load
init_db()

