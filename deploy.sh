#!/bin/bash

# Setupia AI Saver - Quick Deployment Script

echo "🚀 Setupia AI Saver - Deploy to Railway"
echo "======================================"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
    git add .
    git commit -m "Initial commit - Setupia AI Saver"
else
    echo "✅ Git repository already initialized"
fi

# Check for GitHub remote
if ! git remote | grep -q "origin"; then
    echo ""
    echo "📋 Next steps:"
    echo "1. Create GitHub repository at: https://github.com/new"
    echo "2. Name it: setupia-ai-saver"
    echo "3. Run: git remote add origin https://github.com/YOUR_USERNAME/setupia-ai-saver"
    echo "4. Run: git push -u origin main"
    echo ""
    echo "5. Then deploy on Railway:"
    echo "   - Go to: https://railway.app"
    echo "   - Sign up with GitHub"
    echo "   - Click 'Deploy from GitHub'"
    echo "   - Select 'setupia-ai-saver'"
    echo "   - Add environment variable: BOT_TOKEN=your_token"
    echo "   - Click Deploy!"
else
    echo "✅ GitHub remote configured"
    echo "📤 Pushing to GitHub..."
    git add .
    git commit -m "Deploy: $(date)"
    git push origin main
    
    echo ""
    echo "🎉 Code pushed to GitHub!"
    echo "🌐 Now deploy on Railway:"
    echo "   - Go to: https://railway.app"
    echo "   - Deploy from your GitHub repo"
    echo "   - Add BOT_TOKEN environment variable"
fi

echo ""
echo "📱 After deployment, your bot will be available 24/7 on your phone!"
