# Contributing to Browser Native Python Client

We love contributions! Here's how you can help.

## Development Setup

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/browsernative-python.git
   cd browsernative-python
   ```

3. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest tests/
```

With coverage:
```bash
pytest tests/ --cov=browsernative --cov-report=html
```

## Code Style

We use Black for code formatting:
```bash
black browsernative/
```

Run flake8 for linting:
```bash
flake8 browsernative/
```

## Making Changes

1. Create a new branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and write tests

3. Run tests and ensure they pass

4. Commit your changes:
   ```bash
   git commit -m "feat: add amazing feature"
   ```

5. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a Pull Request

## Commit Message Format

We follow conventional commits:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `test:` Test additions or changes
- `chore:` Maintenance tasks

## Reporting Issues

- Use GitHub Issues
- Include Python version and OS
- Provide minimal reproducible example
- Include full error messages

## Questions?

Open an issue or discussion on GitHub!