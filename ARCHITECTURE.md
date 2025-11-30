# 🏗️ PM-AI System Architecture & Data Flow

## System Architecture Diagram

```mermaid
graph TB
    subgraph "🎨 FRONTEND - React App :5173"
        UI[👤 User Interface]
        Kanban[📋 Kanban Board<br/>Drag & Drop Tasks]
        Chat[💬 AI Agent Chat<br/>Natural Language Input]
        Dashboard[📊 Dashboard<br/>Project Overview]
        Projects[📁 Project Management<br/>CRUD Operations]
    end

    subgraph "🔧 BACKEND - FastAPI :8000"
        Gateway[🚪 API Gateway<br/>CORS & Routing]
        
        subgraph "Route Handlers"
            AgentRoute[🤖 /agent/execute<br/>AI Commands]
            ProjectRoute[📁 /projects/*<br/>Project CRUD]
            TaskRoute[✅ /tasks/*<br/>Task CRUD]
            SprintRoute[🏃 /sprints/*<br/>Sprint CRUD]
            UserRoute[👥 /users/*<br/>Team Management]
        end
    end

    subgraph "🧠 AI AGENT SYSTEM"
        IntentDetect{🎯 Intent Detection<br/>What does user want?}
        
        subgraph "Agent Service Layer"
            TaskGen[📝 Task Generation<br/>generate_task_list]
            ProjectGen[🗂️ Project Planning<br/>generate_project_plan]
            TaskMod[✏️ Task Modification<br/>modify_task]
            HealthCheck[💊 Health Monitor<br/>get_project_health]
            NLResponse[💬 NL Response Gen<br/>Humanized Messages]
        end
        
        subgraph "Prompts Engine"
            Prompts[📜 Prompt Templates<br/>System Instructions]
        end
        
        subgraph "Agent Tools"
            CreateTask[➕ create_task]
            UpdateTask[🔄 update_task]
            DeleteTask[🗑️ delete_task]
            GetTasks[📥 get_tasks]
        end
    end

    subgraph "☁️ EXTERNAL SERVICES"
        LLM[🤖 OpenRouter API<br/>Grok / Llama / GPT<br/>claude / etc.]
    end

    subgraph "🗄️ DATABASE - PostgreSQL"
        DB[(💾 Database)]
        Tables[📊 Tables:<br/>• projects<br/>• tasks<br/>• sprints<br/>• users<br/>• team_members]
    end

    %% User Interactions
    UI --> Gateway
    Kanban --> Gateway
    Chat --> Gateway
    Dashboard --> Gateway
    Projects --> Gateway

    %% API Gateway Routing
    Gateway --> AgentRoute
    Gateway --> ProjectRoute
    Gateway --> TaskRoute
    Gateway --> SprintRoute
    Gateway --> UserRoute

    %% Agent Route Flow
    AgentRoute -->|Natural Language| IntentDetect
    
    %% Intent Detection Routes
    IntentDetect -->|"Project Creation"| ProjectGen
    IntentDetect -->|"Task Creation"| TaskGen
    IntentDetect -->|"Update/Delete"| TaskMod
    IntentDetect -->|"Health Check"| HealthCheck

    %% Service Layer to LLM
    ProjectGen -->|Prompt| LLM
    TaskGen -->|Prompt| LLM
    TaskMod -->|Prompt| LLM
    LLM -->|JSON Plan| ProjectGen
    LLM -->|JSON Tasks| TaskGen
    LLM -->|JSON Action| TaskMod

    %% Prompts Engine
    Prompts -.provides.-> ProjectGen
    Prompts -.provides.-> TaskGen
    Prompts -.provides.-> TaskMod
    Prompts -.provides.-> NLResponse

    %% Tools Execution
    ProjectGen --> CreateTask
    TaskGen --> CreateTask
    TaskMod --> UpdateTask
    TaskMod --> DeleteTask
    HealthCheck --> GetTasks

    %% Natural Language Response Generation
    ProjectGen --> NLResponse
    TaskGen --> NLResponse
    TaskMod --> NLResponse
    HealthCheck --> NLResponse
    NLResponse -->|Prompt| LLM
    LLM -->|Human Message| NLResponse

    %% Database Operations
    CreateTask --> DB
    UpdateTask --> DB
    DeleteTask --> DB
    GetTasks --> DB
    ProjectRoute --> DB
    TaskRoute --> DB
    SprintRoute --> DB
    UserRoute --> DB

    %% Response Flow
    NLResponse --> AgentRoute
    AgentRoute --> Gateway
    ProjectRoute --> Gateway
    TaskRoute --> Gateway
    Gateway --> UI

    %% Styling
    classDef frontend fill:#E3F2FD,stroke:#1976D2,stroke-width:3px,color:#000
    classDef backend fill:#E8F5E9,stroke:#388E3C,stroke-width:3px,color:#000
    classDef agent fill:#FFF3E0,stroke:#F57C00,stroke-width:3px,color:#000
    classDef database fill:#E1F5FE,stroke:#0288D1,stroke-width:3px,color:#000
    classDef external fill:#F3E5F5,stroke:#7B1FA2,stroke-width:3px,color:#000
    
    class UI,Kanban,Chat,Dashboard,Projects frontend
    class Gateway,AgentRoute,ProjectRoute,TaskRoute,SprintRoute,UserRoute backend
    class IntentDetect,TaskGen,ProjectGen,TaskMod,HealthCheck,NLResponse,Prompts,CreateTask,UpdateTask,DeleteTask,GetTasks agent
    class DB,Tables database
    class LLM external
```

## 📊 Detailed Data Flow

### 1️⃣ **User Creates Project via AI Chat**

```
User Input: "Create an e-commerce website with authentication and payment"
    ↓
Frontend (Chat) → POST /agent/execute
    ↓
Backend (AgentRoute) → Intent Detection → "Project Creation"
    ↓
Agent Service → generate_project_plan()
    ↓
Prompts Engine → Formats PLAN_GENERATION_PROMPT
    ↓
OpenRouter LLM → Returns JSON: {project_name, tasks[], milestones[]}
    ↓
Agent Tools → create_project() → create_task() (loop)
    ↓
PostgreSQL → INSERT INTO projects, tasks
    ↓
NL Response Gen → generate_natural_language_response()
    ↓
OpenRouter LLM → "I've created your e-commerce project with 12 tasks..."
    ↓
Backend → JSON Response with humanized message
    ↓
Frontend → Displays success message & updates Kanban board
```

### 2️⃣ **User Creates Task with Role Assignment**

```
User Input: "Create a task to optimize database queries"
    ↓
Intent Detection → "Single Task Creation"
    ↓
generate_task_list() → Checks team_members status
    ↓
LLM → Returns: {
  name: "Optimize Database Queries",
  assignee: "MK",
  assignment_reasoning: "Mike is the Backend Dev..."
}
    ↓
create_task() → INSERT INTO tasks
    ↓
NL Response → "I've assigned this to Mike since he's our backend expert..."
```

### 3️⃣ **User Updates Task via Natural Language**

```
User Input: "Move Login Page to high priority"
    ↓
Intent Detection → "Task Modification"
    ↓
modify_task() → LLM interprets: {action: "update", target: "login page"}
    ↓
get_tasks() → Searches for matching task
    ↓
update_task() → UPDATE tasks SET priority='high'
    ↓
NL Response → "I've updated the Login Page to high priority..."
```

### 4️⃣ **User Checks Project Health**

```
User Input: "How is the project doing?"
    ↓
Intent Detection → "Project Health"
    ↓
get_project_health() → Calculates metrics
    ↓
Returns: {
  total_tasks: 40,
  completion_rate: 30,
  overloaded_members: ["Alice"],
  burnout_risk: "Medium"
}
    ↓
NL Response → "The project is 30% complete. I'm concerned about Alice 
               having 6 active tasks. Consider reassigning to Bob..."
```

### 5️⃣ **User Drags Task on Kanban Board**

```
User Action: Drag task to "In Progress"
    ↓
Frontend → PUT /tasks/{id} {status: "In Progress"}
    ↓
Backend (TaskRoute) → Direct database update
    ↓
PostgreSQL → UPDATE tasks SET status='In Progress'
    ↓
Backend → JSON Response
    ↓
Frontend → Updates UI immediately
```

## 🔄 Key Integration Points

### Frontend ↔ Backend
- **Protocol**: REST API over HTTP
- **Format**: JSON
- **Authentication**: (To be implemented)
- **Real-time**: Polling (WebSocket planned)

### Backend ↔ AI Agent
- **Trigger**: `/agent/execute` endpoint
- **Input**: Natural language string + context
- **Output**: Structured response with humanized message
- **Error Handling**: Fallback messages on LLM failure

### AI Agent ↔ OpenRouter
- **Client**: AsyncOpenAI (async HTTP)
- **Models**: Configurable via `OPENROUTER_MODEL` env var
- **Temperature**: 0.1-0.7 depending on task type
- **Retry Logic**: Automatic on network errors

### Agent Tools ↔ Database
- **ORM**: SQLAlchemy (async)
- **Connection**: asyncpg
- **Transactions**: Automatic commit/rollback
- **Schema**: Auto-created on startup

## 🎯 Agent Intent Detection Logic

The agent uses keyword matching to route requests:

| **Intent** | **Keywords** | **Handler** |
|------------|--------------|-------------|
| Project Creation | "create project", "new project", "build a" | `generate_project_plan()` |
| Bulk Task Creation | "create tasks", "add tasks" + project_id | `generate_task_list()` |
| Single Task Creation | "create a task", "add a task" | `generate_task_list()` |
| Task Modification | "update", "change", "move", "delete" | `modify_task()` |
| Project Health | "status", "health", "how is", "progress" | `get_project_health()` |
| Default | Anything else | `generate_project_plan()` |

## 🛡️ Error Handling Flow

```mermaid
graph LR
    Request[API Request] --> Validate{Valid?}
    Validate -->|No| Error400[400 Bad Request]
    Validate -->|Yes| AgentEnabled{Agent<br/>Enabled?}
    AgentEnabled -->|No| Error503[503 Service Unavailable]
    AgentEnabled -->|Yes| LLMCall[Call LLM]
    LLMCall --> LLMSuccess{Success?}
    LLMSuccess -->|No| ErrorLog[Log Error] --> Fallback[Fallback Message]
    LLMSuccess -->|Yes| DBWrite[Write to DB]
    DBWrite --> DBSuccess{Success?}
    DBSuccess -->|No| Error500[500 Internal Error]
    DBSuccess -->|Yes| Response200[200 OK + NL Response]
    
    style Error400 fill:#ffcdd2
    style Error503 fill:#ffcdd2
    style Error500 fill:#ffcdd2
    style Response200 fill:#c8e6c9
```

## 📈 Performance Characteristics

| **Operation** | **Avg Time** | **Bottleneck** |
|---------------|--------------|----------------|
| Simple Task Create | ~2s | LLM API call |
| Project Generation | ~5s | LLM + DB writes |
| Kanban Drag-Drop | <100ms | Local only |
| Health Check | ~1s | DB query |
| NL Response Gen | ~1-2s | Extra LLM call |

---

**Architecture Philosophy**: 
- **Separation of Concerns**: Frontend, Backend, AI Agent are loosely coupled
- **Async First**: All I/O operations are non-blocking
- **Fail-Safe**: Graceful degradation when AI is unavailable
- **Human-Centric**: AI speaks like a colleague, not a machine
