#!/bin/bash
# Exit immediately if any command fails
set -e

echo "🚀 Running initial data ingestion..."
# Run your shared script
python src/ingest.py

echo "✅ Ingestion complete!"
# This magic line hands control back to your Dockerfile's CMD
exec "$@"