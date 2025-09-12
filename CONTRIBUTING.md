# Contributing to Banana AI Prompt Expander

Thank you for your interest in contributing! Here's how you can help:

## Getting Started

1. **Fork the repository**
2. **Clone your fork**
   ```bash
   git clone https://github.com/your-username/banana-ai-prompt-expander.git
   cd banana-ai-prompt-expander
   ```

3. **Set up development environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

## Development Workflow

### Code Style
- Use **Black** for code formatting: `black .`
- Use **flake8** for linting: `flake8 .`
- Use **isort** for import sorting: `isort .`

### Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bananaai --cov-report=html

# Run specific test
pytest tests/test_basic.py -v
```

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow existing code patterns
   - Add tests for new functionality
   - Update documentation if needed

3. **Run tests and linting**
   ```bash
   black .
   flake8 .
   pytest
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: your feature description"
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

## Areas for Contribution

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🧪 **Test coverage**
- 🎨 **UI/UX enhancements**
- 🔧 **Performance optimizations**

## Code Guidelines

### Python Code
- Follow PEP 8 standards
- Use type hints where beneficial
- Write docstrings for public functions
- Keep functions focused and small

### Frontend Code
- Use vanilla JavaScript (no frameworks)
- Follow existing CSS patterns
- Ensure responsive design
- Test in multiple browsers

### API Design
- Follow REST principles
- Use proper HTTP status codes
- Provide clear error messages
- Document all endpoints

## Pull Request Process

1. **Describe your changes** clearly in the PR description
2. **Reference any related issues**
3. **Ensure all tests pass**
4. **Update documentation** if needed
5. **Request review** from maintainers

## Questions or Issues?

- 📫 **Open an issue** for bug reports
- 💬 **Start a discussion** for feature ideas
- 📧 **Contact maintainers** for other questions

Thank you for contributing! 🎉