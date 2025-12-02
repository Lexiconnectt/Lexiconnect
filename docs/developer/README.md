# Lexiconnect Developer Guide

Welcome to the Lexiconnect developer documentation! This guide is designed to help developers understand, set up, and contribute to the Lexiconnect project.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Architecture](#architecture)
4. [Development Setup](#development-setup)
5. [Code Structure](#code-structure)
6. [API Reference](#api-reference)
7. [Testing](#testing)
8. [Deployment](#deployment)
9. [Contributing](#contributing)

## Overview

Lexiconnect is a full-stack web application for linguistic documentation and research, built with:

- **Backend**: FastAPI (Python 3.11+) with Neo4j graph database
- **Frontend**: Next.js 14+ (TypeScript) with Tailwind CSS
- **Database**: Neo4j (graph database)
- **Deployment**: Docker, Google Cloud Platform (Cloud Run), Vercel
- **Storage**: Google Cloud Storage (for file uploads)

### Key Features

- Import FLEx (FieldWorks Language Explorer) text files
- Graph-based visualization of linguistic relationships
- Export data in FLEXText XML format
- Interactive search and exploration
- Neo4j graph database for relationship modeling

## Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18 or higher
- **Docker** and **Docker Compose**: For local development
- **Neo4j**: Can run via Docker or use Neo4j AuraDB
- **Git**: For version control

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Lexiconnect
   ```

2. **Start development environment**
   ```bash
   ./start-free.sh
   ```
   This starts:
   - Backend API at `http://localhost:8000`
   - Frontend at `http://localhost:3000`
   - Neo4j at `bolt://localhost:7687`
   - Neo4j Browser at `http://localhost:7474`

3. **Verify installation**
   - Backend health: `http://localhost:8000/health`
   - API docs: `http://localhost:8000/docs`
   - Frontend: `http://localhost:3000`

For detailed setup instructions, see [Setup Guide](./setup.md).

## Architecture

Lexiconnect follows a modern microservices-inspired architecture:

```
┌─────────────┐
│   Frontend  │  Next.js (Vercel)
│  (Next.js)  │
└──────┬──────┘
       │ HTTP/REST
       │
┌──────▼──────┐
│   Backend   │  FastAPI (Cloud Run)
│  (FastAPI)  │
└──────┬──────┘
       │
       │ Cypher Queries
       │
┌──────▼──────┐
│   Database  │  Neo4j
│   (Neo4j)   │
└─────────────┘
```

### Key Components

- **Routers**: Handle HTTP requests and responses
- **Services**: Business logic and data processing
- **Models**: Data structures and validation
- **Parsers**: Import FLEx files
- **Exporters**: Export data in various formats
- **Database**: Neo4j service layer

For detailed architecture information, see [Architecture Guide](./architecture.md).

## Development Setup

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Run backend**
   ```bash
   python main.py
   # Or with uvicorn directly:
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Set up environment variables**
   ```bash
   # Create .env.local
   echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
   ```

4. **Run development server**
   ```bash
   npm run dev
   ```

For complete setup instructions, see [Setup Guide](./setup.md).

## Code Structure

### Backend Structure

```
backend/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── Dockerfile             # Container definition
├── app/
│   ├── core/              # Core configuration
│   │   └── config.py      # Settings and environment
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication
│   │   ├── export.py      # Export endpoints
│   │   ├── languages.py   # Language management
│   │   ├── linguistic.py  # Linguistic data
│   │   └── documentation.py
│   ├── services/          # Business logic
│   │   ├── neo4j_service.py
│   │   ├── export_service.py
│   │   └── export_flextext_service.py
│   ├── models/            # Data models
│   │   └── linguistic.py
│   ├── parsers/           # File parsers
│   │   ├── flextext_parser.py
│   │   └── elan_parser.py
│   ├── exporters/         # Export implementations
│   │   ├── base.py
│   │   ├── flextext_exporter.py
│   │   └── json_exporter.py
│   ├── database.py        # Database connection
│   └── migrations/        # Database migrations
│       └── neo4j/
│           └── schema.cypher
└── tests/                 # Test suite
```

### Frontend Structure

```
frontend/
├── app/                   # Next.js app directory
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home page
│   ├── components/        # React components
│   │   ├── GraphVisualization.tsx
│   │   ├── FileUpload.tsx
│   │   ├── SearchBar.tsx
│   │   └── ...
│   ├── api/               # API routes (if needed)
│   └── upload/            # Upload page
├── package.json
├── next.config.js
└── tailwind.config.js
```

For detailed code structure information, see [Code Structure Guide](./code-structure.md).

## API Reference

The Lexiconnect API is RESTful and follows OpenAPI standards. Key endpoints:

- **Authentication**: `/api/v1/auth/*`
- **Languages**: `/api/v1/languages/*`
- **Documentation**: `/api/v1/docs/*`
- **Linguistic Data**: `/api/v1/linguistic/*`
- **Export**: `/api/v1/export`

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

For complete API documentation, see [API Reference](./api-reference.md).

## Testing

### Running Tests

```bash
# From backend directory
cd backend

# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_neo4j_service.py

# Run with coverage
pytest --cov=app tests/
```

### Test Types

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints
- **Database Tests**: Validate database operations

For detailed testing information, see [Testing Guide](../backend/tests/TESTS_README.md).

## Deployment

### Backend Deployment (Cloud Run)

1. **Build and push container**
   ```bash
   gcloud builds submit --config=gcp/cloudbuild.yaml .
   ```

2. **Deploy with Terraform**
   ```bash
   cd gcp/terraform
   terraform init
   terraform apply
   ```

### Frontend Deployment (Vercel)

1. **Install Vercel CLI**
   ```bash
   npm install -g vercel
   ```

2. **Deploy**
   ```bash
   cd frontend
   vercel
   ```

For detailed deployment instructions, see the main [README.md](../../README.md).

## Contributing

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow code style guidelines
   - Write tests for new features
   - Update documentation

3. **Test your changes**
   ```bash
   # Backend tests
   cd backend && pytest tests/
   
   # Frontend tests (if available)
   cd frontend && npm test
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

5. **Create pull request**

### Code Style

- **Python**: Follow PEP 8, use Black for formatting
- **TypeScript**: Follow ESLint rules, use Prettier
- **Documentation**: Use Markdown, keep it clear and concise

For detailed contributing guidelines, see [Contributing Guide](./contributing.md).

## Additional Resources

- [Architecture Guide](./architecture.md) - Deep dive into system design
- [Setup Guide](./setup.md) - Detailed setup instructions
- [API Reference](./api-reference.md) - Complete API documentation
- [Code Structure](./code-structure.md) - Codebase organization
- [Database Schema](../../DATABASE.md) - Neo4j schema documentation
- [Export System](../export_system.md) - Export system details

## Getting Help

- Check existing documentation
- Review code comments
- Examine test files for usage examples
- Check GitHub issues (if available)

## Project Handoff Notes

This project is being transferred from student development to continued development by the instructor and other developers. Key points:

- All documentation is in the `docs/` directory
- Configuration examples are in `env.example` files
- Database schema is in `backend/app/migrations/neo4j/schema.cypher`
- Tests demonstrate expected behavior
- API documentation is auto-generated at `/docs` endpoint

---

**Last Updated**: Project handoff documentation - 2024

