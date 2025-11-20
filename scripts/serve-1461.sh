#!/bin/bash
set -e

echo "Starting server on port 1461..."

# Set the port for the backend server
export PORT=1461

# Run the backend server
cargo run --package backend --bin backend
