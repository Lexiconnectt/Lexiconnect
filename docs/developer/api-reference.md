# Lexiconnect API Reference

Complete API reference for the Lexiconnect backend. All endpoints are prefixed with `/api/v1`.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: (Configured per deployment)

## Interactive Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Authentication

Most endpoints require authentication via JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <token>
```

## Endpoints

### Health Check

#### GET `/health`

Check API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "lexiconnect-api"
}
```

---

### Authentication

#### POST `/api/v1/auth/register`

Register a new user.

**Request Body:**
```json
{
  "username": "string",
  "email": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "id": "user-id",
  "username": "string",
  "email": "string"
}
```

#### POST `/api/v1/auth/login`

Login and get JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:** `200 OK`
```json
{
  "access_token": "jwt-token",
  "token_type": "bearer"
}
```

---

### Languages

#### POST `/api/v1/languages/`

Create a new language entry.

**Request Body:**
```json
{
  "name": "string",
  "code": "string",
  "description": "string (optional)"
}
```

**Response:** `200 OK`
```json
{
  "id": "language-id",
  "name": "string",
  "code": "string",
  "description": "string",
  "created_at": "ISO datetime string"
}
```

#### GET `/api/v1/languages/`

Get list of languages.

**Query Parameters:**
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records

**Response:** `200 OK`
```json
[
  {
    "id": "language-id",
    "name": "string",
    "code": "string",
    "description": "string",
    "created_at": "ISO datetime string"
  }
]
```

#### GET `/api/v1/languages/{language_id}`

Get a specific language.

**Response:** `200 OK`
```json
{
  "id": "language-id",
  "name": "string",
  "code": "string",
  "description": "string",
  "created_at": "ISO datetime string"
}
```

---

### Linguistic Data

#### POST `/api/v1/linguistic/upload-flextext`

Upload and parse a FLEXText XML file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload (`.flextext` file)

**Response:** `200 OK`
```json
{
  "message": "File uploaded successfully",
  "text_id": "text-id",
  "stats": {
    "sections": 5,
    "phrases": 20,
    "words": 100,
    "morphemes": 150
  }
}
```

**Error Responses:**
- `400 Bad Request`: Invalid file format or parsing error
- `500 Internal Server Error`: Server error during processing

#### GET `/api/v1/linguistic/search`

Search for words or morphemes.

**Query Parameters:**
- `query` (string, required) - Search term
- `type` (string, enum: `word`, `morpheme`) - Type to search
- `limit` (int, default: 200, min: 10, max: 1000) - Result limit

**Response:** `200 OK`
```json
{
  "nodes": [
    {
      "id": "word-id",
      "type": "Word",
      "properties": {
        "surface_form": "example",
        "gloss": "example",
        "language": "en"
      }
    }
  ],
  "edges": [
    {
      "source": "word-id",
      "target": "morpheme-id",
      "type": "WORD_MADE_OF"
    }
  ]
}
```

#### GET `/api/v1/linguistic/graph-data`

Get graph data for visualization.

**Query Parameters:**
- `text_id` (string, optional) - Filter by text ID
- `limit` (int, default: 200) - Maximum nodes to return

**Response:** `200 OK`
```json
{
  "nodes": [...],
  "edges": [...]
}
```

#### GET `/api/v1/linguistic/statistics`

Get database statistics.

**Response:** `200 OK`
```json
{
  "texts": 10,
  "sections": 50,
  "phrases": 200,
  "words": 1000,
  "morphemes": 1500
}
```

---

### Export

#### POST `/api/v1/export`

Export data in specified format.

**Query Parameters:**
- `file_type` (string, default: `flextext`) - Export format

**Request Body:**
```json
{
  "file_id": "text-id"
}
```

**Response:** `200 OK`
- Content-Type: Varies by exporter (e.g., `application/xml` for flextext)
- Content-Disposition: `attachment; filename="<file_id>.<extension>"`
- Body: Binary file content

**Error Responses:**
- `400 Bad Request`: Missing file_id or unsupported file_type
- `404 Not Found`: File ID not found
- `500 Internal Server Error`: Export generation failed

#### POST `/api/v1/export/flextext`

Legacy endpoint (same as `/api/v1/export?file_type=flextext`).

---

### Documentation

#### POST `/api/v1/docs/`

Create a documentation entry.

**Request Body:**
```json
{
  "title": "string",
  "content": "string",
  "language_id": "string (optional)"
}
```

**Response:** `200 OK`
```json
{
  "id": "doc-id",
  "title": "string",
  "content": "string",
  "language_id": "string or null",
  "created_at": "ISO datetime string"
}
```

#### GET `/api/v1/docs/`

Get list of documentation entries.

**Query Parameters:**
- `language_id` (string, optional) - Filter by language
- `skip` (int, default: 0) - Number of records to skip
- `limit` (int, default: 100) - Maximum number of records

**Response:** `200 OK`
```json
[
  {
    "id": "doc-id",
    "title": "string",
    "content": "string",
    "language_id": "string or null",
    "created_at": "ISO datetime string"
  }
]
```

#### POST `/api/v1/docs/upload`

Upload a documentation file.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: File upload
- Query Parameter: `language_id` (optional)

**Response:** `200 OK`
```json
{
  "message": "File uploaded successfully",
  "document_id": "doc-id"
}
```

---

## Data Models

### Word

```json
{
  "id": "string",
  "surface_form": "string",
  "gloss": "string (optional)",
  "pos": "string (optional)",
  "language": "string (optional)"
}
```

### Morpheme

```json
{
  "id": "string",
  "surface_form": "string",
  "citation_form": "string (optional)",
  "gloss": "string (optional)",
  "msa": "string (optional)",
  "type": "stem|prefix|suffix|infix|circumfix|root",
  "language": "string (optional)"
}
```

### Phrase

```json
{
  "id": "string",
  "segnum": "string (optional)",
  "surface_text": "string",
  "language": "string (optional)",
  "order": "integer"
}
```

### Text

```json
{
  "id": "string",
  "title": "string (optional)",
  "source": "string (optional)",
  "comment": "string (optional)",
  "language_code": "string (optional)"
}
```

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message description"
}
```

### Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## Rate Limiting

Currently, no rate limiting is implemented. Consider implementing for production use.

## CORS

CORS is configured for specific origins. See `backend/app/core/config.py` for allowed origins.

## Versioning

API version is specified in the URL path (`/api/v1/`). Future versions will use `/api/v2/`, etc.

## Pagination

List endpoints support pagination via `skip` and `limit` query parameters:

```
GET /api/v1/languages/?skip=0&limit=20
```

## Filtering and Search

Search endpoints support filtering:

```
GET /api/v1/linguistic/search?query=example&type=word&limit=50
```

## Examples

### Upload a FLEXText File

```bash
curl -X POST \
  http://localhost:8000/api/v1/linguistic/upload-flextext \
  -H "Content-Type: multipart/form-data" \
  -F "file=@example.flextext"
```

### Search for Words

```bash
curl -X GET \
  "http://localhost:8000/api/v1/linguistic/search?query=example&type=word&limit=10"
```

### Export Data

```bash
curl -X POST \
  http://localhost:8000/api/v1/export?file_type=flextext \
  -H "Content-Type: application/json" \
  -d '{"file_id": "text-001"}' \
  --output exported.flextext
```

### Get Statistics

```bash
curl -X GET \
  http://localhost:8000/api/v1/linguistic/statistics
```

## Testing

Use the interactive documentation at `/docs` to test endpoints, or use tools like:
- Postman
- curl
- httpie
- Your frontend application

---

For more details, see the interactive API documentation at `http://localhost:8000/docs` when the backend is running.

