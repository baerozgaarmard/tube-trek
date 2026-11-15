# Contributing to Tube Trek

Thanks for your interest in contributing to Tube Trek! Here's how to get involved.

## Reporting bugs

Open an issue on GitHub with:
- Your OS and Python version
- The exact error message / traceback
- Steps to reproduce

## Submitting a pull request

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Make your changes — keep them focused on a single improvement
4. Test locally: run `pytest` to ensure all tests pass
5. Commit with a clear message: `git commit -m "Add: short description"`
6. Push and open a PR against `main`

## Code style

- Python: follow PEP 8, minimal dependencies, standard library preferred
- Keep functions small and single-purpose
- Do not commit API keys, tokens, or video binary artifacts
