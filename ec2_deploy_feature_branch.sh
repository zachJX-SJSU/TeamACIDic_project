#!/usr/bin/env bash
set -e

echo "========================================="
echo "HR Portal EC2 Deployment Script"
echo "Feature Branch: pratham-13-and-14-login-change-password-clean"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Branch to deploy
BRANCH_NAME="pratham-13-and-14-login-change-password-clean"

# ================================
# Step 1: System Update
# ================================
echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update -y
sudo apt-get upgrade -y

# ================================
# Step 2: Install MySQL Server
# ================================
echo -e "${GREEN}Step 2: Installing MySQL Server...${NC}"
sudo apt-get install -y mysql-server

# Start MySQL service
sudo systemctl start mysql
sudo systemctl enable mysql

# ================================
# Step 3: Configure MySQL Database
# ================================
echo -e "${GREEN}Step 3: Setting up MySQL database...${NC}"

# Set MySQL root password and create database
# TEAM STANDARD: hr_user / abc123
sudo mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'abc123';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS employees;
CREATE USER IF NOT EXISTS 'hr_user'@'localhost' IDENTIFIED BY 'abc123';
GRANT ALL PRIVILEGES ON employees.* TO 'hr_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${GREEN}MySQL database 'employees' created successfully!${NC}"

# ================================
# Step 4: Install Node.js
# ================================
echo -e "${GREEN}Step 4: Installing Node.js 18.x...${NC}"
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# ================================
# Step 5: Install Python and dependencies
# ================================
echo -e "${GREEN}Step 5: Installing Python and build tools...${NC}"
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    git \
    curl \
    wget

# ================================
# Step 6: Clone Repository
# ================================
echo -e "${GREEN}Step 6: Cloning TeamACIDic_project repository...${NC}"
cd ~
if [ -d "TeamACIDic_project" ]; then
    echo -e "${YELLOW}Repository already exists. Fetching and checking out branch...${NC}"
    cd TeamACIDic_project
    git fetch origin
    git checkout $BRANCH_NAME
    git pull origin $BRANCH_NAME
else
    git clone https://github.com/zachJX-SJSU/TeamACIDic_project.git
    cd TeamACIDic_project
    git checkout $BRANCH_NAME
fi

PROJECT_DIR="$HOME/TeamACIDic_project"
cd $PROJECT_DIR

echo -e "${YELLOW}Current branch: $(git branch --show-current)${NC}"

# ================================
# Step 7: Setup Python Virtual Environment
# ================================
echo -e "${GREEN}Step 7: Setting up Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# ================================
# Step 8: Import Database Schema
# ================================
echo -e "${GREEN}Step 8: Importing database schema...${NC}"
mysql -u hr_user -pabc123 employees < employees_dev.sql

echo -e "${GREEN}Database schema imported successfully!${NC}"

# Verify tables
echo -e "${YELLOW}Database tables:${NC}"
mysql -u hr_user -pabc123 -e "USE employees; SHOW TABLES;"

# ================================
# Step 9: Create Environment File
# ================================
echo -e "${GREEN}Step 9: Creating .env file...${NC}"
cat > .env << 'ENVEOF'
DATABASE_URL=mysql+pymysql://hr_user:abc123@localhost:3306/employees
ENVEOF

# ================================
# Step 10: Start Backend Service
# ================================
echo -e "${GREEN}Step 10: Starting FastAPI backend...${NC}"

# Kill any existing uvicorn processes
pkill -f uvicorn || true

# Start backend
source .venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > backend.log 2>&1 &

sleep 5

# Test backend
echo -e "${YELLOW}Testing backend...${NC}"
if curl -s http://localhost:8000/ > /dev/null; then
    echo -e "${GREEN}Backend is responding!${NC}"
else
    echo -e "${RED}Backend not responding yet, check backend.log${NC}"
    tail -20 backend.log
fi

# ================================
# Step 11: Verify Frontend Directory
# ================================
echo -e "${GREEN}Step 11: Checking for frontend directory...${NC}"

if [ ! -d "$PROJECT_DIR/frontend" ]; then
    echo -e "${RED}ERROR: frontend directory not found!${NC}"
    echo -e "${RED}Current branch: $(git branch --show-current)${NC}"
    echo -e "${RED}Available directories:${NC}"
    ls -la $PROJECT_DIR
    echo -e "${RED}Deployment cannot continue without frontend.${NC}"
    exit 1
fi

echo -e "${GREEN}Frontend directory found!${NC}"

# ================================
# Step 12: Setup Frontend
# ================================
echo -e "${GREEN}Step 12: Setting up React frontend...${NC}"
cd $PROJECT_DIR/frontend

# Install frontend dependencies
echo -e "${GREEN}Installing frontend dependencies (this may take a few minutes)...${NC}"
npm install

# Get EC2 public IP
EC2_PUBLIC_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo -e "${YELLOW}EC2 Public IP: $EC2_PUBLIC_IP${NC}"

# Update API endpoint in frontend (if App.js exists and uses localhost)
if [ -f "src/App.js" ]; then
    echo -e "${GREEN}Updating API endpoint in frontend...${NC}"
    # Backup original
    cp src/App.js src/App.js.backup
    # Replace localhost with EC2 IP
    sed -i "s|http://localhost:8000|http://$EC2_PUBLIC_IP:8000|g" src/App.js
    echo -e "${YELLOW}Updated API endpoint to: http://$EC2_PUBLIC_IP:8000${NC}"
fi

# Build frontend for production
echo -e "${GREEN}Building frontend for production...${NC}"
npm run build

# Install serve globally
if ! command -v serve &> /dev/null; then
    sudo npm install -g serve
fi

# Kill any existing serve processes
pkill -f "serve" || true

# Start frontend
echo -e "${GREEN}Starting frontend server...${NC}"
nohup serve -s build -l 3000 > frontend.log 2>&1 &

sleep 3

# ================================
# Step 13: Verification
# ================================
echo -e "${GREEN}Step 13: Verifying deployment...${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo -e "${YELLOW}Branch Deployed:${NC} $BRANCH_NAME"
echo -e "${YELLOW}Backend API:${NC} http://$EC2_PUBLIC_IP:8000"
echo -e "${YELLOW}API Docs:${NC} http://$EC2_PUBLIC_IP:8000/docs"
echo -e "${YELLOW}Frontend:${NC} http://$EC2_PUBLIC_IP:3000"
echo ""
echo -e "${YELLOW}Database Credentials:${NC}"
echo "  Username: hr_user"
echo "  Password: abc123"
echo "  Database: employees"
echo ""
echo -e "${YELLOW}Test endpoints:${NC}"
echo "  curl http://$EC2_PUBLIC_IP:8000/"
echo "  curl http://$EC2_PUBLIC_IP:3000/"
echo ""
echo -e "${YELLOW}View logs:${NC}"
echo "  Backend: tail -f $PROJECT_DIR/backend.log"
echo "  Frontend: tail -f $PROJECT_DIR/frontend/frontend.log"
echo ""
echo -e "${YELLOW}Process status:${NC}"
ps aux | grep -E "uvicorn|serve" | grep -v grep
echo ""
echo "========================================="
echo -e "${GREEN}Share these with your team lead:${NC}"
echo "  IP: $EC2_PUBLIC_IP"
echo "  Backend: http://$EC2_PUBLIC_IP:8000"
echo "  Frontend: http://$EC2_PUBLIC_IP:3000"
echo "  API Docs: http://$EC2_PUBLIC_IP:8000/docs"
echo "========================================="
