#!/bin/bash
# Push to GitHub using Personal Access Token
# Usage: ./push_with_token.sh YOUR_TOKEN

if [ -z "$1" ]; then
    echo "Usage: ./push_with_token.sh YOUR_GITHUB_TOKEN"
    echo ""
    echo "Get a token at: https://github.com/settings/tokens"
    exit 1
fi

TOKEN=$1
cd "$(dirname "$0")"

git push https://${TOKEN}@github.com/samettemurcin/Sunnydata_edu.git main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Successfully pushed to GitHub!"
else
    echo ""
    echo "❌ Push failed. Check your token and try again."
fi
