#!/bin/bash

# Build script for Browser Native Python Client

echo "🏗️  Building Browser Native Python Client for PyPI..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info

# Build the package
echo "Building package..."
python3 -m build

# Check the distribution
echo -e "\n📦 Distribution files:"
ls -la dist/

echo -e "\n✅ Package built successfully!"
echo -e "\nTo upload to PyPI:"
echo "  python3 -m twine upload dist/*"
echo -e "\nTo upload to Test PyPI first:"
echo "  python3 -m twine upload --repository testpypi dist/*"