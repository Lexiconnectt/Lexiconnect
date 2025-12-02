# Contributing to Lexiconnect

Thank you for your interest in contributing to Lexiconnect! This guide will help you get started with contributing to the project.

## Getting Started

1. **Read the documentation**
   - [Developer Guide](./README.md)
   - [Architecture Guide](./architecture.md)
   - [Code Structure](./code-structure.md)

2. **Set up your development environment**
   - Follow the [Setup Guide](./setup.md)

3. **Understand the codebase**
   - Review existing code
   - Check test files for examples
   - Read code comments

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

**Branch naming conventions:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates

### 2. Make Your Changes

- Write clean, readable code
- Follow existing code style
- Add comments for complex logic
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest tests/

# Frontend tests (if available)
cd frontend
npm test
```

### 4. Commit Your Changes

```bash
git add .
git commit -m "Description of changes"
```

**Commit message guidelines:**
- Use clear, descriptive messages
- Start with a verb (Add, Fix, Update, Remove)
- Keep first line under 50 characters
- Add details in body if needed

**Examples:**
```
Add export functionality for JSON format
Fix Neo4j connection timeout issue
Update API documentation
```

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request with:
- Clear description of changes
- Reference to related issues (if any)
- Screenshots (for UI changes)

## Code Style

### Python

- **Style**: Follow PEP 8
- **Formatting**: Use Black (if configured)
- **Type hints**: Use type hints for function parameters and return values
- **Docstrings**: Use Google-style docstrings

**Example:**
```python
def process_text(text_id: str, db: Session) -> dict:
    """Process a text and return statistics.
    
    Args:
        text_id: The ID of the text to process
        db: Neo4j database session
        
    Returns:
        Dictionary containing processing statistics
        
    Raises:
        ValueError: If text_id is invalid
    """
    ...
```

### TypeScript

- **Style**: Follow ESLint rules
- **Formatting**: Use Prettier
- **Types**: Explicit types, avoid `any`
- **Components**: Functional components with hooks

**Example:**
```typescript
interface SearchProps {
  query: string;
  onSearch: (query: string) => void;
}

export function SearchBar({ query, onSearch }: SearchProps) {
  // Component implementation
}
```

## Testing Guidelines

### Writing Tests

- **Unit tests**: Test individual functions/classes
- **Integration tests**: Test API endpoints
- **Test coverage**: Aim for high coverage on critical paths

### Test Structure

```python
# backend/tests/test_example.py
import pytest
from app.services.example_service import example_function

def test_example_function_success():
    """Test successful execution."""
    result = example_function("input")
    assert result == "expected_output"

def test_example_function_error():
    """Test error handling."""
    with pytest.raises(ValueError):
        example_function("invalid_input")
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_example.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v tests/
```

## Documentation

### Code Documentation

- **Docstrings**: Document all public functions and classes
- **Comments**: Explain "why", not "what"
- **Type hints**: Use type hints for clarity

### User Documentation

- Update user guide for new features
- Add examples and screenshots
- Keep troubleshooting section current

### Developer Documentation

- Update architecture docs for structural changes
- Document new APIs
- Update setup guide for new dependencies

## Pull Request Process

### Before Submitting

- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No linter errors
- [ ] Commit messages are clear

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring

## Testing
How was this tested?

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Code follows style guidelines
```

### Review Process

1. **Automated checks**: CI/CD runs tests
2. **Code review**: Maintainers review code
3. **Feedback**: Address review comments
4. **Approval**: Once approved, PR is merged

## Adding New Features

### Backend Features

1. **Create models** in `app/models/`
2. **Add service logic** in `app/services/`
3. **Create routes** in `app/routers/`
4. **Write tests** in `backend/tests/`
5. **Update API docs** (auto-generated from code)

### Frontend Features

1. **Create components** in `app/components/`
2. **Add API calls** (use existing patterns)
3. **Update styles** (Tailwind CSS)
4. **Test in browser**

### New Exporters

1. **Create exporter class** in `app/exporters/`
2. **Implement `Exporter` protocol**
3. **Register in `app/exporters/__init__.py`**
4. **Add tests**
5. **Update frontend** (if needed)

### New Parsers

1. **Create parser** in `app/parsers/`
2. **Add route handler** in `app/routers/linguistic.py`
3. **Write tests**
4. **Update documentation**

## Bug Reports

### Reporting Bugs

When reporting bugs, include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Detailed steps
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, Python/Node versions, etc.
6. **Logs**: Relevant error messages or logs

### Bug Report Template

```markdown
## Description
Brief description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. ...

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., Windows 10]
- Python: [e.g., 3.11]
- Node: [e.g., 18.0.0]

## Logs
Error messages or relevant logs
```

## Feature Requests

### Suggesting Features

When suggesting features:

1. **Use case**: Why is this feature needed?
2. **Description**: Detailed feature description
3. **Alternatives**: Other solutions considered
4. **Impact**: Who benefits from this feature?

## Code Review Guidelines

### For Reviewers

- Be constructive and respectful
- Focus on code quality and correctness
- Suggest improvements, don't just point out problems
- Approve when satisfied

### For Authors

- Respond to all comments
- Make requested changes
- Ask questions if unclear
- Be open to feedback

## Project-Specific Guidelines

### Database Changes

- Update schema in `backend/app/migrations/neo4j/schema.cypher`
- Test migrations on sample data
- Document schema changes

### API Changes

- Follow RESTful conventions
- Update API documentation
- Maintain backward compatibility when possible
- Version breaking changes

### Frontend Changes

- Maintain responsive design
- Test on multiple browsers
- Consider accessibility
- Update UI documentation

## Getting Help

- **Documentation**: Check existing docs first
- **Issues**: Search existing issues
- **Code**: Review similar code in codebase
- **Questions**: Ask in PR comments or issues

## Recognition

Contributors will be:
- Listed in project documentation (if applicable)
- Credited in commit history
- Acknowledged in release notes

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Help others learn

---

