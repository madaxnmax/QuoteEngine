#!/bin/bash
set -e

# Install system dependencies
echo "Installing system dependencies..."
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv unzip

# Create venv
echo "Creating virtual environment..."
python3 -m venv brep_env
source brep_env/bin/activate

# Install PyTorch (CUDA 12.1)
echo "Installing PyTorch..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

# Install DGL (CUDA 12.1)
echo "Installing DGL..."
pip install dgl -f https://data.dgl.ai/wheels/cu121/repo.html

# Install other dependencies
echo "Installing other dependencies..."
pip install pytorch-lightning==1.7.1 torchmetrics==0.9.3 fairseq torch-geometric numpy==1.23.5

# Unzip code
echo "Unzipping code..."
unzip -o brep_code.zip -d BrepMFR

echo "Setup complete."
