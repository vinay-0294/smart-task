# Smart Task Tracker

A modern task management application built with **Next.js (React)** and **FastAPI (Python)**, featuring AI-powered smart intake for automatic task creation from natural language.

![Smart Task Tracker](https://img.shields.io/badge/Next.js-14-black?logo=next.js) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi) ![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python) ![TypeScript](https://img.shields.io/badge/TypeScript-5.6-blue?logo=typescript)

## Features

- **📁 Project Management** - Create and manage multiple projects
- **📋 Task Management** - Create, edit, and update tasks with title, description, status, and priority
- **🔍 Status Filtering** - Filter tasks by Todo, In-Progress, or Done
- **🤖 Smart Intake** - Paste text (emails, messages) and auto-extract task title & priority
- **🎨 Modern UI** - Beautiful dark theme with smooth animations

## Quickstart

### Using Docker (Recommended)

```bash
# Clone and navigate to project
cd smart-task-tracker-skeleton-v7-candidate

# Copy environment file (optional)
cp .env.example .env

# Build and run with Docker Compose
docker compose up --build

# Access the application:
# Web UI: http://localhost:3000
# API Docs: http://localhost:8000/docs
# Health Check: http://localhost:8000/healthz
```

### Manual Setup

#### Backend (FastAPI)
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```

## Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# Or using the script
./scripts/test.sh
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/healthz` | Health check |
| GET | `/api/projects` | List all projects |
| POST | `/api/projects` | Create a project |
| GET | `/api/projects/{id}/tasks` | List tasks (optional `?status=` filter) |
| POST | `/api/projects/{id}/tasks` | Create a task |
| PATCH | `/api/tasks/{id}` | Update a task |
| POST | `/api/ai/intake` | Smart Intake - extract title & priority from text |

## Design Choices

### Backend Architecture

1. **SQLite Database** - Chosen for simplicity and zero-configuration setup. The `database.py` module provides a clean abstraction layer that could easily be swapped for PostgreSQL or another database.

2. **Thread-Local Connections** - Using thread-local storage for SQLite connections to handle concurrent requests safely.

3. **FAKE AI Adapter** - The smart intake uses a deterministic rule-based approach:
   - **Title Extraction**: Takes the first sentence, removes common action prefixes ("I need to", "Please", etc.)
   - **Priority Detection**: Keyword matching for urgency indicators ("urgent", "asap" → High; "later", "nice to have" → Low)

4. **Pydantic Validation** - All request/response models use Pydantic for automatic validation and serialization.

### Frontend Architecture

1. **React with Hooks** - Using `useState` and `useEffect` for state management. For a 4-hour project, this is simpler than Redux/Zustand.

2. **CSS-in-CSS** - Pure CSS with CSS variables for theming. Provides great performance and no build-time overhead.

3. **Component Structure** - Single-page application with modal dialogs for forms. Clean separation between task list, filters, and smart intake.

### Smart Intake Flow

1. User pastes text (email, message, notes) into the Smart Intake textarea
2. Click "Analyze Text" to send to `/api/ai/intake`
3. Backend extracts title and detects priority
4. User reviews suggestions and clicks "Create Task with These Details"
5. Form opens pre-filled with the suggestions

## Trade-offs & TODOs

### What's Included ✅
- Full CRUD for projects and tasks
- Status filtering (Todo/In-Progress/Done)
- Priority support (Low/Med/High)
- Smart Intake with title extraction and priority detection
- Comprehensive backend tests (12+ test cases)
- Modern, responsive UI with animations

### Future Improvements 📝
- [ ] **Task Deletion** - Add delete functionality for tasks
- [ ] **Search** - Add text search across tasks
- [ ] **Persistence** - Move SQLite file to a Docker volume
- [ ] **Real AI Integration** - Replace FAKE adapter with OpenAI/Claude
- [ ] **Due Dates** - Add deadline tracking
- [ ] **User Authentication** - Multi-user support
- [ ] **Drag & Drop** - Kanban-style task reordering
- [ ] **Frontend Tests** - Add React Testing Library tests

## AI Usage Report

### Tools Used
- **GitHub Copilot** - Code completion and suggestions
- **Claude** - Architecture discussions and code review

### AI-Assisted Components
1. **CSS Styling** - AI helped generate the dark theme color palette and CSS variables
2. **Priority Keywords** - AI suggested comprehensive lists of urgency-related keywords
3. **Test Cases** - AI helped identify edge cases for error handling tests

### Human Decisions
1. **Architecture** - Database schema, API design, component structure
2. **UI/UX Flow** - Smart Intake workflow and task management patterns
3. **Error Handling** - Validation rules and error messages
4. **Code Organization** - File structure and module separation

## Project Structure

```
smart-task-tracker-skeleton-v7-candidate/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI routes
│   │   ├── schemas.py       # Pydantic models
│   │   ├── database.py      # SQLite database layer
│   │   └── ai_intake.py     # FAKE AI adapter
│   ├── tests/
│   │   ├── test_health.py
│   │   └── test_api.py      # API tests (happy + error paths)
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── globals.css      # Theme and styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main application
│   ├── lib/
│   │   └── api.ts           # API client
│   ├── Dockerfile
│   └── package.json
├── scripts/
│   ├── test.sh
│   └── clean.sh
├── docker-compose.yml
├── .env.example
├── CANDIDATE.md
└── README.md
```

## License

MIT
