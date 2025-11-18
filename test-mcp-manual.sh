#!/bin/bash
# Manual testing script for MCP server
# This demonstrates how to interact with the MCP server using CLI tools

SERVER="./target/release/game-mcp-server"
DB_PATH="/tmp/manual-test-$(date +%s).db"

echo "=== MCP Server Manual Testing ==="
echo "Database: $DB_PATH"
echo ""

export GAME_DB_PATH="$DB_PATH"

# Test 1: View game state
echo "Test 1: View game state"
echo '{"jsonrpc":"2.0","id":1,"method":"view_game_state","params":{}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 2: Get turn
echo "Test 2: Get current turn"
echo '{"jsonrpc":"2.0","id":2,"method":"get_turn","params":{}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 3: Make a move
echo "Test 3: Make move at (1,1)"
echo '{"jsonrpc":"2.0","id":3,"method":"make_move","params":{"row":1,"col":1}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 4: Send a taunt
echo "Test 4: Send taunt"
echo '{"jsonrpc":"2.0","id":4,"method":"taunt_player","params":{"message":"Nice try!"}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 5: Get game history
echo "Test 5: Get game history"
echo '{"jsonrpc":"2.0","id":5,"method":"get_game_history","params":{}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 6: Invalid method (error test)
echo "Test 6: Invalid method (should return error)"
echo '{"jsonrpc":"2.0","id":6,"method":"invalid_method","params":{}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Test 7: Invalid params (error test)
echo "Test 7: Invalid params (should return error)"
echo '{"jsonrpc":"2.0","id":7,"method":"make_move","params":{}}' | \
  timeout 2 $SERVER 2>/dev/null | \
  python3 -m json.tool
echo ""

# Cleanup
rm -f "$DB_PATH" "${DB_PATH}-shm" "${DB_PATH}-wal"

echo "=== Manual testing complete ==="
