FROM python:3.11-slim

# Install dependencies
RUN apt-get update && \
    apt-get install -y graphviz && \
    pip install diagrams && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy your topology file
COPY topology.py .

# Run topology script and generate PNG
CMD ["python", "topology.py"]
