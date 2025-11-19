#!/bin/bash
# Simple test script to verify MCP server responds to JSON-RPC commands
#
# This sends a sequence of JSON-RPC requests to the MCP server and shows the responses

set -e

DB_PATH="${GAME_DB_PATH:-:memory:}"

echo "Testing MCP server with JSON-RPC commands..."
echo "Database: $DB_PATH"
echo ""

# Check if binary exists
if [ ! -f "./target/release/game-mcp-server" ]; then
    echo "Error: MCP server binary not found. Please run ./scripts/build.sh first."
    exit 1
fi

# Create test input
cat <<EOF | GAME_DB_PATH="$DB_PATH" ./target/release/game-mcp-server
{"jsonrpc":"2.0","id":1,"method":"view_game_state","params":{}}
{"jsonrpc":"2.0","id":2,"method":"get_turn","params":{}}
{"jsonrpc":"2.0","id":3,"method":"make_move","params":{"row":0,"col":0}}
{"jsonrpc":"2.0","id":4,"method":"get_turn","params":{}}
{"jsonrpc":"2.0","id":5,"method":"view_game_state","params":{}}
EOF

echo ""
echo "Test complete!"
