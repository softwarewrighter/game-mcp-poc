#!/bin/bash
set -e

echo "Building project for serving..."
./scripts/build.sh

echo "Starting server on port 1461..."
export PORT=1461
cargo run --package backend --bin backend
