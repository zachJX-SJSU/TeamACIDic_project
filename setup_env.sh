#!/usr/bin/env bash
set -euo pipefail

# ================================
# Basic system update & utilities
# ================================
sudo apt-get update -y
sudo apt-get upgrade -y

echo "Installing Basic system update & utilities..."
# Core tools for dev & deployment
sudo apt-get install -y \
    git \                # version control
    curl \               # handy for API testing / downloads
    wget \               # same as above
    unzip \              # for handling zip files
    build-essential \    # compilers, in case any pip packages need it
    pkg-config

# ================================
# Python & DB-related tools
# ================================
echo "Installing Python & DB-related tools..."
sudo apt-get install -y \
    python3 \
    python3-venv \
    python3-pip \
    sqlite3              # for local dev DB

# Optional: MySQL client (to poke production DBs / RDS from EC2)
sudo apt-get install -y \
    default-mysql-client

# ================================
# Reverse proxy/web server
# ================================
# Serve FastAPI via Nginx + uvicorn/gunicorn in production
echo "Installing proxy/web server..."

sudo apt-get install -y nginx

# ================================
# Project setup (backend)
# ================================
# Adjust this path to wherever you want your backend code to live
echo "Setting up project workspace proxy/web server..."
PROJECT_DIR="$(pwd)"
echo "PROJECT_DIR = $PROJECT_DIR"
# # If the directory doesn't exist yet, create it (or git clone into it later)
# sudo mkdir -p "$PROJECT_DIR"
# sudo chown "$USER":"$USER" "$PROJECT_DIR"

cd $PROJECT_DIR

# If you haven't cloned your repo yet, do something like:
# git clone git@github.com:zachJX-SJSU/TeamACIDic_project.git "$PROJECT_DIR"

# ================================
# Python virtual environment
# ================================
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip & basic tooling inside the venv
pip install --upgrade pip setuptools wheel

# ================================
# Install Python dependencies
# ================================
echo "Installing Python dependencies from requirements.txt..."
if [[ ! -f "requirements.txt" ]]; then
  echo "requirements.txt not found in $PROJECT_DIR"
  echo "Make sure your FastAPI project (with requirements.txt) is in this directory, then run 'pip install -r requirements.txt'"
  exit 1
fi

pip install -r requirements.txt

echo "========================================="
echo "Environment setup complete."
echo "Activate your venv with:  source $PROJECT_DIR/.venv/bin/activate"
echo "Run the app with:         uvicorn app.main:app --host 0.0.0.0 --port 8000"
echo "========================================="
