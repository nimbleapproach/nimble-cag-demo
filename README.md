# Bella Terra CAG System

A Context Augmentation Generation (CAG) system for the Bella Terra restaurant, providing intelligent menu recommendations and information through AI-powered agents.

## 🏗️ Architecture

The system is structured into three main components:

### 📁 Directory Structure

```
nimble-cag-demo/
├── api/                    # FastAPI backend service
│   ├── main.py            # API entry point
│   ├── Dockerfile         # API container configuration
│   ├── requirements.txt   # API dependencies
│   └── app/               # API application modules
│       ├── models.py      # Pydantic models
│       ├── routes/        # API endpoints
│       ├── services/      # Business logic services
│       └── middleware/    # Middleware components
├── cag/                   # CAG system library
│   ├── requirements.txt   # CAG dependencies
│   ├── core/              # Core CAG components
│   ├── agents/            # CrewAI agents
│   ├── tasks/             # Agent tasks
│   └── utils/             # Utility functions
├── db_populator/          # Database population service
│   ├── main.py           # Database populator entry point
│   ├── Dockerfile        # Database populator container
│   ├── requirements.txt  # Database dependencies
│   ├── parsers/          # Menu parsing logic
│   └── database/         # Database operations
├── frontend/             # Next.js frontend
│   ├── Dockerfile        # Frontend container configuration
│   ├── package.json      # Frontend dependencies
│   └── src/              # Frontend source code
├── data/                 # Restaurant knowledge base
├── BellaTerra/           # Menu files
├── chroma_db/            # Vector store data
└── docker-compose.yml    # Service orchestration
```

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose
- OpenAI API key
- Node.js (for frontend development)

### 1. Environment Setup

Create a `.env` file in the root directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 2. Start the Full Stack

```bash
# Make the start script executable
chmod +x start_full_stack.sh

# Start all services
./start_full_stack.sh
```

This will start:
- **Database**: PostgreSQL with Bella Terra menu data
- **API**: FastAPI backend with CAG system integration
- **Frontend**: Next.js web interface

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🐳 Docker Deployment

### Full Stack with Docker Compose

```bash
# Build and start all services
docker-compose up --build

# Run in background
docker-compose up -d --build
```

### Individual Services

```bash
# Start only the database
docker-compose up db

# Start database and API
docker-compose up db api

# Start database and populate it
docker-compose up db db-populator
```

## 🔧 Development

### API Development

```bash
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### CAG System Development

```bash
cd cag
pip install -r requirements.txt
python -c "from core.cag_system import CAGSystem; cag = CAGSystem()"
```

### Database Population

```bash
cd db_populator
pip install -r requirements.txt
python main.py
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## 🧠 CAG System Components

### Agents

- **Context Analyst**: Analyzes queries and determines if SQL data is needed
- **SQL Query Agent**: Executes database queries for structured data
- **Context Augmenter**: Enhances context with additional insights
- **Response Generator**: Creates comprehensive responses

### Tasks

- SQL query determination and execution
- Context analysis and augmentation
- Response generation with enhanced insights

### Vector Store

- ChromaDB for semantic search
- OpenAI embeddings for document retrieval
- Automatic markdown processing and chunking

## 📊 Database Schema

The system uses PostgreSQL with the following main table:

```sql
CREATE TABLE menu_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(100),
    is_vegetarian BOOLEAN DEFAULT FALSE,
    is_vegan BOOLEAN DEFAULT FALSE,
    is_gluten_free BOOLEAN DEFAULT FALSE,
    properties JSONB
);
```

## 🔌 API Endpoints

### Query Processing

- `POST /api/query` - Synchronous query processing
- `POST /api/query/async` - Asynchronous query processing
- `GET /api/jobs/{job_id}` - Check async job status

### Health & Status

- `GET /` - Basic health check
- `GET /health` - Detailed health status

### WebSocket

- `WS /api/ws/query` - Real-time query processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
