/**
 * API client for Smart Task Tracker backend
 */

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

// Types
export type Priority = 'Low' | 'Med' | 'High';
export type Status = 'Todo' | 'In-Progress' | 'Done';

export interface Project {
  id: number;
  name: string;
}

export interface Task {
  id: number;
  title: string;
  description: string | null;
  status: Status;
  priority: Priority;
  project_id: number;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: Status;
  priority?: Priority;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: Status;
  priority?: Priority;
}

export interface AIIntakeResult {
  title: string;
  priority: Priority;
}

// API functions

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }
  return response.json();
}

// Projects
export async function getProjects(): Promise<Project[]> {
  const response = await fetch(`${API_BASE}/api/projects`);
  return handleResponse<Project[]>(response);
}

export async function createProject(name: string): Promise<Project> {
  const response = await fetch(`${API_BASE}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  });
  return handleResponse<Project>(response);
}

// Tasks
export async function getTasks(projectId: number, status?: Status): Promise<Task[]> {
  const url = new URL(`${API_BASE}/api/projects/${projectId}/tasks`);
  if (status) {
    url.searchParams.set('status', status);
  }
  const response = await fetch(url.toString());
  return handleResponse<Task[]>(response);
}

export async function createTask(projectId: number, task: TaskCreate): Promise<Task> {
  const response = await fetch(`${API_BASE}/api/projects/${projectId}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  });
  return handleResponse<Task>(response);
}

export async function updateTask(taskId: number, updates: TaskUpdate): Promise<Task> {
  const response = await fetch(`${API_BASE}/api/tasks/${taskId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updates),
  });
  return handleResponse<Task>(response);
}

// AI Intake
export async function smartIntake(input: string): Promise<AIIntakeResult> {
  const response = await fetch(`${API_BASE}/api/ai/intake`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input }),
  });
  return handleResponse<AIIntakeResult>(response);
}

