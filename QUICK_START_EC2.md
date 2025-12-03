# EC2 Quick Start - 5 Minutes to Deploy

## Step 1: Launch EC2 Instance (2 minutes)
1. AWS Console → EC2 → Launch Instance
2. Choose: **Ubuntu Server 22.04 LTS**
3. Instance type: **t2.medium**
4. Create/Select key pair
5. **Security Group - Add these inbound rules:**
   - Port 22 (SSH) - Your IP
   - Port 8000 (Backend) - Anywhere (0.0.0.0/0)
   - Port 3000 (Frontend) - Anywhere (0.0.0.0/0)
6. Launch!

## Step 2: Connect to EC2 (30 seconds)
```bash
ssh -i "your-key.pem" ubuntu@<YOUR_EC2_IP>
```

## Step 3: Run Deployment Script (10 minutes)
```bash
# Copy paste this entire block
curl -O https://raw.githubusercontent.com/zachJX-SJSU/TeamACIDic_project/main/ec2_deploy.sh
chmod +x ec2_deploy.sh
./ec2_deploy.sh
```

**Wait for it to complete. It will show:**
```
========================================
Backend API: http://<YOUR_IP>:8000
Frontend: http://<YOUR_IP>:3000
API Docs: http://<YOUR_IP>:8000/docs
========================================
```

## Step 4: Message Your Team Lead

**Copy this template and fill in your IP:**

```
Hi Zach,

EC2 is running!

IP Address: <YOUR_EC2_IP>
Backend (Port 8000): http://<YOUR_EC2_IP>:8000
Frontend (Port 3000): http://<YOUR_EC2_IP>:3000
API Docs: http://<YOUR_EC2_IP>:8000/docs

Login and change password features are deployed and ready for testing.
```

---

## Getting Your EC2 IP

### From AWS Console:
EC2 → Instances → Select your instance → Copy "Public IPv4 address"

### From EC2 Terminal:
```bash
curl http://169.254.169.254/latest/meta-data/public-ipv4
```

---

## Quick Test

```bash
# Test backend
curl http://<YOUR_IP>:8000/

# Open frontend in browser
http://<YOUR_IP>:3000
```

---

## If Something Breaks

### Check if services are running:
```bash
ps aux | grep -E "uvicorn|serve"
```

### Check logs:
```bash
# Backend
tail -f ~/TeamACIDic_project/backend.log

# Frontend
tail -f ~/TeamACIDic_project/frontend/frontend.log
```

### Restart backend:
```bash
cd ~/TeamACIDic_project
source .venv/bin/activate
pkill -f uvicorn
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > backend.log 2>&1 &
```

### Restart frontend:
```bash
cd ~/TeamACIDic_project/frontend
pkill -f serve
nohup serve -s build -l 3000 > frontend.log 2>&1 &
```

---

## Pull Latest Code from GitHub

```bash
cd ~/TeamACIDic_project
git pull origin main

# Restart backend
pkill -f uvicorn
source .venv/bin/activate
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 --log-level debug > backend.log 2>&1 &

# Restart frontend
cd frontend
npm install
npm run build
pkill -f serve
nohup serve -s build -l 3000 > frontend.log 2>&1 &
```

---

## Important for Demo Day

1. **Keep EC2 Running:** Don't stop or terminate until after demo
2. **Test Before Demo:** Open frontend in browser, try logging in
3. **Have Backup:** Take a snapshot of your EC2 instance
4. **Monitor:** Check logs 30 minutes before demo
5. **Connection:** Make sure security group allows ports 8000 and 3000

---

## Cost Management

- **t2.medium:** ~$0.05/hour (~$1.20/day)
- **Stop (not terminate) after demo** to save costs
- **Warning:** Stopping changes public IP (use Elastic IP if needed)

---

That's it! Your app should be live in ~15 minutes total. 🚀
