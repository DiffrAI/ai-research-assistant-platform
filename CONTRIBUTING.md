# Contributing to AI Research Assistant Platform

Thank you for your interest in contributing to the AI Research Assistant Platform! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## Getting Started

### Prerequisites

- Python 3.9+ 
- Node.js 16+ (for frontend)
- Git
- Docker (optional, for containerized development)

### Quick Start

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-research-assistant-platform.git
   cd ai-research-assistant-platform
   ```

2. **Set up the development environment**
   ```bash
   # Backend setup
   uv sync
   cp .env.sample .env
   # Edit .env with your configuration
   
   # Frontend setup
   cd frontend
   npm install
   ```

3. **Start development servers**
   ```bash
   # Backend
   uv run python main.py
   
   # Frontend (in another terminal)
   cd frontend && npm start
   ```

## Development Setup

### Backend Development

The backend uses FastAPI with the following simplified structure:

```
app/
├── api/                   # API endpoints
│   ├── auth.py           # Authentication endpoints
│   ├── chat.py           # Chat & streaming endpoints
│   ├── research.py       # Research endpoints
│   ├── payment.py        # Payment & subscription endpoints
│   └── health.py         # Health check endpoints
├── core/                 # Core infrastructure
│   ├── config.py         # Configuration management
│   ├── database.py       # Database setup & connections
│   ├── server.py         # FastAPI application setup
│   └── lifespan.py       # Application lifecycle management
├── models/               # Data models
│   └── models.py         # Unified Pydantic & SQLAlchemy models
├── workflows/            # AI workflow components
│   └── graphs/websearch/ # Web search AI workflows
├── tasks/                # Background task processing
├── auth.py              # Authentication logic & utilities
├── payment.py           # Payment service integration
├── responses.py         # Response formatting utilities
├── exceptions.py        # Custom exception handling
└── utils.py             # Essential utility functions
```

### Frontend Development

The frontend uses React with:

```
frontend/src/
├── components/     # Reusable UI components
├── pages/          # Page components
├── services/       # API services
├── store/          # State management (Zustand)
└── utils/          # Utility functions
```

### Environment Configuration

Copy the example environment file and configure it:

```bash
cp .env.sample .env
```

Required for development:
- `SECRET_KEY` (any string for development)
- `USE_LOCAL_MODEL=true`
- `LOCAL_MODEL_NAME` (must match your Ollama model)
- `SEARCH_PROVIDER=duckduckgo`

## Code Style

### Python (Backend)

We use the following tools for code quality:

- **Ruff** for linting and formatting
- **MyPy** for type checking
- **Black** for code formatting (via Ruff)
- **isort** for import sorting (via Ruff)

**Run code quality checks:**
```bash
make lint          # Lint and format code
make type-check    # Run type checking
make security-check # Security checks
```

**Pre-commit hooks:**
```bash
make pre-commit-install  # Install pre-commit hooks
make pre-commit-run      # Run pre-commit on all files
```

### JavaScript/React (Frontend)

- **ESLint** for linting
- **Prettier** for formatting
- **React Hook Form** for form management
- **Zustand** for state management

**Run frontend checks:**
```bash
cd frontend
npm run lint
npm run test
```

## Testing

### Backend Tests

Run all tests:
```bash
uv run pytest tests/ -v
```

Run specific test files:
```bash
uv run pytest tests/test_api.py -v
```

Run with coverage:
```bash
make test
```

### Frontend Tests

```bash
cd frontend
npm test
```

### Integration Tests

Test the full stack:
```bash
# Start both services
./start-dev.sh

# Run API tests
./test-apis.sh
```

## Pull Request Process

### Before Submitting

1. **Ensure your code follows the style guidelines**
   ```bash
   make lint
   make type-check
   make test
   ```

2. **Update documentation**
   - Update README.md if needed
   - Add/update docstrings for new functions
   - Update API documentation if endpoints changed

3. **Test your changes**
   - Run all tests
   - Test manually if needed
   - Ensure no breaking changes

### Pull Request Guidelines

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clear, descriptive commit messages
   - Use conventional commits: `feat:`, `fix:`, `docs:`, `test:`, etc.

3. **Submit your PR**
   - Use the PR template
   - Describe what you changed and why
   - Include any relevant issue numbers
   - Add screenshots for UI changes

### PR Template

```markdown
## Description
Brief description of what this PR does.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Test update

## Testing
- [ ] All tests pass
- [ ] Manual testing completed
- [ ] No breaking changes

## Checklist
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] Commit messages are conventional
```

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Environment details**
   - OS and version
   - Python version
   - Node.js version
   - Ollama version (if using local models)

2. **Steps to reproduce**
   - Clear, step-by-step instructions
   - Sample data if applicable

3. **Expected vs actual behavior**
   - What you expected to happen
   - What actually happened

4. **Additional context**
   - Error messages/logs
   - Screenshots if UI-related
   - Browser console logs if frontend issue

### Issue Template

```markdown
## Bug Description
Brief description of the bug.

## Steps to Reproduce
1. Step 1
2. Step 2
3. Step 3

## Expected Behavior
What should happen.

## Actual Behavior
What actually happens.

## Environment
- OS: [e.g., macOS 14.0]
- Python: [e.g., 3.11.5]
- Node.js: [e.g., 18.17.0]
- Ollama: [e.g., 0.1.20]

## Additional Information
Any other context, logs, or screenshots.
```

## Feature Requests

### Before Requesting Features

1. **Check existing issues** - Your feature might already be requested
2. **Search the codebase** - The feature might already exist
3. **Consider the scope** - Is this feature within the project's goals?

### Feature Request Template

```markdown
## Feature Description
Clear description of the feature you'd like to see.

## Use Case
Why is this feature needed? What problem does it solve?

## Proposed Solution
How would you like to see this implemented?

## Alternatives Considered
What other approaches have you considered?

## Additional Context
Any other relevant information.
```

## Architecture Guidelines

### Backend

- **Keep it async**: Use `async/await` for I/O operations
- **Use dependency injection**: Leverage FastAPI's dependency system
- **Follow REST principles**: Design APIs consistently
- **Handle errors gracefully**: Use proper exception handling
- **Cache appropriately**: Use Redis for caching when beneficial

### Frontend

- **Component composition**: Build reusable components
- **State management**: Use Zustand for global state
- **Form handling**: Use React Hook Form for forms
- **Error boundaries**: Implement proper error handling
- **Responsive design**: Ensure mobile compatibility

### Database

- **Use migrations**: For schema changes
- **Index appropriately**: For performance
- **Validate data**: At the model level
- **Handle relationships**: Properly with SQLAlchemy

## Development Workflow

### Daily Development

1. **Start with a fresh branch**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b feature/your-feature
   ```

2. **Make incremental commits**
   ```bash
   git add .
   git commit -m "feat: add user profile editing"
   ```

3. **Test frequently**
   ```bash
   make test
   make lint
   ```

4. **Push and create PR**
   ```bash
   git push origin feature/your-feature
   # Create PR on GitHub
   ```

### Code Review Process

1. **Self-review first**
   - Read your own code
   - Test your changes
   - Check for obvious issues

2. **Request review**
   - Tag appropriate reviewers
   - Provide context in PR description
   - Respond to feedback promptly

3. **Address feedback**
   - Make requested changes
   - Add tests if needed
   - Update documentation

## Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Ollama Documentation](https://ollama.ai/docs)

### Tools
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Pytest Documentation](https://docs.pytest.org/)

### Community
- [GitHub Issues](https://github.com/DiffrAI/ai-research-assistant-platform/issues)
- [GitHub Discussions](https://github.com/DiffrAI/ai-research-assistant-platform/discussions)

## Areas for Contribution

### High Priority
- [ ] Add more test coverage
- [ ] Improve error handling
- [ ] Add user profile management
- [ ] Implement password reset
- [ ] Add dark mode to frontend

### Medium Priority
- [ ] Add more LLM providers
- [ ] Improve search functionality
- [ ] Add export formats
- [ ] Implement team features
- [ ] Add mobile responsiveness

### Low Priority
- [ ] Add internationalization
- [ ] Implement advanced analytics
- [ ] Add API rate limiting
- [ ] Create mobile app
- [ ] Add SSO integration

## Thank You

Thank you for contributing to the AI Research Assistant Platform! Your contributions help make this project better for everyone.

If you have any questions or need help getting started, please don't hesitate to reach out through GitHub issues or discussions. 