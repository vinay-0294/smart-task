'use client';

import { useState, useEffect, useCallback } from 'react';
import * as api from '../lib/api';
import type { Project, Task, Status, Priority } from '../lib/api';

// Status filter options
const STATUS_OPTIONS: (Status | 'All')[] = ['All', 'Todo', 'In-Progress', 'Done'];
const PRIORITY_OPTIONS: Priority[] = ['Low', 'Med', 'High'];

export default function Page() {
  // State
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProjectId, setSelectedProjectId] = useState<number | null>(null);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [statusFilter, setStatusFilter] = useState<Status | 'All'>('All');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Form state
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [taskTitle, setTaskTitle] = useState('');
  const [taskDescription, setTaskDescription] = useState('');
  const [taskStatus, setTaskStatus] = useState<Status>('Todo');
  const [taskPriority, setTaskPriority] = useState<Priority>('Med');
  const [formLoading, setFormLoading] = useState(false);
  
  // Project form state
  const [showProjectForm, setShowProjectForm] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  
  // Smart Intake state
  const [intakeText, setIntakeText] = useState('');
  const [intakeResult, setIntakeResult] = useState<api.AIIntakeResult | null>(null);
  const [intakeLoading, setIntakeLoading] = useState(false);

  // Load projects
  useEffect(() => {
    loadProjects();
  }, []);

  // Load tasks when project or filter changes
  useEffect(() => {
    if (selectedProjectId) {
      loadTasks();
    }
  }, [selectedProjectId, statusFilter]);

  const loadProjects = async () => {
    try {
      const data = await api.getProjects();
      setProjects(data);
      if (data.length > 0 && !selectedProjectId) {
        setSelectedProjectId(data[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const loadTasks = async () => {
    if (!selectedProjectId) return;
    try {
      const status = statusFilter === 'All' ? undefined : statusFilter;
      const data = await api.getTasks(selectedProjectId, status);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    }
  };

  // Project handlers
  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    
    try {
      const project = await api.createProject(newProjectName.trim());
      setProjects([...projects, project]);
      setSelectedProjectId(project.id);
      setNewProjectName('');
      setShowProjectForm(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
    }
  };

  // Task handlers
  const openTaskForm = (task?: Task) => {
    if (task) {
      setEditingTask(task);
      setTaskTitle(task.title);
      setTaskDescription(task.description || '');
      setTaskStatus(task.status);
      setTaskPriority(task.priority);
    } else {
      setEditingTask(null);
      setTaskTitle('');
      setTaskDescription('');
      setTaskStatus('Todo');
      setTaskPriority('Med');
    }
    setShowTaskForm(true);
  };

  const closeTaskForm = () => {
    setShowTaskForm(false);
    setEditingTask(null);
    setTaskTitle('');
    setTaskDescription('');
    setTaskStatus('Todo');
    setTaskPriority('Med');
  };

  const handleTaskSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskTitle.trim() || !selectedProjectId) return;
    
    setFormLoading(true);
    try {
      if (editingTask) {
        await api.updateTask(editingTask.id, {
          title: taskTitle.trim(),
          description: taskDescription.trim() || undefined,
          status: taskStatus,
          priority: taskPriority,
        });
      } else {
        await api.createTask(selectedProjectId, {
          title: taskTitle.trim(),
          description: taskDescription.trim() || undefined,
          status: taskStatus,
          priority: taskPriority,
        });
      }
      closeTaskForm();
      loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save task');
    } finally {
      setFormLoading(false);
    }
  };

  const handleStatusChange = async (task: Task, newStatus: Status) => {
    try {
      await api.updateTask(task.id, { status: newStatus });
      loadTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    }
  };

  // Smart Intake handlers
  const handleSmartIntake = async () => {
    if (!intakeText.trim()) return;
    
    setIntakeLoading(true);
    try {
      const result = await api.smartIntake(intakeText.trim());
      setIntakeResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Smart Intake failed');
    } finally {
      setIntakeLoading(false);
    }
  };

  const applyIntakeResult = () => {
    if (intakeResult) {
      setTaskTitle(intakeResult.title);
      setTaskPriority(intakeResult.priority);
      setIntakeText('');
      setIntakeResult(null);
      setShowTaskForm(true);
    }
  };

  // Priority badge class
  const getPriorityClass = (priority: Priority) => {
    switch (priority) {
      case 'High': return 'badge-high';
      case 'Med': return 'badge-med';
      case 'Low': return 'badge-low';
    }
  };

  // Status badge class
  const getStatusClass = (status: Status) => {
    switch (status) {
      case 'Todo': return 'badge-todo';
      case 'In-Progress': return 'badge-progress';
      case 'Done': return 'badge-done';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center" style={{ minHeight: '400px' }}>
        <div className="spinner" />
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <header className="header">
        <h1>✨ Smart Task Tracker</h1>
        <div className="header-actions">
          <button className="btn btn-secondary" onClick={() => setShowProjectForm(true)}>
            + New Project
          </button>
          {selectedProjectId && (
            <button className="btn btn-primary" onClick={() => openTaskForm()}>
              + Add Task
            </button>
          )}
        </div>
      </header>

      {/* Error Message */}
      {error && (
        <div className="message message-error">
          {error}
          <button 
            className="btn btn-ghost btn-sm" 
            onClick={() => setError(null)}
            style={{ marginLeft: '12px' }}
          >
            ✕
          </button>
        </div>
      )}

      {/* Main Content */}
      <div className="main-layout">
        {/* Left: Task List */}
        <div>
          {/* Project Selector */}
          {projects.length > 0 && (
            <div className="project-selector">
              <label className="form-label" style={{ margin: 0 }}>Project:</label>
              <select
                className="form-select"
                value={selectedProjectId || ''}
                onChange={(e) => setSelectedProjectId(Number(e.target.value))}
              >
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Status Filter */}
          {selectedProjectId && (
            <div className="filter-tabs" style={{ marginBottom: '24px' }}>
              {STATUS_OPTIONS.map((status) => (
                <button
                  key={status}
                  className={`filter-tab ${statusFilter === status ? 'active' : ''}`}
                  onClick={() => setStatusFilter(status)}
                >
                  {status}
                </button>
              ))}
            </div>
          )}

          {/* Task List */}
          {!selectedProjectId ? (
            <div className="empty-state">
              <div className="empty-state-icon">📁</div>
              <p className="empty-state-text">No projects yet</p>
              <p className="empty-state-hint">Create a project to get started</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="empty-state">
              <div className="empty-state-icon">📋</div>
              <p className="empty-state-text">No tasks found</p>
              <p className="empty-state-hint">
                {statusFilter !== 'All' 
                  ? `No ${statusFilter} tasks. Try a different filter.`
                  : 'Add a new task or use Smart Intake'
                }
              </p>
            </div>
          ) : (
            <div className="task-list">
              {tasks.map((task) => (
                <div key={task.id} className="task-item">
                  <div className="task-content">
                    <div className="task-title">{task.title}</div>
                    {task.description && (
                      <div className="task-description">{task.description}</div>
                    )}
                  </div>
                  <div className="task-meta">
                    <select
                      className="form-select"
                      value={task.status}
                      onChange={(e) => handleStatusChange(task, e.target.value as Status)}
                      style={{ width: 'auto', padding: '6px 32px 6px 10px', fontSize: '0.8rem' }}
                    >
                      <option value="Todo">Todo</option>
                      <option value="In-Progress">In Progress</option>
                      <option value="Done">Done</option>
                    </select>
                    <span className={`badge ${getPriorityClass(task.priority)}`}>
                      {task.priority}
                    </span>
                    <button 
                      className="btn btn-ghost btn-sm"
                      onClick={() => openTaskForm(task)}
                    >
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Right: Smart Intake */}
        <div>
          <div className="intake-section">
            <div className="intake-header">
              <div className="intake-icon">🤖</div>
              <div>
                <div className="intake-title">Smart Intake</div>
                <div className="intake-subtitle">Paste text to auto-generate task details</div>
              </div>
            </div>
            
            <div className="form-group" style={{ marginBottom: '12px' }}>
              <textarea
                className="form-textarea"
                placeholder="Paste an email, message, or description here...&#10;&#10;Example: 'I need to urgently fix the login bug before the deadline tomorrow!'"
                value={intakeText}
                onChange={(e) => setIntakeText(e.target.value)}
                rows={4}
              />
            </div>
            
            <button
              className="btn btn-primary"
              onClick={handleSmartIntake}
              disabled={!intakeText.trim() || intakeLoading}
              style={{ width: '100%' }}
            >
              {intakeLoading ? (
                <>
                  <div className="spinner" /> Analyzing...
                </>
              ) : (
                '✨ Analyze Text'
              )}
            </button>
            
            {intakeResult && (
              <div className="intake-result">
                <div style={{ marginBottom: '12px' }}>
                  <div className="intake-result-label">Suggested Title</div>
                  <div className="intake-result-value">{intakeResult.title}</div>
                </div>
                <div style={{ marginBottom: '16px' }}>
                  <div className="intake-result-label">Detected Priority</div>
                  <span className={`badge ${getPriorityClass(intakeResult.priority)}`}>
                    {intakeResult.priority}
                  </span>
                </div>
                <button
                  className="btn btn-primary"
                  onClick={applyIntakeResult}
                  style={{ width: '100%' }}
                >
                  Create Task with These Details
                </button>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Task Form Modal */}
      {showTaskForm && (
        <div className="modal-overlay" onClick={closeTaskForm}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">
                {editingTask ? 'Edit Task' : 'Create New Task'}
              </h2>
              <button className="modal-close" onClick={closeTaskForm}>✕</button>
            </div>
            
            <form onSubmit={handleTaskSubmit}>
              <div className="form-group">
                <label className="form-label">Title</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="What needs to be done?"
                  value={taskTitle}
                  onChange={(e) => setTaskTitle(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">Description (optional)</label>
                <textarea
                  className="form-textarea"
                  placeholder="Add more details..."
                  value={taskDescription}
                  onChange={(e) => setTaskDescription(e.target.value)}
                  rows={3}
                />
              </div>
              
              <div className="grid grid-2">
                <div className="form-group">
                  <label className="form-label">Status</label>
                  <select
                    className="form-select"
                    value={taskStatus}
                    onChange={(e) => setTaskStatus(e.target.value as Status)}
                  >
                    <option value="Todo">Todo</option>
                    <option value="In-Progress">In Progress</option>
                    <option value="Done">Done</option>
                  </select>
                </div>
                
                <div className="form-group">
                  <label className="form-label">Priority</label>
                  <select
                    className="form-select"
                    value={taskPriority}
                    onChange={(e) => setTaskPriority(e.target.value as Priority)}
                  >
                    <option value="Low">Low</option>
                    <option value="Med">Medium</option>
                    <option value="High">High</option>
                  </select>
                </div>
              </div>
              
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={closeTaskForm}>
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={formLoading || !taskTitle.trim()}
                >
                  {formLoading ? (
                    <>
                      <div className="spinner" /> Saving...
                    </>
                  ) : editingTask ? (
                    'Save Changes'
                  ) : (
                    'Create Task'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Project Form Modal */}
      {showProjectForm && (
        <div className="modal-overlay" onClick={() => setShowProjectForm(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2 className="modal-title">Create New Project</h2>
              <button className="modal-close" onClick={() => setShowProjectForm(false)}>✕</button>
            </div>
            
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label className="form-label">Project Name</label>
                <input
                  type="text"
                  className="form-input"
                  placeholder="e.g., Website Redesign, Q1 Goals..."
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  required
                  autoFocus
                />
              </div>
              
              <div className="modal-footer">
                <button 
                  type="button" 
                  className="btn btn-secondary" 
                  onClick={() => setShowProjectForm(false)}
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="btn btn-primary"
                  disabled={!newProjectName.trim()}
                >
                  Create Project
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
