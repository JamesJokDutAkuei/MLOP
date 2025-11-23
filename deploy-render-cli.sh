#!/bin/bash
# 🚀 RENDER DEPLOYMENT VIA CLI
# One-command deployment to Render (no browser clicks needed)

set -e

BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  🚀 RENDER CLI DEPLOYMENT                                ║${NC}"
echo -e "${BLUE}║     Brain Tumor MRI Classifier                           ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Step 1: Check if Render CLI is installed
echo -e "${YELLOW}1️⃣  Checking Render CLI...${NC}"

if ! command -v render &> /dev/null; then
    echo -e "${YELLOW}⚠️  Render CLI not installed. Installing...${NC}"
    
    # Install Render CLI
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        brew tap render-oss/render
        brew install render
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        curl -fsSL https://render.com/install.sh | sh
    else
        echo -e "${RED}❌ Unsupported OS. Please install Render CLI from: https://render.com/docs/cli${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✅ Render CLI ready${NC}"

# Step 2: Check authentication
echo ""
echo -e "${YELLOW}2️⃣  Checking Render authentication...${NC}"

if ! render auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  Not authenticated. Starting auth...${NC}"
    render auth login
fi

echo -e "${GREEN}✅ Authenticated${NC}"

# Step 3: Check if git is configured
echo ""
echo -e "${YELLOW}3️⃣  Checking git setup...${NC}"

if [ -z "$(git remote get-url origin)" ]; then
    echo -e "${RED}❌ No git remote 'origin' configured${NC}"
    echo "Please run first:"
    echo "  git remote add origin https://github.com/YOUR_USERNAME/mlop.git"
    exit 1
fi

GITHUB_URL=$(git remote get-url origin)
echo -e "${GREEN}✅ Git remote: $GITHUB_URL${NC}"

# Step 4: Push to GitHub
echo ""
echo -e "${YELLOW}4️⃣  Pushing code to GitHub...${NC}"

git push -u origin main 2>/dev/null || echo -e "${YELLOW}⚠️  Already up to date${NC}"

echo -e "${GREEN}✅ Code on GitHub${NC}"

# Step 5: Create/Deploy API service
echo ""
echo -e "${YELLOW}5️⃣  Deploying API service...${NC}"

render deploy \
  --name mlop-api \
  --type web \
  --repo "$GITHUB_URL" \
  --region us-west \
  --instance-type free \
  --dockerfile deploy/Dockerfile.api \
  --env PORT=8000 \
  --env PYTHON_UNBUFFERED=1

API_URL=$(render services describe mlop-api --format json | jq -r '.url')
echo -e "${GREEN}✅ API deployed: $API_URL${NC}"

# Step 6: Create/Deploy UI service
echo ""
echo -e "${YELLOW}6️⃣  Deploying UI service...${NC}"

render deploy \
  --name mlop-ui \
  --type web \
  --repo "$GITHUB_URL" \
  --region us-west \
  --instance-type free \
  --dockerfile deploy/Dockerfile.ui \
  --env PORT=8501 \
  --env GCP_API_URL="$API_URL" \
  --env DOCKER_ENV=true \
  --env STREAMLIT_SERVER_HEADLESS=true

UI_URL=$(render services describe mlop-ui --format json | jq -r '.url')
echo -e "${GREEN}✅ UI deployed: $UI_URL${NC}"

# Step 7: Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║            ✅ DEPLOYMENT COMPLETE!                        ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}🎉 Your app is LIVE!${NC}"
echo ""
echo -e "${YELLOW}📱 Streamlit UI:${NC}"
echo "   $UI_URL"
echo ""
echo -e "${YELLOW}📚 API Documentation:${NC}"
echo "   $API_URL/docs"
echo ""
echo -e "${YELLOW}💰 Cost: FREE (free tier)${NC}"
echo ""
echo "Next steps:"
echo "1. Wait 2-3 minutes for services to start"
echo "2. Open the UI URL in your browser"
echo "3. Upload a brain MRI image to test"
echo "4. Share URLs with instructors"
echo ""
echo -e "${GREEN}Good luck! 🚀${NC}"
