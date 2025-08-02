#!/bin/bash
# PersonalAgent GitHub Deployment Script
# Comprehensive deployment strategy for open source release

set -e  # Exit on any error

echo "🚀 PersonalAgent GitHub Deployment Strategy"
echo "============================================="

# Phase 1: Pre-deployment checks
echo ""
echo "📋 Phase 1: Pre-deployment Validation"
echo "------------------------------------"

# Check if we're in the right directory
if [ ! -f "README.md" ] || [ ! -d "src" ]; then
    echo "❌ Please run this script from the PersonalAgent root directory"
    exit 1
fi

echo "✅ Directory structure verified"

# Run security audit
echo "🔒 Running security audit..."
if source venv/bin/activate && python3 src/utils/security_audit.py > /dev/null 2>&1; then
    echo "✅ Security audit passed"
else
    echo "⚠️ Security audit found issues - review before deployment"
    echo "   Run: python3 src/utils/security_audit.py"
fi

# Run compatibility test
echo "🌍 Running compatibility test..."
if source venv/bin/activate && python3 src/utils/cross_platform_test.py > /dev/null 2>&1; then
    echo "✅ Platform compatibility verified"
else
    echo "⚠️ Compatibility issues found - review before deployment"
    echo "   Run: python3 src/utils/cross_platform_test.py"
fi

# Check for sensitive files
echo "🔍 Checking for sensitive files..."
if [ -f "config/credentials.json" ]; then
    echo "⚠️ Found config/credentials.json - ensure it's in .gitignore"
fi

if [ -f ".env" ] && grep -q "API_KEY" .env 2>/dev/null; then
    echo "⚠️ Found API keys in .env - ensure it's in .gitignore"
fi

echo "✅ Pre-deployment checks complete"

# Phase 2: Repository preparation
echo ""
echo "📦 Phase 2: Repository Preparation"
echo "----------------------------------"

# Initialize git if not already done
if [ ! -d ".git" ]; then
    echo "🔧 Initializing git repository..."
    git init
    echo "✅ Git repository initialized"
else
    echo "✅ Git repository already exists"
fi

# Check git status
echo "📊 Current git status:"
git status --porcelain | head -10

# Phase 3: GitHub CLI authentication
echo ""
echo "🔑 Phase 3: GitHub Authentication"
echo "--------------------------------"

echo "Please authenticate with GitHub CLI when prompted..."
echo "This will open your browser for OAuth authentication"

# Phase 4: Repository creation
echo ""
echo "🏗️ Phase 4: Repository Creation"
echo "-------------------------------"

echo "We will create the repository with the following settings:"
echo "  Name: personalagent"
echo "  Description: Priority-based calendar management with AI-powered task automation"
echo "  Visibility: Public"
echo "  License: MIT"

echo ""
echo "📝 Repository Topics that will be added:"
echo "  - calendar-management"
echo "  - priority-scheduling"
echo "  - ai-automation"
echo "  - family-first"
echo "  - productivity"
echo "  - google-calendar"
echo "  - multi-llm"
echo "  - command-line"
echo "  - python"
echo "  - calendar"

echo ""
echo "Ready to proceed with deployment?"
echo "Press Enter to continue, or Ctrl+C to abort..."
read -r

# The actual deployment commands will be shown as instructions
echo ""
echo "🚀 DEPLOYMENT COMMANDS"
echo "====================="
echo ""
echo "Run these commands in sequence:"
echo ""

cat << 'EOF'
# 1. Authenticate with GitHub
gh auth login

# 2. Create the repository
gh repo create personalagent \
  --public \
  --description "Priority-based calendar management with AI-powered task automation. Family events take priority, work adapts to life." \
  --homepage "https://github.com/macizomedia/personalagent" \
  --clone=false

# 3. Add repository topics
gh repo edit personalagent \
  --add-topic calendar-management \
  --add-topic priority-scheduling \
  --add-topic ai-automation \
  --add-topic family-first \
  --add-topic productivity \
  --add-topic google-calendar \
  --add-topic multi-llm \
  --add-topic command-line \
  --add-topic python \
  --add-topic calendar

# 4. Set up repository settings
gh repo edit personalagent \
  --enable-issues \
  --enable-wiki \
  --enable-projects \
  --allow-update-branch

# 5. Add the remote and push
git remote add origin https://github.com/$(gh api user --jq .login)/personalagent.git
git branch -M main
git add .
git commit -m "🎉 Initial release: PersonalAgent v1.0.0

✨ Features:
- Priority-based calendar management (Family > Personal > Work)
- AI-powered task automation with 200+ LLM models
- Intelligent conflict resolution and scheduling
- Secure encrypted credential storage
- Cross-platform compatibility
- Comprehensive CLI interface with 60+ aliases

🔒 Security:
- Encrypted API key storage with Fernet encryption
- Comprehensive security audit framework
- Secure file permissions and .gitignore configuration

🌍 Compatibility:
- Cross-platform testing framework
- Python 3.8+ support
- Shell compatibility (zsh, bash, fish)
- Automated setup and installation

📦 Ready for production use and community contributions!"

git push -u origin main

# 6. Create release
gh release create v1.0.0 \
  --title "PersonalAgent v1.0.0 - Priority-Based Calendar Management" \
  --notes-file V1_0_0_RELEASE_SUMMARY.md \
  --latest

# 7. Set up repository protection (optional)
gh api repos/:owner/personalagent/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"contexts":[]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field restrictions=null

EOF

echo ""
echo "📋 POST-DEPLOYMENT CHECKLIST"
echo "============================"
echo ""
echo "After running the above commands:"
echo ""
echo "1. 🌐 Visit your repository on GitHub"
echo "2. 📝 Verify the README.md displays correctly"
echo "3. 🏷️ Check that all topics are applied"
echo "4. 📋 Enable GitHub Pages (optional) for documentation"
echo "5. 🔧 Set up GitHub Actions for CI/CD (future enhancement)"
echo "6. 👥 Add collaborators if needed"
echo "7. 📊 Monitor repository insights and traffic"
echo "8. 🐛 Set up issue templates for bug reports and features"
echo ""

echo "✅ Deployment script preparation complete!"
echo ""
echo "Your PersonalAgent project is ready for GitHub deployment!"
echo "Follow the commands above to publish your open source project."
