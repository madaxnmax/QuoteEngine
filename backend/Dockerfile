FROM continuumio/miniconda3

WORKDIR /app

# Install system dependencies required for pythonocc/GL
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglu1-mesa \
    libx11-6 \
    libxi6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY environment.yml .

# Create Conda environment
RUN conda env create -f environment.yml

# Make RUN commands use the new environment
SHELL ["conda", "run", "-n", "brep_mfr", "/bin/bash", "-c"]

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["conda", "run", "--no-capture-output", "-n", "brep_mfr", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
