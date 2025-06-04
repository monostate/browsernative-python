# Publishing to PyPI

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token at https://pypi.org/manage/account/token/
3. Install build tools: `pip install build twine`

## Publishing Steps

1. **Build the package:**
   ```bash
   python -m build
   ```

2. **Check the package:**
   ```bash
   twine check dist/*
   ```

3. **Upload to PyPI:**
   ```bash
   # Using environment variable
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=your-pypi-api-token
   twine upload dist/*
   
   # Or interactively
   twine upload dist/*
   # Username: __token__
   # Password: your-pypi-api-token
   ```

## Testing on Test PyPI First

1. Upload to Test PyPI:
   ```bash
   twine upload --repository testpypi dist/*
   ```

2. Test installation:
   ```bash
   pip install --index-url https://test.pypi.org/simple/ browsernative
   ```

## After Publishing

Users can install with:
```bash
pip install browsernative
```

## Version Updates

1. Update version in `browsernative/__init__.py`
2. Update version in `setup.py` and `pyproject.toml`
3. Update CHANGELOG.md
4. Create git tag: `git tag v1.0.1`
5. Push tags: `git push --tags`
6. Build and upload new version