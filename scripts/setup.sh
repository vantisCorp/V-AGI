#!/bin/bash

# OMNI-AI Setup Script

set -e

echo "=========================================="
echo "OMNI-AI Setup Script"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo ""
echo "Creating necessary directories..."
mkdir -p logs
mkdir -p data/knowledge_graph
mkdir -p data/vector_store
mkdir -p data/simulations
mkdir -p data/cad

# Copy environment file if it doesn't exist
echo ""
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "Please edit .env with your configuration"
else
    echo ".env file already exists"
fi

# Initialize Git repository if not exists
echo ""
if [ ! -d .git ]; then
    echo "Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: OMNI-AI project setup"
else
    echo "Git repository already exists"
fi

echo ""
echo "=========================================="
echo "Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Start services: docker-compose up -d"
echo "3. Run the application: python src/main.py"
echo ""