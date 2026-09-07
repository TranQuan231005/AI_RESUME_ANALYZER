FROM python:3.11-slim

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CLASSIFIER_ARTIFACT_DIR=/app/models/classifier \
    MATCHING_CONFIG_PATH=/app/models/matching/metadata.json \
    EMBEDDING_MODEL_PATH=/opt/models/all-MiniLM-L6-v2

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Resolve the immutable embedding revision while building; runtime stays offline.
RUN python -c "from sentence_transformers import SentenceTransformer; m=SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2', revision='f5610b47471b118dafc55f4c387822dbfc8413ae', device='cpu'); m.save('/opt/models/all-MiniLM-L6-v2')" \
    && python -c "import joblib; joblib.load('/app/models/classifier/classifier_pipeline.joblib')" \
    && python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('/opt/models/all-MiniLM-L6-v2', device='cpu', local_files_only=True)"

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
