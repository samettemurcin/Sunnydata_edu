#!/bin/bash

# Script to push to GitHub
# This will prompt you for your GitHub credentials

echo "🚀 Pushing to GitHub..."
echo ""
echo "You'll be prompted for:"
echo "  - Username: Your GitHub username"
echo "  - Password: Use a Personal Access Token (NOT your password)"
echo ""
echo "Don't have a token? Get one at: https://github.com/settings/tokens"
echo ""

cd "$(dirname "$0")"

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
    echo "📦 View your repository at: https://github.com/samettemurcin/Sunnydata_edu"
else
    echo ""
    echo "❌ Push failed. Make sure you have:"
    echo "   1. A valid GitHub Personal Access Token"
    echo "   2. Access to the repository"
    echo ""
    echo "Get a token at: https://github.com/settings/tokens"
fi

