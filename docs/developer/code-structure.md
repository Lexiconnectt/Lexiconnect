# Lexiconnect Code Structure

This document describes the organization and structure of the Lexiconnect codebase.

## Project Structure

```
Lexiconnect/
├── README.md                    # Main project README
├── DATABASE.md                  # Database schema documentation
├── docker-compose.yml           # Docker Compose configuration
├── docker-compose.free.yml      # Free tier Docker Compose
├── start-free.sh                # Quick start script
├── apply-schema.sh              # Database schema application
│
├── backend/                     # Backend application
│   ├── main.py                  # Application entry point
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Container definition
│   ├── env.example             # Environment variables template
│   │
│   ├── app/                    # Application code
│   │   ├── __init__.py
│   │   ├── core/               # Core configuration
│   │   │   ├── __init__.py
│   │   │   └── config.py       # Settings and environment
│   │   │
│   │   ├── routers/            # API route handlers
│   │   │   ├── __init__.py
│   │   │   ├── auth.py         # Authentication endpoints
│   │   │   ├── export.py       # Export endpoints
│   │   │   ├── languages.py    # Language management
│   │   │   ├── linguistic.py    # Linguistic data operations
│   │   │   └── documentation.py # Documentation entries
│   │   │
│   │   ├── services/           # Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── neo4j_service.py      # Neo4j operations
│   │   │   ├── export_service.py     # Export orchestration
│   │   │   └── export_flextext_service.py # FLEXText export
│   │   │
│   │   ├── models/             # Data models (Pydantic)
│   │   │   ├── __init__.py
│   │   │   └── linguistic.py   # Linguistic data models
│   │   │
│   │   ├── parsers/            # File parsers
│   │   │   ├── flextext_parser.py  # FLEx Text XML parser
│   │   │   └── elan_parser.py      # ELAN file parser
│   │   │
│   │   ├── exporters/          # Export implementations
│   │   │   ├── __init__.py
│   │   │   ├── base.py        # Exporter interface
│   │   │   ├── flextext_exporter.py # FLEXText XML export
│   │   │   └── json_exporter.py    # JSON export
│   │   │
│   │   ├── database.py         # Database connection management
│   │   │
│   │   └── migrations/         # Database migrations
│   │       └── neo4j/
│   │           └── schema.cypher # Neo4j schema definition
│   │
│   └── tests/                  # Test suite
│       ├── TESTS_README.md
│       ├── test_neo4j_service.py
│       ├── test_export_route.py
│       ├── test_export_service.py
│       ├── test_export_flextext_service.py
│       ├── test_json_exporter.py
│       ├── test_graph_edges.py
│       ├── test_upload.py
│       └── validate_database.py
│
├── frontend/                    # Frontend application
│   ├── package.json            # Node.js dependencies
│   ├── next.config.js          # Next.js configuration
│   ├── tailwind.config.js      # Tailwind CSS configuration
│   ├── tsconfig.json           # TypeScript configuration
│   ├── Dockerfile.dev          # Development container
│   ├── vercel.json             # Vercel configuration
│   │
│   └── app/                    # Next.js app directory
│       ├── layout.tsx          # Root layout
│       ├── page.tsx             # Home page
│       ├── globals.css          # Global styles
│       ├── providers.tsx       # Context providers
│       │
│       ├── components/         # React components
│       │   ├── GraphVisualization.tsx
│       │   ├── FileUpload.tsx
│       │   ├── SearchBar.tsx
│       │   ├── NodeDetails.tsx
│       │   ├── Navigation.tsx
│       │   ├── GraphFilters.tsx
│       │   ├── ExportFileTypeModal.tsx
│       │   ├── CorpusStatistics.tsx
│       │   └── DatabaseStatistics.tsx
│       │
│       ├── api/                # API routes (if needed)
│       │   └── v1/
│       │       └── [...slug]/
│       │           └── route.ts
│       │
│       └── upload/             # Upload page
│           └── page.tsx
│
├── docs/                       # Documentation
│   ├── README.md               # Documentation index
│   ├── user/                   # User documentation
│   │   └── README.md
│   ├── developer/             # Developer documentation
│   │   ├── README.md
│   │   ├── architecture.md
│   │   ├── setup.md
│   │   ├── api-reference.md
│   │   ├── code-structure.md
│   │   └── contributing.md
│   ├── export_system.md
│   └── flextext_export_mapping.md
│
└── gcp/                        # Google Cloud Platform configs
    ├── cloudbuild.yaml         # Cloud Build configuration
    └── terraform/              # Infrastructure as code
        ├── main.tf
        ├── variables.tf
        ├── outputs.tf
        └── terraform.tfvars.example
```

## Backend Structure

### Entry Point: `main.py`

- Initializes FastAPI application
- Configures CORS middleware
- Registers routers
- Manages application lifespan (database connections)

### Core Module (`app/core/`)

**`config.py`**: Centralized configuration
- Environment variable management
- Settings class using Pydantic BaseSettings
- CORS, database, JWT, GCP settings

### Routers (`app/routers/`)

Route handlers organized by domain:

- **`auth.py`**: User authentication and registration
- **`export.py`**: Data export endpoints
- **`languages.py`**: Language management CRUD
- **`linguistic.py`**: Linguistic data operations (upload, search, graph)
- **`documentation.py`**: Documentation entry management

**Pattern:**
- FastAPI router with dependency injection
- Pydantic models for request/response validation
- Service layer calls for business logic
- Error handling with HTTPException

### Services (`app/services/`)

Business logic and data operations:

- **`neo4j_service.py`**: Neo4j database operations
  - Graph data retrieval
  - Node and relationship queries
  - Statistics aggregation

- **`export_service.py`**: Export orchestration
  - Coordinates data retrieval and export
  - Handles export format selection

- **`export_flextext_service.py`**: FLEXText-specific export logic

**Pattern:**
- Pure business logic (no HTTP concerns)
- Database session dependency injection
- Error handling and logging

### Models (`app/models/`)

Pydantic models for data validation:

- **`linguistic.py`**: Linguistic data models
  - Request models (Create, Update)
  - Response models
  - Search query models

**Pattern:**
- Separate models for create/update/response
- Field validation and types
- Optional fields with defaults

### Parsers (`app/parsers/`)

File format parsers:

- **`flextext_parser.py`**: FLEx Text XML parser
  - Parses XML structure
  - Creates Neo4j nodes and relationships
  - Handles linguistic hierarchy

- **`elan_parser.py`**: ELAN file parser
  - Parses ELAN annotation files
  - Converts to internal format

**Pattern:**
- File input → Neo4j operations
- Error handling for malformed files
- Statistics generation

### Exporters (`app/exporters/`)

Export format implementations:

- **`base.py`**: Exporter interface/protocol
  - Defines exporter contract
  - Common exceptions

- **`flextext_exporter.py`**: FLEXText XML export
  - Graph data → XML serialization
  - Round-trip compatibility

- **`json_exporter.py`**: JSON export
  - Graph data → JSON serialization

**Pattern:**
- Protocol-based design (easy to extend)
- Registry pattern for exporter lookup
- Graph data input → formatted output

### Database (`app/database.py`)

Neo4j connection management:

- Driver initialization
- Session management
- Context managers for resource cleanup
- FastAPI dependency for injection

### Migrations (`app/migrations/neo4j/`)

- **`schema.cypher`**: Neo4j schema definition
  - Node constraints
  - Relationship types
  - Indexes

## Frontend Structure

### Next.js App Router

Uses Next.js 14+ App Router pattern:

- **`app/`**: Application directory
- **`layout.tsx`**: Root layout with providers
- **`page.tsx`**: Home page
- **Route groups**: Organized by feature

### Components (`app/components/`)

React components organized by feature:

- **`GraphVisualization.tsx`**: Main graph visualization
- **`FileUpload.tsx`**: File upload interface
- **`SearchBar.tsx`**: Search functionality
- **`NodeDetails.tsx`**: Node detail panel
- **`Navigation.tsx`**: Navigation bar
- **`GraphFilters.tsx`**: Graph filtering controls
- **`ExportFileTypeModal.tsx`**: Export modal
- **`CorpusStatistics.tsx`**: Corpus statistics display
- **`DatabaseStatistics.tsx`**: Database statistics

**Pattern:**
- Functional components with hooks
- TypeScript for type safety
- Tailwind CSS for styling
- API calls via fetch

### API Routes (`app/api/`)

Next.js API routes (if needed for proxying):

- **`v1/[...slug]/route.ts`**: Proxy to backend API

## Code Conventions

### Python

- **Style**: PEP 8
- **Type hints**: Used throughout
- **Docstrings**: Google style
- **Imports**: Absolute imports preferred
- **Error handling**: Specific exceptions, proper logging

### TypeScript

- **Style**: ESLint + Prettier
- **Types**: Explicit types, avoid `any`
- **Components**: Functional components with hooks
- **Naming**: PascalCase for components, camelCase for functions

### File Naming

- **Python**: `snake_case.py`
- **TypeScript**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Config files**: `kebab-case` (e.g., `next.config.js`)

## Dependencies

### Backend (`requirements.txt`)

Key dependencies:
- `fastapi`: Web framework
- `uvicorn`: ASGI server
- `neo4j`: Neo4j driver
- `pydantic`: Data validation
- `python-dotenv`: Environment variables
- `pytest`: Testing framework

### Frontend (`package.json`)

Key dependencies:
- `next`: React framework
- `react`: UI library
- `typescript`: Type safety
- `tailwindcss`: Styling
- `d3` or similar: Graph visualization

## Testing Structure

### Backend Tests (`backend/tests/`)

- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Database tests**: Validate Neo4j operations
- **Standalone scripts**: Validation and utility scripts

**Pattern:**
- Pytest for test framework
- Mocked database for unit tests
- Real database for integration tests

## Configuration Files

### Backend

- **`env.example`**: Environment variables template
- **`requirements.txt`**: Python dependencies
- **`Dockerfile`**: Container definition

### Frontend

- **`.env.local`**: Environment variables (gitignored)
- **`package.json`**: Node.js dependencies and scripts
- **`next.config.js`**: Next.js configuration
- **`tailwind.config.js`**: Tailwind CSS configuration
- **`tsconfig.json`**: TypeScript configuration

### Infrastructure

- **`docker-compose.yml`**: Local development services
- **`docker-compose.free.yml`**: Free tier configuration
- **`gcp/cloudbuild.yaml`**: Cloud Build configuration
- **`gcp/terraform/*.tf`**: Infrastructure as code

## Extension Points

### Adding a New Exporter

1. Create `app/exporters/new_exporter.py`
2. Implement `Exporter` protocol from `base.py`
3. Register in `app/exporters/__init__.py`

### Adding a New Parser

1. Create `app/parsers/new_parser.py`
2. Implement parser function
3. Add route handler in `app/routers/linguistic.py`

### Adding a New API Endpoint

1. Add route handler in appropriate router
2. Create Pydantic models in `app/models/`
3. Implement service logic in `app/services/`
4. Add tests in `backend/tests/`

## Best Practices

1. **Separation of Concerns**: Routers → Services → Database
2. **Dependency Injection**: Use FastAPI dependencies
3. **Error Handling**: Specific exceptions, proper HTTP status codes
4. **Type Safety**: Use type hints and Pydantic models
5. **Documentation**: Keep code and docs in sync
6. **Testing**: Write tests for new features
7. **Logging**: Use structured logging with context

---

For more details, see:
- [Architecture Guide](./architecture.md)
- [API Reference](./api-reference.md)
- [Contributing Guide](./contributing.md)

