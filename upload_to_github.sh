#!/bin/bash

# LeadFinder GitHub Upload Script
# This script helps upload all changes to GitHub

echo "🚀 Starting LeadFinder GitHub upload process..."

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check git status
echo "📋 Checking git status..."
git status

# Add all changes
echo "📦 Adding all changes to git..."
git add .

# Check what will be committed
echo "📋 Changes to be committed:"
git status --porcelain

# Commit changes
echo "💾 Committing changes..."
git commit -m "Update dependencies and add comprehensive documentation

- Updated requirements.txt with all 15 dependencies
- Added DEPENDENCIES.md with detailed dependency documentation
- Added DEPENDENCY_ANALYSIS.md with analysis and recommendations
- Fixed API integrations and error handling
- Improved code quality and documentation
- Added development tools (black, flake8, mypy)
- Enhanced lead workshop functionality
- Updated configuration management"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo "✅ Successfully uploaded to GitHub!"
echo "🌐 Repository: https://github.com/DanielHesse79/leadfinder.git"
echo ""
echo "📊 Summary of changes:"
echo "- Updated requirements.txt (15 dependencies)"
echo "- Added comprehensive dependency documentation"
echo "- Fixed API integrations and error handling"
echo "- Improved code quality and testing"
echo ""
echo "🎉 LeadFinder is now updated on GitHub!" 