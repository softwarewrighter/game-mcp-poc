#!/bin/bash
set -e

echo "Starting production server..."

# Check if build exists
if [ ! -f "./target/release/backend" ]; then
    echo "Backend not built. Running build script..."
    ./scripts/build.sh
fi

if [ ! -d "./frontend/dist" ]; then
    echo "Frontend not built. Running build script..."
    ./scripts/build.sh
fi

# Start the backend server (it will serve the frontend static files)
echo "Starting server..."
./target/release/backend
