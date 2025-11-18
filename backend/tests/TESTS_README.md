# Running Tests

This directory contains various test scripts for the Lexiconnect backend. There are two types of tests:

1. **Standalone Scripts** - Can be run directly with Python
2. **Pytest Tests** - Use the pytest framework

## Prerequisites

### Option 1: Install Dependencies Locally
```bash
cd backend
pip install -r requirements.txt
```

### Option 2: Use Docker (Recommended)
```bash
# Make sure services are running
docker-compose -f docker-compose.free.yml up -d
```

## Running Standalone Test Scripts

These scripts can be run directly with Python:

### 1. Database Validation Script
Comprehensive Cypher-based validation of database integrity:
```bash
# From Docker (recommended)
docker-compose -f docker-compose.free.yml exec backend python tests/validate_database.py

# Or locally (after installing dependencies)
cd backend
python tests/validate_database.py
```

### 2. Graph Edges Test
Checks for missing ANALYZES relationships between Gloss, Word, and Morpheme nodes:
```bash
# From Docker
docker-compose -f docker-compose.free.yml exec backend python tests/test_graph_edges.py

# Or locally
cd backend
python tests/test_graph_edges.py
```

### 3. Upload Test
Tests FLEx file parsing and schema compliance:
```bash
# From Docker
docker-compose -f docker-compose.free.yml exec backend python tests/test_upload.py

# Or locally
cd backend
python tests/test_upload.py
```

**Note:** This test requires `.flextext` files in a `data/` directory.

### 4. Export Service Test
Tests the export service with a real database connection:
```bash
# From Docker (requires text_id)
docker-compose -f docker-compose.free.yml exec backend python tests/test_export_service.py [text_id]

# Or locally
cd backend
python tests/test_export_service.py [text_id]

# If no text_id provided, it will list available texts
python tests/test_export_service.py
```

## Running Pytest Tests

These tests use the pytest framework and can be run individually or all together:

### Run All Pytest Tests
```bash
# From Docker
docker-compose -f docker-compose.free.yml exec backend pytest tests/

# Or locally
cd backend
pytest tests/
```

### Run Specific Pytest Test Files
```bash
# From Docker
docker-compose -f docker-compose.free.yml exec backend pytest tests/test_neo4j_service.py
docker-compose -f docker-compose.free.yml exec backend pytest tests/test_json_exporter.py
docker-compose -f docker-compose.free.yml exec backend pytest tests/test_export_route.py
docker-compose -f docker-compose.free.yml exec backend pytest tests/test_export_flextext_service.py

# Or locally
cd backend
pytest tests/test_neo4j_service.py
pytest tests/test_json_exporter.py
pytest tests/test_export_route.py
pytest tests/test_export_flextext_service.py
```

### Run Specific Test Functions
```bash
# Run a specific test function
pytest tests/test_neo4j_service.py::test_get_file_graph_data_returns_nested_structure

# Run with verbose output
pytest tests/ -v

# Run with output capture disabled (see print statements)
pytest tests/ -s
```

## Test File Descriptions

| File | Type | Description |
|------|------|-------------|
| `validate_database.py` | Standalone | Comprehensive database integrity validation using Cypher queries |
| `test_graph_edges.py` | Standalone | Checks for missing ANALYZES relationships in the graph |
| `test_upload.py` | Standalone | Tests FLEx file parsing and schema compliance |
| `test_export_service.py` | Standalone | Tests export service with real database connection |
| `test_neo4j_service.py` | Pytest | Unit tests for Neo4j service with mocked database |
| `test_json_exporter.py` | Pytest | Unit tests for JSON exporter |
| `test_export_route.py` | Pytest | Unit tests for export API endpoints |
| `test_export_flextext_service.py` | Pytest | Unit tests for FLEXText export service |

## Environment Variables

Make sure these are set (or use defaults):
- `NEO4J_URI` (default: `bolt://localhost:7687`)
- `NEO4J_USER` (default: `neo4j`)
- `NEO4J_PASSWORD` (default: `password`)

For Docker, these are automatically set in `docker-compose.free.yml`.

For local runs, create a `.env` file in the `backend/` directory:
```bash
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Quick Reference

```bash
# Run all tests (pytest only)
pytest tests/

# Run validation script
python tests/validate_database.py

# Run all standalone scripts
python tests/test_graph_edges.py
python tests/test_upload.py
python tests/test_export_service.py

# Run with Docker (from project root)
docker-compose -f docker-compose.free.yml exec backend pytest tests/
docker-compose -f docker-compose.free.yml exec backend python tests/validate_database.py
```

