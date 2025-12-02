# Lexiconnect Development Setup Guide

This guide provides detailed instructions for setting up a development environment for Lexiconnect.

## Prerequisites

### Required Software

- **Python**: 3.11 or higher
  - Check version: `python --version`
  - Download: https://www.python.org/downloads/

- **Node.js**: 18 or higher
  - Check version: `node --version`
  - Download: https://nodejs.org/

- **Docker** and **Docker Compose**
  - Docker Desktop: https://www.docker.com/products/docker-desktop
  - Verify: `docker --version` and `docker-compose --version`

- **Git**: For version control
  - Download: https://git-scm.com/downloads

### Optional (for full deployment)

- **Google Cloud SDK**: For GCP deployment
- **Terraform**: For infrastructure as code
- **Vercel CLI**: For frontend deployment

## Quick Start (Recommended)

The fastest way to get started is using the provided script:

```bash
# Clone the repository
git clone <repository-url>
cd Lexiconnect

# Start all services
./start-free.sh
```

This will start:
- Backend API at `http://localhost:8000`
- Frontend at `http://localhost:3000`
- Neo4j at `bolt://localhost:7687`
- Neo4j Browser at `http://localhost:7474`

## Manual Setup

### Step 1: Clone Repository

```bash
git clone <repository-url>
cd Lexiconnect
```

### Step 2: Backend Setup

#### 2.1 Create Virtual Environment

```bash
cd backend
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

#### 2.2 Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 2.3 Configure Environment Variables

```bash
# Copy example environment file
cp env.example .env

# Edit .env with your settings
# Minimum required:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
SECRET_KEY=your-secret-key-here
```

#### 2.4 Start Neo4j (if not using Docker)

If you're not using Docker Compose, you'll need to start Neo4j separately:

```bash
# Using Docker
docker run -d \
  --name neo4j \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Or install Neo4j locally
# See: https://neo4j.com/docs/operations-manual/current/installation/
```

#### 2.5 Initialize Database Schema

```bash
# Apply schema
./apply-schema.sh

# Or manually:
# Connect to Neo4j Browser at http://localhost:7474
# Run the contents of backend/app/migrations/neo4j/schema.cypher
```

#### 2.6 Run Backend

```bash
# Development mode (with auto-reload)
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Verify backend is running:
- API: http://localhost:8000
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Step 3: Frontend Setup

#### 3.1 Install Dependencies

```bash
cd frontend
npm install
```

#### 3.2 Configure Environment Variables

```bash
# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### 3.3 Run Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

### Step 4: Verify Installation

1. **Backend Health Check**
   ```bash
   curl http://localhost:8000/health
   # Should return: {"status":"healthy","service":"lexiconnect-api"}
   ```

2. **Frontend Access**
   - Open browser to `http://localhost:3000`
   - Should see the Lexiconnect interface

3. **Neo4j Browser**
   - Open `http://localhost:7474`
   - Login with credentials from `.env`
   - Run: `MATCH (n) RETURN n LIMIT 25`

## Docker Setup (Alternative)

### Using Docker Compose

```bash
# From project root
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Using Free Tier Docker Compose

```bash
# Uses free tier configuration (no GCP required)
docker-compose -f docker-compose.free.yml up -d
```

## Development Workflow

### Backend Development

1. **Make code changes** in `backend/app/`
2. **Backend auto-reloads** (if using `--reload` flag)
3. **Test changes** via API or tests

### Frontend Development

1. **Make code changes** in `frontend/app/`
2. **Frontend hot-reloads** automatically
3. **See changes** in browser immediately

### Database Development

1. **Connect to Neo4j Browser**: `http://localhost:7474`
2. **Run Cypher queries** to inspect data
3. **Use schema migration** for structure changes

## IDE Setup

### VS Code (Recommended)

**Extensions:**
- Python
- Pylance
- ESLint
- Prettier
- Docker

**Settings** (`.vscode/settings.json`):
```json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.linting.enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### PyCharm

1. Open project root
2. Configure Python interpreter: `backend/venv/bin/python`
3. Mark `backend/` as sources root
4. Configure Neo4j data source (optional)

## Environment Variables Reference

### Backend (.env)

```env
# Environment
ENVIRONMENT=development
DEBUG=True

# Neo4j Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# JWT
SECRET_KEY=your-super-secret-jwt-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALGORITHM=HS256

# Google Cloud Platform (optional)
GCP_PROJECT_ID=your-gcp-project-id
GCP_SERVICE_ACCOUNT_FILE=/app/credentials/service-account.json
GCS_BUCKET_NAME=your-bucket-name
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Common Issues and Solutions

### Issue: Neo4j Connection Failed

**Symptoms:**
- Backend can't connect to Neo4j
- Error: "Unable to connect to Neo4j"

**Solutions:**
1. Check Neo4j is running: `docker ps | grep neo4j`
2. Verify connection string: `bolt://localhost:7687`
3. Check credentials in `.env`
4. Test connection: `cypher-shell -u neo4j -p password`

### Issue: Port Already in Use

**Symptoms:**
- Error: "Address already in use"

**Solutions:**
1. Find process using port:
   ```bash
   # Linux/Mac
   lsof -i :8000
   # Windows
   netstat -ano | findstr :8000
   ```
2. Kill process or change port in configuration

### Issue: Python Dependencies Fail to Install

**Symptoms:**
- `pip install` errors
- Missing system dependencies

**Solutions:**
1. Update pip: `pip install --upgrade pip`
2. Install system dependencies (Linux):
   ```bash
   sudo apt-get update
   sudo apt-get install python3-dev gcc
   ```
3. Use virtual environment (recommended)

### Issue: Frontend Can't Connect to Backend

**Symptoms:**
- API calls fail
- CORS errors

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `NEXT_PUBLIC_API_URL` in `.env.local`
3. Verify CORS settings in `backend/app/core/config.py`
4. Check browser console for errors

### Issue: Database Schema Not Applied

**Symptoms:**
- Queries fail
- Missing constraints

**Solutions:**
1. Run schema migration:
   ```bash
   ./apply-schema.sh
   ```
2. Or manually run `backend/app/migrations/neo4j/schema.cypher` in Neo4j Browser

## Testing Setup

### Run Tests

```bash
cd backend

# Install test dependencies (if separate)
pip install pytest pytest-cov

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=app tests/
```

### Test Database

Tests use a separate test database or mocked connections. See [Testing Guide](../backend/tests/TESTS_README.md).

## Next Steps

After setup:

1. **Read the code**: Start with `backend/main.py` and `frontend/app/page.tsx`
2. **Explore API**: Visit `http://localhost:8000/docs`
3. **Upload test data**: Use a sample `.flextext` file
4. **Read documentation**: See [Developer Guide](./README.md)

## Additional Resources

- [Architecture Guide](./architecture.md)
- [Code Structure](./code-structure.md)
- [API Reference](./api-reference.md)
- [Main README](../../README.md)

---

**Troubleshooting**: If you encounter issues not covered here, check:
- Docker logs: `docker-compose logs`
- Backend logs: Console output or log files
- Browser console: For frontend errors
- Neo4j Browser: For database issues

