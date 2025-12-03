#!/bin/bash
set -e

# Activate environment
source /home/ubuntu/brep_env/bin/activate

# Go to data directory
cd /lambda/nfs/brepTrain

# Unzip data
echo "Unzipping data..."
# We assume the zip file was created with full paths or relative, but we'll try to handle it.
# If it was absolute paths, unzip might create Volumes/... 
# Let's just unzip and fix if needed.
unzip -q -o bin.zip

# Check if 'bin' directory exists, if not, it might be inside the full path structure
if [ ! -d "bin" ]; then
    # Try to find where bin went
    FOUND_BIN=$(find . -type d -name "bin" | head -n 1)
    if [ -n "$FOUND_BIN" ]; then
        echo "Found bin at $FOUND_BIN, moving contents..."
        mv "$FOUND_BIN" .
    fi
fi

# Ensure split files are in bin (as we did locally)
echo "Preparing split files..."
cp train.txt val.txt test.txt bin/

# Go to code directory
cd /home/ubuntu/BrepMFR

# Run training
echo "Starting training..."
# Using nohup to keep it running if session disconnects, and redirecting output
nohup python3 segmentation.py train \
    --dataset_path "/lambda/nfs/brepTrain/bin" \
    --max_epochs 1000 \
    --batch_size 64 \
    --num_workers 16 \
    --accelerator gpu \
    --devices 1 \
    > training.log 2>&1 &

echo "Training started. PID: $!"
echo "Logs are being written to /home/ubuntu/BrepMFR/training.log"
