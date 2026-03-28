# Contributing to devkit

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

```bash
# Fork and clone the repo
git clone https://github.com/yourusername/devkit.git
cd devkit

# Install in development mode with all optional deps
pip install -e ".[all]"
pip install -r requirements-dev.txt

# Run tests
pytest tests/ -v
```

## Making Changes

1. Create a branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Write tests for new functionality
4. Run the test suite: `pytest tests/ -v`
5. Run linting: `ruff check devkit/ tests/`
6. Commit with a descriptive message

## Code Standards

- Type hints on all public function signatures
- Docstrings for all public functions
- No hardcoded paths or personal data
- Use `click.echo()` in CLI code, `logging` in library code
- Lazy imports for optional dependencies

## Adding a New Tool

1. Create your module in the appropriate category (`devkit/<category>/`)
2. Add CLI command in `devkit/cli.py` under the relevant command group
3. Write tests in `tests/test_<category>.py`
4. Update `devkit/<category>/__init__.py` with public exports
5. Add documentation to README.md

## Pull Requests

- Keep PRs focused on a single change
- Include tests for new features
- Update documentation if needed
- Reference any related issues

## Reporting Issues

Please include:
- Python version (`python --version`)
- devkit version (`devkit --version`)
- Operating system
- Steps to reproduce
- Expected vs actual behavior

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
