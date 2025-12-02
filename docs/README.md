# Lexiconnect Documentation

Welcome to the Lexiconnect documentation! This directory contains all documentation for the Lexiconnect project, organized into user and developer sections.

## 📚 Documentation Overview

### For End Users
- **[User Guide](./user/README.md)** - Complete guide for using Lexiconnect to upload, visualize, and export linguistic data

### For Developers
- **[Developer Guide](./developer/README.md)** - Comprehensive guide for developers working on Lexiconnect
- **[Architecture](./developer/architecture.md)** - System architecture and design decisions
- **[Setup Guide](./developer/setup.md)** - Development environment setup
- **[API Reference](./developer/api-reference.md)** - Complete API documentation
- **[Code Structure](./developer/code-structure.md)** - Codebase organization and conventions
- **[Contributing](./developer/contributing.md)** - Guidelines for contributing to the project

### Technical Documentation
- **[Database Schema](../DATABASE.md)** - Neo4j database structure and relationships
- **[Export System](./export_system.md)** - How the export system works
- **[FLEXText Export Mapping](./flextext_export_mapping.md)** - Database to FLEXText XML mapping
- **[Testing Guide](../backend/tests/TESTS_README.md)** - How to run tests

## 🚀 Quick Links

- **Getting Started**: See [User Guide](./user/README.md) for end users or [Developer Setup](./developer/setup.md) for developers
- **Project Overview**: See the main [README.md](../README.md)
- **API Documentation**: Interactive API docs available at `http://localhost:8000/docs` when the backend is running

## 📖 Documentation Structure

```
docs/
├── README.md (this file)
├── user/
│   └── README.md (User guide)
├── developer/
│   ├── README.md (Developer overview)
│   ├── architecture.md (System architecture)
│   ├── setup.md (Development setup)
│   ├── api-reference.md (API documentation)
│   ├── code-structure.md (Code organization)
│   └── contributing.md (Contributing guidelines)
├── export_system.md (Export system technical docs)
└── flextext_export_mapping.md (FLEXText mapping details)
```

## 🎯 Who Should Read What?

### I'm a linguistic researcher using Lexiconnect
→ Start with the [User Guide](./user/README.md)

### I'm a developer taking over this project
→ Start with the [Developer Guide](./developer/README.md), then read [Architecture](./developer/architecture.md) and [Setup Guide](./developer/setup.md)

### I want to understand how exports work
→ Read [Export System](./export_system.md) and [FLEXText Export Mapping](./flextext_export_mapping.md)

### I want to understand the database structure
→ Read [DATABASE.md](../DATABASE.md)

### I want to run tests
→ Read [Testing Guide](../backend/tests/TESTS_README.md)

## 📝 Documentation Maintenance

This documentation is maintained as part of the Lexiconnect project. When making significant changes to the codebase:

1. Update relevant documentation files
2. Keep examples and code snippets current
3. Update version numbers and dates where applicable
4. Ensure cross-references between documents remain accurate

## 🤝 Contributing to Documentation

If you find errors or areas that need improvement:

1. Check the [Contributing Guide](./developer/contributing.md) for documentation standards
2. Submit updates via pull request
3. Ensure all code examples are tested and working

---

**Last Updated**: This documentation structure was established for project handoff. Individual documents may have different update dates.

