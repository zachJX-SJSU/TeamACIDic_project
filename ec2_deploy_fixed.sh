#!/usr/bin/env bash
set -e

echo "========================================="
echo "HR Portal EC2 Deployment Script"
echo "========================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# MySQL root password - TEAM STANDARD
MYSQL_ROOT_PASSWORD="abc123"

# ================================
# Step 1: System Update
# ================================
echo -e "${GREEN}Step 1: Updating system packages...${NC}"
sudo apt-get update -y

# ================================
# Step 2: Configure MySQL Database
# ================================
echo -e "${GREEN}Step 2: Setting up MySQL database...${NC}"

# Create database and user using existing root password
# TEAM STANDARD: hr_user / abc123
mysql -u root -p"$MYSQL_ROOT_PASSWORD" <<EOF
CREATE DATABASE IF NOT EXISTS employees;
CREATE USER IF NOT EXISTS 'hr_user'@'localhost' IDENTIFIED BY 'abc123';
GRANT ALL PRIVILEGES ON employees.* TO 'hr_user'@'localhost';
FLUSH PRIVILEGES;
EOF

echo -e "${GREEN}MySQL database 'employees' created successfully!${NC}"

# ================================
# Step 3: Install Node.js (if not installed)
# ================================
if ! command -v node &> /dev/null; then
    echo -e "${GREEN}Step 3: Installing Node.js 18.x...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo -e "${GREEN}Step 3: Node.js already installed${NC}"
fi

echo "Node version: $(node --version)"
echo "NPM version: $(npm --version)"

# ================================
# Step 4: Install Python and dependencies
# ================================
echo -e "${GREEN}Step 4: Installing Python and build tools...${NC}"
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
# Step 5: Clone Repository
# ================================
echo -e "${GREEN}Step 5: Cloning TeamACIDic_project repository...${NC}"
cd ~
if [ -d "TeamACIDic_project" ]; then
    echo -e "${YELLOW}Repository already exists. Pulling latest changes...${NC}"
    cd TeamACIDic_project
    git pull
else
    git clone https://github.com/zachJX-SJSU/TeamACIDic_project.git
    cd TeamACIDic_project
fi

PROJECT_DIR="$HOME/TeamACIDic_project"
cd $PROJECT_DIR

# ================================
# Step 6: Setup Python Virtual Environment
# ================================
echo -e "${GREEN}Step 6: Setting up Python virtual environment...${NC}"
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo -e "${GREEN}Installing Python dependencies...${NC}"
pip install -r requirements.txt

# ================================
# Step 7: Import Database Schema
# ================================
echo -e "${GREEN}Step 7: Importing database schema...${NC}"
mysql -u hr_user -pabc123 employees < employees_dev.sql

echo -e "${GREEN}Database schema imported successfully!${NC}"

# Verify tables
echo -e "${YELLOW}Database tables:${NC}"
mysql -u hr_user -pabc123 -e "USE employees; SHOW TABLES;"

# ================================
# Step 8: Create Environment File
# ================================
echo -e "${GREEN}Step 8: Creating .env file...${NC}"
cat > .env << 'ENVEOF'
DATABASE_URL=mysql+pymysql://hr_user:abc123@localhost:3306/employees
ENVEOF

# ================================
# Step 9: Start Backend Service
# ================================
echo -e "${GREEN}Step 9: Starting FastAPI backend...${NC}"

# Kill any existing uvicorn processes
pkill -f uvicorn || true

# Start backend
source .venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 > backend.log 2>&1 &

sleep 3

# Test backend
echo -e "${YELLOW}Testing backend...${NC}"
curl -s http://localhost:8000/ || echo "Backend not responding yet, check backend.log"

# ================================
# Step 10: Setup Frontend
# ================================
echo -e "${GREEN}Step 10: Setting up React frontend...${NC}"
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
    sed -i "s|http://localhost:8000|http://$EC2_PUBLIC_IP:8000|g" src/App.js || true
fi

# Build frontend for production
echo -e "${GREEN}Building frontend for production...${NC}"
npm run build

# Install serve globally if not installed
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
# Step 11: Verification
# ================================
echo -e "${GREEN}Step 11: Verifying deployment...${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}Deployment Complete!${NC}"
echo "========================================="
echo ""
echo -e "${YELLOW}Backend API:${NC} http://$EC2_PUBLIC_IP:8000"
echo -e "${YELLOW}API Docs:${NC} http://$EC2_PUBLIC_IP:8000/docs"
echo -e "${YELLOW}Frontend:${NC} http://$EC2_PUBLIC_IP:3000"
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
echo -e "${GREEN}Share these URLs with your team lead:${NC}"
echo "  Backend: http://$EC2_PUBLIC_IP:8000"
echo "  Frontend: http://$EC2_PUBLIC_IP:3000"
echo "  API Docs: http://$EC2_PUBLIC_IP:8000/docs"
echo "========================================="
