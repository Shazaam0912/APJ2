# 🚀 PM-AI: Intelligent Project Management System

An advanced project management platform powered by AI that acts as your **Compassionate Head of Engineering**, automating project planning, task creation, team assignment, and health monitoring.

## ✨ Key Features

### 🤖 AI-Powered Project Manager
- **Natural Language Project Creation**: Describe your project in plain English, and the AI generates a complete project plan with tasks, milestones, and sprints
- **Intelligent Task Generation**: Creates detailed, actionable tasks with role-based assignments
- **Smart Subtasking**: Automatically breaks down complex tasks into manageable subtasks
- **Role-Based Assignment**: Assigns tasks to the right team members based on their skills and expertise
- **Humanized Responses**: The agent communicates like a human colleague, not a robot

### 📊 Project Management Core
- **Kanban Board**: Visual task management with drag-and-drop functionality
- **Sprint Planning**: Organize work into sprints with goals and timelines
- **Task Lifecycle**: Full CRUD operations on tasks (Create, Read, Update, Delete)
- **Priority Management**: Set and visualize task priorities (High, Medium, Low)
- **Team Collaboration**: Assign tasks to team members and track progress

### 🧠 Advanced Agent Capabilities
- **HRM Logic**: Respects team member workload and status (Online/Busy/Offline)
- **Burnout Prevention**: Avoids overloading busy team members and suggests redistribution
- **Project Health Monitoring**: Real-time insights on completion rate, team workload, and burnout risk
- **Task Modification**: Update or delete tasks via natural language commands
- **Multi-Turn Conversations**: Remembers context and asks clarifying questions when needed

## 🏗️ Architecture

```mermaid
graph TB
    subgraph "Frontend (React + TypeScript)"
        UI[User Interface]
        Kanban[Kanban Board]
        Chat[AI Agent Chat]
        Dashboard[Dashboard]
    end

    subgraph "Backend (FastAPI + Python)"
        API[REST API]
        Routes[Route Handlers]
        DB[PostgreSQL Database]
    end

    subgraph "AI Agent Layer"
        AgentAPI[Agent API /agent/execute]
        Service[Agent Service]
        Tools[Agent Tools]
        Prompts[AI Prompts]
        LLM[OpenRouter LLM<br/>Grok/Llama/etc]
    end

    UI --> API
    Kanban --> API
    Chat --> AgentAPI
    Dashboard --> API
    
    API --> Routes
    Routes --> DB
    
    AgentAPI --> Service
    Service --> Tools
    Service --> Prompts
    Service --> LLM
    Tools --> DB
    
    LLM -.generates.-> Service
    Service -.returns.-> AgentAPI
    
    style AgentAPI fill:#4CAF50
    style Service fill:#4CAF50
    style LLM fill:#FF9800
    style DB fill:#2196F3
```

### System Flow

1. **User Input**: User interacts with the frontend (chat, Kanban, dashboard)
2. **API Layer**: Frontend sends HTTP requests to FastAPI backend
3. **Agent Processing**: 
   - Agent API receives natural language commands
   - Agent Service interprets intent and generates structured plans
   - OpenRouter LLM processes prompts and returns JSON
   - Agent Tools execute database operations
4. **Database**: PostgreSQL stores projects, tasks, sprints, and team data
5. **Response**: Backend returns data to frontend with humanized messages

## 🛠️ Tech Stack

### Frontend
- **React 18** with TypeScript
- **React Router** for navigation
- **Axios** for HTTP requests
- **CSS Modules** for styling

### Backend
- **FastAPI** (Python 3.11+)
- **PostgreSQL** database
- **SQLAlchemy** ORM
- **AsyncPG** for async database access
- **Pydantic** for data validation

### AI Layer
- **OpenRouter** (OpenAI-compatible API)
- **Supported Models**: Grok, Llama, GPT, Claude, etc.
- **Async OpenAI Client** for non-blocking LLM calls

## 📋 Prerequisites

- **Python 3.11+**
- **Node.js 18+** and npm
- **PostgreSQL 14+**
- **OpenRouter API Key** (sign up at [openrouter.ai](https://openrouter.ai))

## ⚙️ Setup Instructions

### 1. Clone the Repository

```bash
cd "Project management demo"
```

### 2. Backend Setup

#### Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

#### Configure Environment Variables
Create a `.env` file in the `backend` directory:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/pm_ai_db
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_MODEL=x-ai/grok-beta:free
```

**Environment Variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY`: Your OpenRouter API key ([Get one here](https://openrouter.ai/keys))
- `OPENROUTER_MODEL`: AI model to use (e.g., `x-ai/grok-beta:free`, `meta-llama/llama-3.1-8b-instruct:free`)

#### Setup Database
```bash
# Create PostgreSQL database
createdb pm_ai_db

# The database schema will be automatically created on first run
```

#### Run Backend Server
```bash
# From the backend directory
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`  
API docs: `http://localhost:8000/docs`

### 3. Frontend Setup

#### Install Dependencies
```bash
cd frontend-rebuild
npm install
```

#### Run Frontend
```bash
npm run dev
```

Frontend will be available at: `http://localhost:5173`

## 🎯 Usage Guide

### Creating a Project with AI

1. Navigate to the **AI Agent Chat** page
2. Type a natural language command:
   ```
   Create a project to build an e-commerce website with user authentication, 
   product catalog, shopping cart, and payment integration
   ```
3. The AI will:
   - Generate a project plan with milestones
   - Create tasks with descriptions and priorities
   - Assign tasks to team members based on roles
   - Provide humanized feedback

### Managing Tasks

**Via Kanban Board:**
- Drag and drop tasks between columns (To Do, In Progress, Done)
- Click on tasks to view details
- Edit task properties (title, description, priority, assignee)

**Via AI Agent:**
```
Update task "Login Page" to high priority and assign to Alice
```
```
Delete the task "Old Authentication System"
```

### Checking Project Health

**Via AI Agent:**
```
How is the project doing?
```

**Response:**
```
The project is currently 30% complete with 12 tasks remaining. 
I noticed Alice is handling 6 active tasks, which might be overloading her. 
Consider reassigning 2-3 tasks to Bob to balance the workload.
```

## 📁 Project Structure

```
Project management demo/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── agent/             # AI Agent Layer
│   │   │   ├── __init__.py    # OpenRouter client setup
│   │   │   ├── agent_service.py   # Core agent logic
│   │   │   ├── tools.py       # Database operation tools
│   │   │   └── prompts.py     # LLM prompts
│   │   ├── routes/            # API endpoints
│   │   │   ├── agent.py       # Agent API (/agent/execute)
│   │   │   ├── projects.py    # Project CRUD
│   │   │   ├── tasks.py       # Task CRUD
│   │   │   ├── sprints.py     # Sprint CRUD
│   │   │   └── users.py       # User/Team management
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── database.py        # Database connection
│   │   └── main.py            # FastAPI app entry point
│   ├── tests/                 # Automated tests
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
│
├── frontend-rebuild/          # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   │   ├── kanban/        # Kanban board
│   │   │   ├── agent/         # AI chat interface
│   │   │   └── layout/        # Layout components
│   │   ├── pages/             # Page components
│   │   ├── services/          # API services
│   │   └── App.tsx            # Root component
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
└── README.md                  # This file
```

## 🧪 Testing

### Run Agent Feature Tests
```bash
cd backend
python3 tests/test_agent_features.py
```

This will verify:
- ✅ Project creation
- ✅ Role-based assignment
- ✅ HRM logic (busy status handling)
- ✅ Intelligent subtasking
- ✅ Task update/delete
- ✅ Project health monitoring

## 🔑 API Endpoints

### Agent API
- `POST /agent/execute` - Execute AI agent commands

### Projects
- `GET /projects` - List all projects
- `POST /projects` - Create project
- `GET /projects/{id}` - Get project details
- `PUT /projects/{id}` - Update project
- `DELETE /projects/{id}` - Delete project

### Tasks
- `GET /tasks` - List all tasks
- `POST /tasks` - Create task
- `PUT /tasks/{id}` - Update task
- `DELETE /tasks/{id}` - Delete task

### Sprints
- `GET /sprints` - List sprints
- `POST /sprints` - Create sprint

### Users
- `GET /users` - List team members
- `POST /users` - Add team member

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **OpenRouter** for providing unified LLM API access
- **FastAPI** for the excellent async Python framework
- **React** for the powerful frontend library

## 📧 Support

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ by the KERDS Team**
