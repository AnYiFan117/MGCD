#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "Step 1: Running main.py to generate code vectors..."
PYTHONPATH=. python3 src/main.py
echo "Step 1 finished."
echo ""

echo "Step 2: Running faiss_init.py to generate the database and initial clone results..."
PYTHONPATH=. python3 src/faiss_init.py
echo "Step 2 finished."
echo ""

echo "Step 3: Running file_similarity.py to calculate file-level similarity..."
PYTHONPATH=. python3 src/file_similarity.py
echo "Step 3 finished."
echo ""

echo "Step 4: Running block_similarity.py to parepare data"
PYTHONPATH=. python3 src/block_similarity.py
echo "Step 4 finished."
echo ""

echo "Step 5: Running deepseek.py to refine block-level results..."
PYTHONPATH=. python3 src/deepseek.py
echo "Step 5 finished."
echo ""

echo "All steps completed successfully."
