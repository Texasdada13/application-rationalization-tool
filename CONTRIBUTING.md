# Contributing to Application Rationalization Assessment Tool

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards others

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Basic understanding of application portfolio management

### Find an Issue

1. Browse open issues on GitHub
2. Look for issues tagged with `good first issue` for beginners
3. Comment on the issue to express interest
4. Wait for assignment or approval before starting work

## Development Setup

1. **Fork the repository**

```bash
# Click 'Fork' on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/application-rationalization-tool.git
cd application-rationalization-tool
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. **Create a feature branch**

```bash
git checkout -b feature/your-feature-name
```

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

1. **Bug Fixes**
   - Fix identified bugs
   - Add tests to prevent regression

2. **New Features**
   - Implement requested features
   - Propose new capabilities

3. **Documentation**
   - Improve README, guides, or code comments
   - Add examples and tutorials

4. **Testing**
   - Write unit tests
   - Add integration tests
   - Improve test coverage

5. **Performance**
   - Optimize code
   - Reduce resource usage

6. **Code Quality**
   - Refactor code
   - Improve readability
   - Add type hints

## Coding Standards

### Python Style

Follow PEP 8 guidelines:

```bash
# Check code style
flake8 src/

# Format code
black src/

# Type checking
mypy src/
```

### Code Structure

- **Modularity**: Keep functions and classes focused on a single responsibility
- **Naming**: Use descriptive names for variables, functions, and classes
- **Comments**: Add comments for complex logic
- **Docstrings**: Include docstrings for all public functions and classes

### Example

```python
def calculate_composite_score(
    business_value: float,
    tech_health: float,
    cost: float
) -> float:
    """
    Calculate composite score based on weighted criteria.

    Args:
        business_value: Business value score (0-10)
        tech_health: Technical health score (0-10)
        cost: Annual cost in dollars

    Returns:
        Composite score from 0-100

    Raises:
        ValueError: If inputs are out of valid ranges
    """
    # Implementation here
    pass
```

### Type Hints

Always use type hints:

```python
from typing import List, Dict, Optional

def process_applications(
    apps: List[Dict],
    threshold: Optional[float] = None
) -> List[Dict]:
    ...
```

## Testing

### Writing Tests

Place tests in the `tests/` directory:

```python
# tests/test_scoring_engine.py
import pytest
from src.scoring_engine import ScoringEngine

def test_calculate_composite_score():
    engine = ScoringEngine()
    score = engine.calculate_composite_score(
        business_value=8.0,
        tech_health=7.0,
        cost=50000,
        usage=500,
        security=8.0,
        strategic_fit=9.0,
        redundancy=0
    )
    assert 70 <= score <= 90
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test
pytest tests/test_scoring_engine.py
```

### Test Coverage

Aim for at least 80% code coverage for new features.

## Documentation

### Code Documentation

- Add docstrings to all public functions and classes
- Include examples in docstrings where helpful
- Document parameters, return values, and exceptions

### User Documentation

- Update README.md for user-facing changes
- Add/update guides in the `docs/` directory
- Include usage examples

### Changelog

Update CHANGELOG.md (if exists) with:
- Feature additions
- Bug fixes
- Breaking changes
- Deprecations

## Pull Request Process

### Before Submitting

1. **Update your branch**

```bash
git fetch origin
git rebase origin/main
```

2. **Run tests**

```bash
pytest
```

3. **Check code quality**

```bash
flake8 src/
black --check src/
mypy src/
```

4. **Update documentation**
   - Update relevant docs
   - Add/update examples

### Commit Messages

Write clear, descriptive commit messages:

```
feat: Add support for custom scoring weights

- Implement ScoringWeights dataclass
- Add validation for weight sum
- Update documentation with examples

Closes #123
```

**Commit message format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Code refactoring

## Testing
Describe testing performed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] All tests passing
- [ ] No new warnings
```

### Review Process

1. Maintainers will review your PR
2. Address any feedback or requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

## Development Workflow

### Typical Workflow

1. Create an issue (or find existing one)
2. Fork and clone the repository
3. Create a feature branch
4. Make your changes
5. Add tests
6. Update documentation
7. Commit changes
8. Push to your fork
9. Create a pull request
10. Respond to review feedback
11. Merge (by maintainer)

### Branch Naming

Use descriptive branch names:

```
feature/add-custom-weights
fix/csv-parsing-error
docs/update-workflow-guide
refactor/scoring-engine
```

## Questions?

- Open an issue for questions
- Join discussions in GitHub Discussions
- Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes
- Project documentation

Thank you for contributing to the Application Rationalization Assessment Tool!

---

**Last Updated**: November 2025
