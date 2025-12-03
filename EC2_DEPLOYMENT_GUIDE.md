# EC2 Deployment Guide - TeamACIDic HR Portal

## Quick Start for Team Lead

**After deployment, share these with your team lead:**
- **Backend API:** `http://<YOUR_EC2_IP>:8000`
- **Frontend UI:** `http://<YOUR_EC2_IP>:3000`
- **API Docs:** `http://<YOUR_EC2_IP>:8000/docs`

---

## Prerequisites

### 1. Launch EC2 Instance
1. Go to AWS Console → EC2 → Launch Instance
2. **AMI:** Ubuntu Server 22.04 LTS
3. **Instance Type:** t2.medium or larger (recommended for demo)
4. **Key Pair:** Create/select your SSH key pair
5. **Security Group:** Configure the following inbound rules:
   - SSH (22) - Your IP
   - HTTP (80) - Anywhere (0.0.0.0/0)
   - Custom TCP (8000) - Anywhere (0.0.0.0/0) - Backend API
   - Custom TCP (3000) - Anywhere (0.0.0.0/0) - Frontend
6. **Storage:** 20 GB minimum

### 2. Connect to Your EC2 Instance
```bash
ssh -i "your-key.pem" ubuntu@<YOUR_EC2_PUBLIC_IP>
```

---

## Deployment Steps

### Option 1: Automated Deployment (RECOMMENDED)

Once connected to EC2, run:

```bash
# Download and run the deployment script
curl -O https://raw.githubusercontent.com/zachJX-SJSU/TeamACIDic_project/main/ec2_deploy.sh
chmod +x ec2_deploy.sh
./ec2_deploy.sh
```

**OR** if you prefer the fixed version (for existing MySQL):

```bash
curl -O https://raw.githubusercontent.com/zachJX-SJSU/TeamACIDic_project/main/ec2_deploy_fixed.sh
chmod +x ec2_deploy_fixed.sh
./ec2_deploy_fixed.sh
```

The script will:
1. Update system packages
2. Install MySQL, Node.js, Python
3. Clone your repository
4. Set up database with schema
5. Install all dependencies
6. Start backend on port 8000
7. Build and start frontend on port 3000
8. Display your EC2 IP and URLs

**Total time:** ~10-15 minutes

### Option 2: Manual Deployment

If you need to deploy manually or troubleshoot:

#### Step 1: System Setup
```bash
sudo apt-get update -y
sudo apt-get upgrade -y

# Install MySQL
sudo apt-get install -y mysql-server
sudo systemctl start mysql
sudo systemctl enable mysql
```

#### Step 2: Configure MySQL
```bash
# Set root password and create database
# TEAM STANDARD CREDENTIALS: hr_user / abc123
sudo mysql <<EOF
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'abc123';
FLUSH PRIVILEGES;
CREATE DATABASE IF NOT EXISTS employees;
CREATE USER IF NOT EXISTS 'hr_user'@'localhost' IDENTIFIED BY 'abc123';
GRANT ALL PRIVILEGES ON employees.* TO 'hr_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

#### Step 3: Install Node.js
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
node --version
npm --version
```

#### Step 4: Install Python Dependencies
```bash
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    build-essential \
    pkg-config \
    default-libmysqlclient-dev \
    git
```

#### Step 5: Clone Repository
```bash
cd ~
git clone https://github.com/zachJX-SJSU/TeamACIDic_project.git
cd TeamACIDic_project
```

#### Step 6: Setup Backend
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file
cat > .env << 'EOF'
DATABASE_URL=mysql+pymysql://hr_user:abc123@localhost:3306/employees
EOF

# Import database schema
mysql -u hr_user -pabc123 employees < employees_dev.sql

# Start backend
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > backend.log 2>&1 &
```

#### Step 7: Setup Frontend
```bash
cd ~/TeamACIDic_project/frontend

# Install dependencies
npm install

# Get EC2 public IP
EC2_IP=$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)
echo "Your EC2 IP: $EC2_IP"

# Update API endpoint in frontend
sed -i "s|http://localhost:8000|http://$EC2_IP:8000|g" src/App.js

# Build for production
npm run build

# Install and start serve
sudo npm install -g serve
nohup serve -s build -l 3000 > frontend.log 2>&1 &
```

---

## Getting Your IP and Port Information

### Method 1: From EC2 Console
1. Go to AWS Console → EC2 → Instances
2. Find your instance
3. Copy "Public IPv4 address"
4. Ports: Backend=8000, Frontend=3000

### Method 2: From EC2 Instance
```bash
# Get public IP
curl http://169.254.169.254/latest/meta-data/public-ipv4

# Or
curl ifconfig.me
```

### Method 3: From Deployment Script Output
The deployment script will display:
```
========================================
Backend API: http://<YOUR_IP>:8000
Frontend: http://<YOUR_IP>:3000
API Docs: http://<YOUR_IP>:8000/docs
========================================
```

---

## Quick Message Template for Team Lead

Copy and send this to your team lead after deployment:

```
Hi [Team Lead Name],

EC2 is up and running! Here are the details:

🔹 EC2 Public IP: <YOUR_EC2_IP>

🔹 Backend API (Port 8000):
   http://<YOUR_EC2_IP>:8000

🔹 Frontend UI (Port 3000):
   http://<YOUR_EC2_IP>:3000

🔹 API Documentation:
   http://<YOUR_EC2_IP>:8000/docs

The application includes:
- Login functionality
- Change password feature
- Full authentication flow
- React frontend integrated with FastAPI backend

All features from PR #19 are deployed and ready for testing.
```

---

## Verification & Testing

### 1. Check Backend
```bash
# From EC2
curl http://localhost:8000/

# From anywhere
curl http://<YOUR_EC2_IP>:8000/
```

Should return: `{"message":"Hello from the Employee Portal"}`

### 2. Check Frontend
Open in browser:
```
http://<YOUR_EC2_IP>:3000
```

You should see the login page.

### 3. Test API Endpoints
```bash
# List all departments
curl http://<YOUR_EC2_IP>:8000/api/departments

# Check API docs
Open: http://<YOUR_EC2_IP>:8000/docs
```

### 4. Check Logs
```bash
# Backend logs
tail -f ~/TeamACIDic_project/backend.log

# Frontend logs
tail -f ~/TeamACIDic_project/frontend/frontend.log
```

### 5. Check Running Processes
```bash
ps aux | grep -E "uvicorn|serve"
```

Should show:
- `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- `serve -s build -l 3000`

---

## Troubleshooting

### Backend Not Starting
```bash
# Check logs
cat ~/TeamACIDic_project/backend.log

# Check if port 8000 is in use
sudo lsof -i :8000

# Restart backend
cd ~/TeamACIDic_project
source .venv/bin/activate
pkill -f uvicorn
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
```

### Frontend Not Starting
```bash
# Check logs
cat ~/TeamACIDic_project/frontend/frontend.log

# Check if port 3000 is in use
sudo lsof -i :3000

# Restart frontend
cd ~/TeamACIDic_project/frontend
pkill -f serve
serve -s build -l 3000
```

### Database Connection Issues
```bash
# Test MySQL connection
mysql -u hr_user -pabc123 employees -e "SHOW TABLES;"

# Check .env file
cat ~/TeamACIDic_project/.env
```

### Security Group Issues
If you can't access from browser:
1. Go to EC2 Console → Security Groups
2. Find your instance's security group
3. Add inbound rules for ports 8000 and 3000
4. Source: `0.0.0.0/0` (Anywhere)

---

## Updating Deployment

To pull latest changes from GitHub:

```bash
cd ~/TeamACIDic_project
git pull origin main

# Restart backend
pkill -f uvicorn
source .venv/bin/activate
pip install -r requirements.txt
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > backend.log 2>&1 &

# Rebuild and restart frontend
cd frontend
npm install
npm run build
pkill -f serve
nohup serve -s build -l 3000 > frontend.log 2>&1 &
```

---

## Production Best Practices (For Demo)

### 1. Keep Services Running
Use `screen` or `tmux` to keep processes running after SSH disconnect:

```bash
# Install screen
sudo apt-get install -y screen

# Start backend in screen
screen -S backend
cd ~/TeamACIDic_project
source .venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug
# Press Ctrl+A then D to detach

# Start frontend in screen
screen -S frontend
cd ~/TeamACIDic_project/frontend
serve -s build -l 3000
# Press Ctrl+A then D to detach

# List screens
screen -ls

# Reattach to a screen
screen -r backend
```

### 2. Monitor Resources
```bash
# Check disk space
df -h

# Check memory
free -h

# Check CPU
top
```

### 3. Backup Database
```bash
mysqldump -u hr_user -pabc123 employees > ~/backup_$(date +%Y%m%d).sql
```

---

## Important Notes

1. **Security:** The credentials in this guide are for DEMO purposes only. Change them for production.

2. **EC2 Instance:** Keep it running until after the demo. You can stop it (not terminate) after to save costs.

3. **Costs:** t2.medium costs ~$0.05/hour. Stop when not demoing.

4. **IP Address:** EC2 public IP changes if you stop/start. Use Elastic IP for permanent address.

5. **Logs:** Check backend.log and frontend.log if anything breaks.

---

## Demo Day Checklist

- [ ] EC2 instance is running
- [ ] Backend responding on port 8000
- [ ] Frontend accessible on port 3000
- [ ] Security group allows inbound on 8000, 3000
- [ ] Login feature working
- [ ] Change password feature working
- [ ] IP address shared with team lead
- [ ] Tested from external browser (not just localhost)
- [ ] Logs are clean (no critical errors)

---

## Emergency Contacts

If deployment fails or you need help:
1. Check logs: `~/TeamACIDic_project/backend.log`
2. Restart services using commands above
3. Contact team lead with error logs
4. AWS Console → CloudWatch for system metrics

Good luck with your demo! 🚀
