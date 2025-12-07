# Jenkins CI/CD Pipeline on AWS EC2

This guide shows how to set up Jenkins on an AWS EC2 instance to run your automated unit tests.

## Prerequisites

- AWS Account
- EC2 instance (Ubuntu 22.04 LTS recommended)
- SSH access to the instance
- GitHub repository with Jenkinsfile

## Step 1: Launch EC2 Instance

### In AWS Console:

1. Go to **EC2 Dashboard**
2. Click **Launch Instances**
3. **Choose AMI:** Ubuntu Server 22.04 LTS (Free tier eligible)
4. **Instance Type:** t2.micro or t3.micro (free tier)
5. **Key Pair:** Create new or select existing
6. **Security Group:** Allow inbound:
   - SSH (22) from your IP
   - HTTP (80) from anywhere
   - HTTPS (443) from anywhere
   - Custom TCP 8080 (Jenkins default port)
7. **Storage:** 20 GB (default)
8. **Launch**

### Get Instance Details:

```bash
# After instance is running, note:
# - Public IP: xxx.xxx.xxx.xxx
# - Instance ID: i-xxxxx
# - Key pair file: your-key.pem
```

## Step 2: SSH into EC2 Instance

```bash
# Change permissions on key (macOS/Linux)
chmod 400 your-key.pem

# SSH into instance
ssh -i your-key.pem ubuntu@<PUBLIC_IP>

# Or on Windows, use PuTTY or:
# ssh -i C:\path\to\your-key.pem ubuntu@<PUBLIC_IP>
```

## Step 3: Install Java (Required for Jenkins)

```bash
# Update system packages
sudo apt update
sudo apt upgrade -y

# Install Java 17 (LTS)
sudo apt install -y openjdk-17-jdk

# Verify installation
java -version
```

## Step 4: Install Jenkins

```bash
# Add Jenkins repository key
curl -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io.key | sudo tee /usr/share/keyrings/jenkins-keyring.asc > /dev/null

# Add Jenkins repository
echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https://pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/null

# Update and install Jenkins
sudo apt-get update
sudo apt-get install -y jenkins

# Start Jenkins
sudo systemctl start jenkins
sudo systemctl enable jenkins  # Auto-start on reboot

# Check status
sudo systemctl status jenkins
```

## Step 5: Install Python and Dependencies

```bash
# Install Python 3.9+
sudo apt install -y python3 python3-venv python3-pip python3-dev

# Verify
python3 --version
pip3 --version
```

## Step 6: Install Git

```bash
sudo apt install -y git

# Verify
git --version
```

## Step 7: Configure Jenkins

### Access Jenkins Web UI:

```
http://<PUBLIC_IP>:8080
```

### Get Initial Admin Password:

```bash
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
```

### Setup Wizard:

1. Paste the admin password from above
2. Click **Install suggested plugins** (wait 5 minutes)
3. **Create First Admin User:**
   - Username: `admin`
   - Password: Choose strong password
   - Full Name: Your name
   - Email: your@email.com
4. **Instance Configuration:** Use default `http://YOUR_EC2_IP:8080`
5. **Start using Jenkins**

## Step 8: Create Pipeline Job

### In Jenkins Web UI:

1. Click **New Item**
2. Name: `TeamACIDic_project`
3. Type: **Pipeline** (not Multibranch)
4. Click **Create**

### Configure:

**Pipeline Section:**
- **Definition:** Pipeline script from SCM
- **SCM:** Git
- **Repository URL:** `https://github.com/zachJX-SJSU/TeamACIDic_project.git`
- **Credentials:** None (public repo)
- **Branch Specifier:** `*/archana_jenkins`
- **Script Path:** `Jenkinsfile`

Click **Save**

## Step 9: Create SSH Key for GitHub (Optional but Recommended)

For private repos or to avoid rate limiting:

```bash
# Generate SSH key on EC2
ssh-keygen -t ed25519 -C "jenkins@ec2"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# Settings → SSH and GPG keys → New SSH key
# Paste the public key

# Test connection
ssh -T git@github.com
```

## Step 10: Build & Monitor

### Trigger First Build:

1. Go to Jenkins job page
2. Click **Build Now**
3. Watch **Console Output** in real-time

### Expected Output:

```
✅ Checkout from GitHub
✅ Create Python venv
✅ Install requirements
✅ Run pytest (23 passed)
✅ Publish JUnit results
```

### View Results:

- **Test Results** tab → JUnit report
- **Artifacts** tab → coverage.xml, junit.xml
- **Console Output** → Full build logs

## Helpful Jenkins Commands

```bash
# Stop Jenkins
sudo systemctl stop jenkins

# Start Jenkins
sudo systemctl start jenkins

# Restart Jenkins
sudo systemctl restart jenkins

# View logs
sudo tail -f /var/log/jenkins/jenkins.log

# Jenkins config files
sudo ls -la /var/lib/jenkins/

# Job workspace (where code runs)
ls /var/lib/jenkins/workspace/TeamACIDic_project/
```

## Security Best Practices

1. **Restrict SSH Access:**
   ```bash
   # Security Group: Allow SSH only from your IP
   # Example: 203.0.113.0/32 (your office/home IP)
   ```

2. **Use IAM Roles (optional):**
   - Attach IAM role to EC2 for AWS API access
   - Avoids storing AWS credentials on instance

3. **Enable Firewall:**
   ```bash
   sudo apt install -y ufw
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 8080/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

4. **Backup Jenkins Config:**
   ```bash
   sudo tar -czf jenkins-backup.tar.gz /var/lib/jenkins/
   ```

## Troubleshooting

### Jenkins Page Not Loading:

```bash
# Check if Jenkins is running
sudo systemctl status jenkins

# Check port 8080
sudo lsof -i :8080

# Restart Jenkins
sudo systemctl restart jenkins

# Wait 30 seconds and refresh browser
```

### Build Fails with Python Error:

```bash
# Check Python is installed on EC2
python3 --version

# Check git is installed
git --version

# Install missing packages
sudo apt install -y python3-venv python3-pip
```

### GitHub Connection Issues:

```bash
# Test GitHub connection
ssh -T git@github.com

# Check if git clone works
cd /tmp && git clone https://github.com/zachJX-SJSU/TeamACIDic_project.git
```

### Jenkins Plugins Missing:

1. Go to **Manage Jenkins** → **Manage Plugins**
2. Install:
   - Pipeline
   - Git plugin
   - JUnit plugin

## Cost Estimation

| Item | Cost (USD/month) |
|------|-----------------|
| t2.micro (1 GB RAM) | ~$8 (Free tier eligible) |
| t3.micro (1 GB RAM) | ~$7 |
| m5.large (8 GB RAM) | ~$70 |
| Data transfer | ~$1 |
| **Total (t2.micro)** | **~$9/month** |

Free tier covers first 12 months of t2.micro.

## Optional: Use Docker on EC2

For reproducible Jenkins builds:

```bash
# Install Docker
sudo apt install -y docker.io

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu
sudo usermod -aG docker jenkins

# Restart jenkins
sudo systemctl restart jenkins

# Run tests in Docker container (more isolated)
```

## Next Steps

1. ✅ Launch EC2 instance
2. ✅ Install Java, Jenkins, Python
3. ✅ Create Pipeline job
4. ✅ Build #1 should pass
5. ✅ View test results in Jenkins UI
6. ✅ Submit EC2 Jenkins URL to Canvas

## Useful Links

- **Jenkins Docs:** https://www.jenkins.io/doc/
- **AWS EC2:** https://aws.amazon.com/ec2/
- **Jenkins on EC2:** https://www.jenkins.io/doc/tutorials/tutorial-for-installing-jenkins-on-AWS/

## Example Jenkins Job URL (after setup)

```
http://<YOUR_EC2_IP>:8080/job/TeamACIDic_project/
```

Share this URL in Canvas as proof of working CI/CD!
