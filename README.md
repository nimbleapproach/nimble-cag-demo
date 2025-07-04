# CAG_Demo

This project contains the backend API and frontend UI for the CAG Demo application.

## Getting Started

To get the application running locally using Docker Compose, follow these steps. These commands should be run from the root of the `nimble-cag-demo` directory.

### Prerequisites

Make sure you have Docker Desktop installed and running on your system.

### 1. Set Up Environment Variables

Copy the example environment file and fill in your OpenAI API key:

```bash
cp .env.example .env
# Open .env and add your OPENAI_API_KEY
```

Or create a .env and then add OPENAI_API_KEY=YOUR_KEY 

### 2. Start the Application Stack

This command will build the Docker images (if not already built), create the necessary containers (PostgreSQL database, API, and Frontend), and start all services in detached mode.

```bash
docker compose up --build -d
```

### 3. Access the Application

Once all services are up and running, you can access the application in your browser:

*   **Frontend UI:** `http://localhost:3000`
*   **Backend API:** `http://localhost:8000`

### Stopping the Application

To stop and remove all running containers, networks, and volumes created by Docker Compose:

```bash
docker compose down -v
```

### Viewing Logs

To view real-time logs from all services (useful for debugging):

```bash
docker compose logs -f
```

To view logs from a specific service (e.g., the API):

```bash
docker compose logs -f api
```
