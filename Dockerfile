# Production Build for Development Intelligence Platform
FROM python:3.11-slim
WORKDIR /app

# System dependencies for FAISS
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Copy data and docs
COPY data/ ./data/
COPY docs/ ./docs/

# Copy locally built static assets
# Ensure 'npm run build' was run locally before 'railway up'
COPY backend/static/ ./backend/static/

# Environment setup
ENV PYTHONPATH=/app/backend
ENV HOST=0.0.0.0
ENV PORT=3000

# Expose port
EXPOSE 3000

# Start FastAPI server
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-3000}"]
