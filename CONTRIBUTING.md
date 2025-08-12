# Contributing to Enhanced Subject Researcher MCP

Thank you for your interest in contributing to the Enhanced Subject Researcher MCP! This document provides guidelines and information for contributors.

## 🤝 How to Contribute

### Reporting Issues

1. **Search existing issues** first to avoid duplicates
2. **Use issue templates** when available
3. **Provide detailed information**:
   - Clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. **Check the roadmap** in README.md first
2. **Open a discussion** before implementing large features
3. **Describe the use case** and expected behavior
4. **Consider backwards compatibility**

### Code Contributions

#### Development Setup

```bash
# Fork and clone the repository
git clone https://github.com/your-username/subject-researcher-mcp.git
cd subject-researcher-mcp

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest pytest-asyncio ruff build bandit safety
```

#### Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**:
   - Follow the coding standards below
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**:
   ```bash
   # Run linting
   ruff check src/ tests/
   
   # Run formatting check
   ruff format --check src/ tests/
   
   # Run tests
   pytest tests/ -v
   
   # Run security scan
   bandit -r src/
   ```

4. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create a PR**:
   ```bash
   git push origin feature/your-feature-name
   ```

## 📝 Coding Standards

### Python Style

- **Follow PEP 8** style guidelines
- **Use type hints** for all function parameters and returns
- **Add docstrings** for all public functions and classes
- **Keep functions focused** - single responsibility principle
- **Use descriptive variable names**

### Code Structure

```python
"""Module docstring describing the purpose."""

import asyncio
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class ExampleClass:
    """Class docstring with purpose and usage examples."""
    
    def __init__(self, param: str) -> None:
        """Initialize with parameters.
        
        Args:
            param: Description of the parameter
        """
        self.param = param
    
    async def async_method(self, data: Dict[str, str]) -> Optional[List[str]]:
        """Async method with proper typing and docstring.
        
        Args:
            data: Input data dictionary
            
        Returns:
            List of processed strings, or None if processing fails
            
        Raises:
            ValueError: If data is invalid
        """
        try:
            # Implementation here
            return ["result"]
        except Exception as e:
            logger.error(f"Processing failed: {e}")
            return None
```

### Testing Standards

- **Write tests for all new functionality**
- **Maintain >80% code coverage**
- **Use descriptive test names**
- **Include both positive and negative test cases**
- **Mock external dependencies**

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_research_engine_conducts_research_successfully():
    """Test that research engine completes research with valid inputs."""
    engine = ResearchEngine()
    inputs = ResearchInputs(subject="test subject")
    
    with patch.object(engine, '_search_duckduckgo', new=AsyncMock(return_value=[])):
        report = await engine.conduct_iterative_research(inputs)
        
        assert report is not None
        assert len(report.questions) > 0
        assert 0 <= report.confidence <= 1

@pytest.mark.asyncio
async def test_research_engine_handles_search_failure():
    """Test that research engine handles search failures gracefully."""
    engine = ResearchEngine()
    inputs = ResearchInputs(subject="test subject")
    
    with patch.object(engine, '_search_duckduckgo', side_effect=Exception("Search failed")):
        report = await engine.conduct_iterative_research(inputs)
        
        # Should still produce a report with fallback data
        assert report is not None
        assert len(report.limitations) > 0
```

## 🏗️ Architecture Guidelines

### Component Organization

```
src/subject_researcher_mcp/
├── research_engine.py      # Core research logic
├── server.py              # MCP server implementation
├── models/                # Data models and types
├── search/                # Search engine implementations
├── analysis/              # Claim mining and analysis
├── synthesis/             # Report generation
└── utils/                 # Utility functions
```

### Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Use constructor injection for dependencies
3. **Error Handling**: Always handle errors gracefully with proper logging
4. **Async/Await**: Use async patterns for I/O operations
5. **Configuration**: Make behavior configurable through inputs/environment

### Adding New Features

#### New Search Engines

1. Create a new search implementation in `search/`
2. Implement the common search interface
3. Add fallback handling for API failures
4. Include rate limiting and respectful usage
5. Add comprehensive tests

#### New Analysis Methods

1. Add analysis logic to `analysis/`
2. Ensure compatibility with existing claim structure
3. Add confidence scoring
4. Include validation and error handling
5. Document the methodology

## 🧪 Testing Guidelines

### Test Categories

1. **Unit Tests**: Test individual functions and methods
2. **Integration Tests**: Test component interactions
3. **E2E Tests**: Test complete research workflows
4. **Performance Tests**: Validate response times and resource usage

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_research_engine.py -v

# With coverage
pytest tests/ --cov=src/ --cov-report=html

# Performance tests
pytest tests/test_performance.py -v

# E2E tests (may take longer)
pytest tests/test_real_mcp_e2e.py -v
```

### Test Data

- Use realistic but anonymized test data
- Include edge cases and error conditions
- Mock external API calls to ensure reproducibility
- Create reusable test fixtures

## 📚 Documentation

### Required Documentation

1. **Code Comments**: Explain complex logic and algorithms
2. **Docstrings**: Document all public APIs
3. **README Updates**: Update installation and usage instructions
4. **API Documentation**: Update for new endpoints or parameters
5. **Examples**: Provide usage examples for new features

### Documentation Style

- Use clear, concise language
- Include code examples
- Explain the "why" not just the "what"
- Keep examples up-to-date with code changes

## 🔍 Review Process

### Pull Request Requirements

- [ ] All tests pass
- [ ] Code coverage maintained
- [ ] Documentation updated
- [ ] Security scan passes
- [ ] Performance impact assessed
- [ ] Backwards compatibility considered

### Review Criteria

1. **Functionality**: Does it work as intended?
2. **Code Quality**: Is it well-structured and readable?
3. **Testing**: Are there adequate tests?
4. **Performance**: Does it impact system performance?
5. **Security**: Are there any security implications?
6. **Documentation**: Is it properly documented?

## 🚀 Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):

- **MAJOR**: Breaking changes
- **MINOR**: New features, backwards compatible
- **PATCH**: Bug fixes, backwards compatible

### Release Checklist

- [ ] Update version in `pyproject.toml`
- [ ] Update CHANGELOG.md
- [ ] Run full test suite
- [ ] Update documentation
- [ ] Create release tag
- [ ] Deploy to PyPI
- [ ] Update Docker images

## 🆘 Getting Help

- **Documentation**: Check the [GitHub Wiki](https://github.com/your-org/subject-researcher-mcp/wiki)
- **Discussions**: Use [GitHub Discussions](https://github.com/your-org/subject-researcher-mcp/discussions)
- **Issues**: Report bugs in [GitHub Issues](https://github.com/your-org/subject-researcher-mcp/issues)
- **Discord**: Join our [development Discord](https://discord.gg/subject-researcher-dev)

## 🙏 Recognition

Contributors are recognized in:

- README.md contributors section
- Release notes
- Annual contributor spotlight
- Maintainer consideration for significant contributions

Thank you for contributing to the Enhanced Subject Researcher MCP! 🚀