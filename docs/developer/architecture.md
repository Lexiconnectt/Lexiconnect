# Lexiconnect Architecture

This document provides a comprehensive overview of the Lexiconnect system architecture, design decisions, and how components interact.

## System Overview

Lexiconnect is a full-stack web application designed for linguistic documentation and research. It uses a graph database to model complex linguistic relationships.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Client Browser                       │
│              (Next.js Frontend - Vercel)                │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS/REST API
                     │
┌────────────────────▼────────────────────────────────────┐
│              FastAPI Backend (Cloud Run)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Routers  │→ │ Services │→ │  Models  │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│       │              │                                  │
│       └──────┬───────┘                                  │
│              │                                          │
│       ┌──────▼───────┐                                  │
│       │   Parsers    │                                  │
│       │  Exporters   │                                  │
│       └──────────────┘                                  │
└────────────────────┬────────────────────────────────────┘
                     │ Cypher Queries
                     │
┌────────────────────▼────────────────────────────────────┐
│              Neo4j Graph Database                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │  Nodes   │  │Relations  │  │Properties│              │
│  └──────────┘  └──────────┘  └──────────┘               │
└─────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend (Next.js)

**Technology Stack:**
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS
- React

**Key Components:**
- `GraphVisualization.tsx` - Main graph visualization using D3.js or similar
- `FileUpload.tsx` - File upload interface
- `SearchBar.tsx` - Search functionality
- `NodeDetails.tsx` - Node detail panel

**Architecture Patterns:**
- Component-based architecture
- Client-side state management
- API route handlers for proxy requests (if needed)

### Backend (FastAPI)

**Technology Stack:**
- FastAPI (Python 3.11+)
- Pydantic for data validation
- Neo4j driver for database access
- Uvicorn ASGI server

**Architecture Layers:**

#### 1. Router Layer (`app/routers/`)
- Handles HTTP requests and responses
- Input validation via Pydantic models
- Error handling and status codes
- Authentication/authorization

**Key Routers:**
- `auth.py` - Authentication endpoints
- `linguistic.py` - Linguistic data operations
- `export.py` - Data export endpoints
- `languages.py` - Language management
- `documentation.py` - Documentation entries

#### 2. Service Layer (`app/services/`)
- Business logic
- Data transformation
- Database query orchestration

**Key Services:**
- `neo4j_service.py` - Neo4j query operations
- `export_service.py` - Export orchestration
- `export_flextext_service.py` - FLEXText-specific export

#### 3. Model Layer (`app/models/`)
- Pydantic models for data validation
- Request/response schemas
- Data transfer objects (DTOs)

#### 4. Parser Layer (`app/parsers/`)
- File format parsers
- Import data transformation

**Parsers:**
- `flextext_parser.py` - FLEx Text XML parser
- `elan_parser.py` - ELAN file parser

#### 5. Exporter Layer (`app/exporters/`)
- Export format implementations
- Data serialization

**Exporters:**
- `flextext_exporter.py` - FLEXText XML export
- `json_exporter.py` - JSON export
- `base.py` - Exporter interface

### Database (Neo4j)

**Graph Model:**
- Nodes represent linguistic entities (Text, Section, Phrase, Word, Morpheme, Gloss)
- Relationships represent linguistic connections
- Properties store attributes

**Key Relationships:**
- `SECTION_PART_OF_TEXT` - Text → Section
- `PHRASE_IN_SECTION` - Section → Phrase
- `PHRASE_COMPOSED_OF` - Phrase → Word
- `WORD_MADE_OF` - Word → Morpheme
- `ANALYZES` - Gloss → (Word|Phrase|Morpheme)

For detailed schema, see [DATABASE.md](../../DATABASE.md).

## Data Flow

### Upload Flow

```
1. User uploads .flextext file
   ↓
2. Frontend sends POST /api/v1/linguistic/upload-flextext
   ↓
3. Router receives file, validates
   ↓
4. Parser (flextext_parser.py) parses XML
   ↓
5. Service creates Neo4j nodes and relationships
   ↓
6. Database stores graph structure
   ↓
7. Response with upload statistics
```

### Visualization Flow

```
1. User searches for word/morpheme
   ↓
2. Frontend sends GET /api/v1/linguistic/search
   ↓
3. Router validates query
   ↓
4. Service queries Neo4j for matching nodes
   ↓
5. Service retrieves related nodes (neighbors)
   ↓
6. Response with graph data (nodes + edges)
   ↓
7. Frontend renders graph visualization
```

### Export Flow

```
1. User clicks export button
   ↓
2. Frontend sends POST /api/v1/export?file_type=flextext
   ↓
3. Router validates request
   ↓
4. Service retrieves graph data from Neo4j
   ↓
5. Exporter serializes to FLEXText XML
   ↓
6. Response streams file download
```

## Design Decisions

### Why Neo4j?

- **Graph-native**: Linguistic relationships are naturally graph-structured
- **Flexible schema**: Easy to add new relationship types
- **Query power**: Cypher queries express complex linguistic patterns
- **Performance**: Efficient traversal of relationships

### Why FastAPI?

- **Performance**: High performance async framework
- **Type safety**: Pydantic models provide validation
- **Documentation**: Auto-generated OpenAPI docs
- **Modern Python**: Uses Python 3.11+ features

### Why Next.js?

- **Server-side rendering**: Better SEO and performance
- **API routes**: Can proxy requests if needed
- **TypeScript**: Type safety in frontend
- **Vercel integration**: Easy deployment

### Why Graph Database?

Linguistic data has complex relationships:
- Words contain morphemes
- Phrases contain words
- Morphemes can be shared across words
- Glosses analyze multiple entities
- These relationships form a natural graph

## Security Architecture

### Authentication
- JWT-based authentication
- Token expiration
- Secure password hashing

### CORS
- Configured for specific origins
- Prevents unauthorized access

### Database Security
- Connection authentication
- Parameterized queries (prevents injection)
- Environment-based credentials

## Scalability Considerations

### Current Limitations
- Single Neo4j instance
- No caching layer
- Synchronous file processing

### Future Improvements
- Neo4j cluster for high availability
- Redis caching for frequent queries
- Async file processing queue
- CDN for static assets

## Deployment Architecture

### Development
- Docker Compose for local services
- Hot reload for development
- Local Neo4j instance

### Production
- **Backend**: Google Cloud Run (containerized)
- **Frontend**: Vercel (serverless)
- **Database**: Neo4j AuraDB or self-hosted
- **Storage**: Google Cloud Storage (optional)

## Monitoring and Logging

### Logging
- Structured logging with context
- Error tracking
- Request/response logging

### Health Checks
- `/health` endpoint
- Database connection checks
- Container health checks

## Error Handling

### Error Types
- **400 Bad Request**: Invalid input
- **401 Unauthorized**: Authentication required
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server errors

### Error Response Format
```json
{
  "detail": "Error message",
  "status_code": 400
}
```

## API Design Principles

1. **RESTful**: Follow REST conventions
2. **Versioned**: `/api/v1/` prefix
3. **Consistent**: Uniform response formats
4. **Documented**: Auto-generated OpenAPI docs
5. **Validated**: Pydantic models for validation

## Testing Architecture

### Test Types
- **Unit tests**: Test individual functions
- **Integration tests**: Test API endpoints
- **Database tests**: Validate Neo4j operations

### Test Structure
- `tests/` directory in backend
- Pytest framework
- Mocked database for unit tests
- Real database for integration tests

## Future Architecture Considerations

### Potential Enhancements
- Microservices split (if needed)
- Event-driven architecture
- Real-time updates (WebSockets)
- Multi-tenancy support
- Advanced caching strategies

---

For more details on specific components, see:
- [Code Structure](./code-structure.md)
- [API Reference](./api-reference.md)
- [Database Schema](../../DATABASE.md)

